"""Page extraction and cleaning for the prototype documents (pypdf only).

For each selected page this module:
  1. removes page furniture (GAO footers, browser print headers, DOT&E running heads)
     and records the printed page number when it can be read reliably;
  2. tags GAO Highlights content as section_type="highlights" when the Highlights
     marker is present (nothing else is tagged; section types are never guessed);
  3. drops text that pypdf extracts badly, and logs every drop:
       - "Table N:" / "Figure N:" blocks in original-layout GAO reports
         (caption through the "Source:" line),
       - numeric-heavy lines (scrambled table cells),
       - runs of short label lines (figure/table residue),
       - tiny word fragments left behind where text overlaps a sidebar,
       - lone footnote markers;
  4. applies the retrieval-hygiene rules in ``ppm_agent.ingestion.hygiene`` (GAO back matter,
     accessible-text front matter / contents / table cells, DoD letter furniture, administrative
     sentences) and drops the DOT&E "major contractor" address line;
  5. rebuilds paragraphs from the remaining wrapped lines.

Every hygiene removal is kept in ExtractedPage.removed (rule + text) for the preprocessing log.
Pages with no usable text (image-only), with too many fragments, or with only
administrative content are skipped and reported.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from pypdf import PdfReader

from ppm_agent.ingestion.corpus_selection import PrototypeDocument
from ppm_agent.ingestion.hygiene import HygieneTracker, strip_admin_sentences

logging.getLogger("pypdf").setLevel(logging.ERROR)

MIN_PAGE_CHARS = 100          # less usable text than this = image-only / empty page
MIN_PAGE_CHARS_AFTER_HYGIENE = 50  # pages that lost administrative lines keep short genuine text (e.g. a figure note)
MAX_FRAGMENT_RATIO = 0.20     # more fragment lines than this = page too garbled to index
FRAGMENT_WARNING_COUNT = 5    # this many fragments = warn about truncated line ends
SHORT_LINE_CHARS = 30
SHORT_RUN_MIN = 3

# pypdf renders the bullet glyph of the original-layout GAO reports as the control character U+0081.
BULLETS = ("\u2022", "\x81", "- ", "\u2013 ")
SENTENCE_END = (".", "?", "!", ".”", ".\"", "”", ";")

GAO_FOOTER = re.compile(r"^\s*Page\s+([ivxlc]+|\d+)\s+GAO-\d{2}-\d+\b", re.IGNORECASE)
BROWSER_HEADER = re.compile(r"^\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2} [AP]M ")
BROWSER_FOOTER = re.compile(r"^https?://\S+\s+\d+/\d+\s*$")
DOTE_RUNNING_HEAD = re.compile(r"^(dod\s+programs|F-35 JSF\s+(\d+)|(\d+)\s+F-35 JSF|F-35 Joint Strike Fighter \(JSF\))\s*$", re.IGNORECASE)
END_MARKER = re.compile(r"^\[End of (section|table|figure|letter)\]\s*$", re.IGNORECASE)
CAPTION = re.compile(r"^(Table|Figure) \d+:")
SOURCE_LINE = re.compile(r"^Source:")
FOOTNOTE_MARKER = re.compile(r"^\s*(\d{1,3}|[a-c])\s*$")
TOC_LINE = re.compile(r"\S\s+\d{1,3}\s*$")
# DOT&E chapters use these small-caps headings; they become paragraph boundaries.
# They are not used as section_type because the two-column layout makes their scope unreliable.
DOTE_HEADINGS = {"executive summary", "system", "mission", "major contractor", "major contractors", "activity",
                 "assessment", "recommendations"}
DOTE_CONTRACTOR_MAX_LINES = 6  # the contractor names/locations under "major contractor(s)" (no sentence)
# Later DOT&E chapters (e.g. FY2024) print running heads such as "Article 47", "44 F-35" or "45F-35 45".
DOTE_FURNITURE = re.compile(r"^(?:article|f-35|\d{1,3})(?:\s*(?:article|f-35|\d{1,3}))*$", re.IGNORECASE)
# Function words that mark wrapped prose (as opposed to figure/table labels) in a run of short lines.
PROSE_WORDS = {"the", "of", "and", "to", "in", "a", "an", "is", "are", "was", "were", "for", "that", "with", "on", "as",
               "by", "be", "it", "its", "this", "from", "at", "or", "not", "has", "have", "had", "will", "which", "but", "than"}
PROSE_MIN_WORDS = 8
PROSE_MIN_FUNCTION_SHARE = 0.15


@dataclass
class ExtractedPage:
    document_id: str
    pdf_page: int
    printed_page: str | None
    paragraphs: list[dict] = field(default_factory=list)  # {"text", "section_type"}
    skipped_reason: str | None = None
    extraction_quality: str = "clean"  # clean | degraded_truncated_words
    dropped: dict = field(default_factory=dict)  # reason -> count
    warnings: list[str] = field(default_factory=list)
    removed: list[dict] = field(default_factory=list)  # hygiene removals: {"rule", "text"}

    @property
    def char_count(self) -> int:
        return sum(len(p["text"]) for p in self.paragraphs)


# --- line-level helpers -----------------------------------------------------------


def is_fragment(line: str) -> bool:
    """A few characters of a word split off by a sidebar, e.g. 'ts', 'ilities,'."""
    s = line.strip()
    return 0 < len(s) <= 12 and not s[0].isupper() and not s[0].isdigit() and not s.endswith((".", "?", "!", ":"))


def is_numeric_heavy(line: str) -> bool:
    tokens = line.split()
    return len(tokens) >= 3 and sum(any(c.isdigit() for c in t) for t in tokens) / len(tokens) >= 0.5


def is_repetitive(line: str) -> bool:
    """Column-header residue such as 'Flights Points Flights Points Flights Points'."""
    tokens = line.split()
    return len(tokens) >= 6 and len(set(tokens)) / len(tokens) < 0.4


def is_heading_run(lines: list[str]) -> bool:
    """A wrapped side heading such as 'Software Development and / Other Technical Risks'.

    Headings are mostly lower-case letters; figure/table labels such as
    'ALL VARIANTS / FLIgHT SCIeNCeS' are mostly capitals and are rejected.
    """
    joined = " ".join(l.strip() for l in lines)
    letters = [c for c in joined if c.isalpha()]
    upper_share = sum(c.isupper() for c in letters) / max(len(letters), 1)
    return (
        len(joined) <= 150
        and all(l.strip()[:1].isupper() for l in lines)
        and upper_share < 0.5
        and not any(c.isdigit() for c in joined)
        and not any(l.strip().startswith(BULLETS) for l in lines)
    )


def is_prose_run(lines: list[str]) -> bool:
    """Wrapped prose from a narrow column: enough words and a normal share of function words.

    Figure and table labels ('Development / Low-rate initial production / ...') have almost none.
    """
    words = re.findall(r"[A-Za-z][A-Za-z'’-]*", " ".join(lines))
    return len(words) >= PROSE_MIN_WORDS and sum(w.lower() in PROSE_WORDS for w in words) / len(words) >= PROSE_MIN_FUNCTION_SHARE


def dote_heading_key(line: str) -> str:
    """Normalize a DOT&E section heading: '» MAJOR CONTRACTORS:' -> 'major contractors'."""
    return re.sub(r"\s+", " ", line.replace("»", "").replace(":", "")).strip().lower()


def is_bullet(line: str) -> bool:
    return line.strip().startswith(BULLETS)


def normalize_line(line: str) -> str:
    line = line.replace("\x81", "\u2022")
    return re.sub(r"[ \t]+", " ", line).strip()


# --- main extraction ----------------------------------------------------------------


class HighlightsTracker:
    """Tracks whether we are inside a GAO Highlights section across pages."""

    def __init__(self, layout: str):
        self.layout = layout
        self.inside = False

    def page_is_highlights(self, lines: list[str]) -> bool:
        # Original-layout GAO reports print Highlights as a single page that names itself.
        return self.layout == "gao_original" and any(re.match(r"^\s*Highlights of GAO-\d{2}-\d+", l) for l in lines)


def extract_document(doc: PrototypeDocument) -> list[ExtractedPage]:
    """Extract and clean every eligible page of one prototype document."""
    reader = PdfReader(doc.path)
    tracker = HighlightsTracker(doc.layout)
    hygiene = HygieneTracker(doc.layout)
    pages = []
    for pdf_page in range(1, len(reader.pages) + 1):
        if not doc.includes_page(pdf_page):
            continue
        raw = reader.pages[pdf_page - 1].extract_text() or ""
        pages.append(clean_page(raw, pdf_page, doc, tracker, hygiene))
    return pages


def clean_page(
    raw: str,
    pdf_page: int,
    doc: PrototypeDocument,
    tracker: HighlightsTracker,
    hygiene: HygieneTracker | None = None,
) -> ExtractedPage:
    page = ExtractedPage(document_id=doc.document_id, pdf_page=pdf_page, printed_page=None)
    dropped: dict[str, int] = {}
    hygiene = hygiene or HygieneTracker(doc.layout)

    def drop(reason: str, n: int = 1):
        dropped[reason] = dropped.get(reason, 0) + n

    def remove(rule: str, text: str):
        """Hygiene removal: counted, and its text kept for the preprocessing log."""
        drop(rule)
        if page.removed and page.removed[-1]["rule"] == rule:
            page.removed[-1]["text"] += "\n" + text  # merge consecutive lines removed by the same rule
        else:
            page.removed.append({"rule": rule, "text": text})

    raw_lines = raw.split("\n")
    page_highlights = tracker.page_is_highlights(raw_lines)

    # 1. page furniture, printed page, section markers -> list of (line or None=boundary, section_type)
    items: list[tuple[str | None, str | None]] = []
    dote_head_page = None
    contractor_lines = 0
    pending_major = False  # "» MAJOR" printed on one line and "CONTRACTORS:" on the next
    for line in raw_lines:
        s = line.strip()
        if not s:
            items.append((None, None))
            continue
        m = GAO_FOOTER.match(s)
        if m:
            page.printed_page = m.group(1) if doc.printed_page_method == "footer" else page.printed_page
            continue
        if BROWSER_HEADER.match(s) or BROWSER_FOOTER.match(s):
            continue
        if doc.layout == "dote_annual_report":
            m = DOTE_RUNNING_HEAD.match(s)
            if m:
                dote_head_page = m.group(2) or m.group(3) or dote_head_page
                continue
            if DOTE_FURNITURE.match(s):
                continue  # running head / page number of later DOT&E chapter formats
            key = dote_heading_key(s)
            if pending_major and key == "contractors":
                key = "major contractors"
            pending_major = key == "major"
            if key in DOTE_HEADINGS or pending_major:
                contractor_lines = DOTE_CONTRACTOR_MAX_LINES if key.startswith("major contractor") else 0
                items.append((None, None))
                continue
            if contractor_lines and not s.endswith("."):
                contractor_lines -= 1
                remove("dote_contractor_line", s)
                continue
            contractor_lines = 0
        if doc.layout.startswith("gao") and s in ("Joint Strike Fighter", "Joint Strike Fighter Acquisition"):
            continue  # running footer title
        rule = hygiene.check(s, pdf_page)
        if rule:
            remove(rule, s)
            continue
        if doc.layout == "gao_accessible_text" and s.startswith("GAO Highlights:"):
            tracker.inside = True
        if END_MARKER.match(s):
            if s.lower().startswith("[end of section"):
                tracker.inside = False
            items.append((None, None))
            continue
        if page_highlights or tracker.inside:
            section = "highlights"
        elif hygiene.in_comments:
            section = "agency_comments"
        else:
            section = None
        items.append((s, section))

    page.warnings.extend(hygiene.warnings)
    hygiene.warnings.clear()
    if page.removed and not any(s for s, _ in items):
        page.skipped_reason = "administrative content only (" + ", ".join(sorted({r["rule"] for r in page.removed})) + ")"
        page.dropped = dropped
        return page

    # printed page
    if doc.printed_page_method == "manual_map":
        page.printed_page = doc.printed_page_map.get(pdf_page)
        if dote_head_page and page.printed_page and dote_head_page != page.printed_page:
            page.warnings.append(f"running head shows page {dote_head_page}, manual map says {page.printed_page}")

    # table-of-contents / list pages (many lines ending in a page number)
    content = [s for s, _ in items if s]
    if content and sum(bool(TOC_LINE.search(s)) for s in content) / len(content) >= 0.4 and doc.layout == "gao_original":
        page.skipped_reason = "table of contents / list of tables (lines end in page numbers)"
        page.dropped = {"toc_page_lines": len(content)}
        return page

    # 2. caption-to-Source blocks in original-layout GAO reports
    if doc.layout == "gao_original":
        i = 0
        while i < len(items):
            s, _ = items[i]
            if s and CAPTION.match(s) and not TOC_LINE.search(s):
                end = next((j for j in range(i + 1, min(i + 80, len(items))) if items[j][0] and SOURCE_LINE.match(items[j][0])), None)
                if end is not None:
                    n = sum(1 for k in range(i, end + 1) if items[k][0])
                    drop(f"{'table' if s.startswith('Table') else 'figure'}_block", n)
                    page.warnings.append(f"omitted {s[:70]!r} ({n} lines; pypdf table/figure text unreliable)")
                    items[i : end + 1] = [(None, None)]
            i += 1

    # 3. line filters
    kept: list[tuple[str | None, str | None]] = []
    for s, section in items:
        if s is None:
            kept.append((None, None))
        elif FOOTNOTE_MARKER.match(s):
            drop("footnote_marker")  # superscript reference; neighbours are re-joined
        elif is_numeric_heavy(s):
            drop("numeric_table_line")
        elif is_repetitive(s):
            drop("repetitive_header_line")
        elif is_fragment(s):
            drop("word_fragment")
        else:
            kept.append((s, section))

    # 4. runs of short label lines: keep wrapped headings, drop figure/table residue
    final: list[tuple[str | None, str | None, bool]] = []  # (line, section, is_heading)
    i = 0
    while i < len(kept):
        s, section = kept[i]
        if s is None:
            final.append((None, None, False))
            i += 1
            continue
        j = i
        while j < len(kept) and kept[j][0] and len(kept[j][0]) <= SHORT_LINE_CHARS and not kept[j][0].endswith(SENTENCE_END):
            j += 1
        if j - i >= SHORT_RUN_MIN:
            run = [kept[k][0] for k in range(i, j)]
            if is_heading_run(run):
                final.append((None, None, False))
                final.append((" ".join(run), section, True))
                final.append((None, None, False))
            elif doc.layout == "dote_annual_report" and is_prose_run(run):
                # DOT&E chapters set body text in narrow columns: these short lines are wrapped prose
                final.extend((kept[k][0], kept[k][1], False) for k in range(i, j))
            else:
                drop("short_label_run", j - i)
            i = j
        else:
            final.append((s, section, False))
            i += 1

    # 5. quality gate
    content_lines = sum(1 for s, _ in items if s)
    fragments = dropped.get("word_fragment", 0)
    # (pages with only a few lines are image-only pages; they fall through to the no-usable-text check)
    if content_lines >= 10 and fragments / content_lines > MAX_FRAGMENT_RATIO:
        page.skipped_reason = f"garbled: {fragments}/{content_lines} lines are word fragments (text overlaps sidebar)"
        page.dropped = dropped
        return page
    if fragments >= FRAGMENT_WARNING_COUNT:
        page.extraction_quality = "degraded_truncated_words"
        page.warnings.append(f"{fragments} word fragments removed; some line-end words may be truncated")

    # 6. paragraphs, then administrative sentences (contact details, distribution notices)
    page.paragraphs = []
    for para in build_paragraphs(final):
        text, removed = strip_admin_sentences(para["text"])
        for sentence in removed:
            remove("admin_sentence", sentence)
        if text:
            page.paragraphs.append({**para, "text": text})
    page.dropped = dropped
    if page.char_count < (MIN_PAGE_CHARS_AFTER_HYGIENE if page.removed else MIN_PAGE_CHARS):
        page.skipped_reason = f"no usable text ({page.char_count} chars after cleaning; image-only or empty)"
        page.paragraphs = []
    return page


def build_paragraphs(lines: list[tuple[str | None, str | None, bool]]) -> list[dict]:
    """Join wrapped lines into paragraphs.

    A new paragraph starts at a blank line, a heading, a bullet, a change of
    section_type, or after a short line that ends a sentence (the usual last line
    of a paragraph in wrapped PDF text).
    """
    widths = sorted(len(s) for s, _, _ in lines if s)
    width = widths[int(len(widths) * 0.8)] if widths else 80

    paragraphs: list[dict] = []
    current: list[str] = []
    current_section = None

    def flush():
        nonlocal current
        if current:
            text = ""
            for part in current:
                if text.endswith("-") and part[:1].islower():
                    text += part  # re-join a word or compound broken at a line end
                else:
                    text = f"{text} {part}" if text else part
            paragraphs.append({"text": text.strip(), "section_type": current_section})
        current = []

    prev = None
    for s, section, heading in lines:
        if s is None:
            flush()
            prev = None
            continue
        s = normalize_line(s)
        starts_new = (
            heading
            or is_bullet(s)
            or section != current_section
            or (prev is not None and prev.endswith(SENTENCE_END) and len(prev) < 0.8 * width)
            or (prev is not None and prev.endswith(":") and len(prev) < 0.8 * width)
        )
        if starts_new:
            flush()
        current_section = section
        current.append(s)
        prev = s
        if heading:
            flush()
            prev = None
    flush()
    return [p for p in paragraphs if p["text"]]
