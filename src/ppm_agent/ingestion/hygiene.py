"""Retrieval-hygiene rules: remove administrative text that is never program evidence.

Deterministic text-quality rules only. Nothing here looks at similarity scores,
at how often a passage is retrieved, or at any evaluation question. Every removal
is reported with its rule name so it can be logged and traced.

Rules (all GAO layouts unless noted):
  back_matter              "GAO Contact and Staff Acknowledgments", "Related GAO Products" and the
                           GAO back cover ("GAO's Mission", ordering information). A section ends at
                           "[End of section]", "Footnotes:" or the next appendix, so endnotes are kept.
  front_matter             accessible-text preamble and cover lines before "GAO Highlights:" (page 1 only).
  contents                 accessible-text "Contents:" section (list of headings, tables and abbreviations),
                           ending at "[End of section]" or the letter's "Washington, DC 20548:" address line;
                           capped at CONTENTS_MAX_LINES with a page warning.
  agency_letter_furniture  inside "Appendix N: Comments from the Department of Defense": address block,
                           salutation, signature block, "[End of letter]" and the restated report title.
                           The department's substantive responses are kept and tagged agency_comments.
  table_cell_fragment      accessible-text tables/figures (caption to "[End of table|figure]"): short
                           standalone label/value cells such as "Aircraft: BF3;". Prose cells are kept.
  table_furniture          "[Refer to PDF for image: ...]" and "Source: ..." lines inside those blocks.
  admin_sentence           (any layout) contact details, distribution and copyright notices.
"""

from __future__ import annotations

import re

APPENDIX = re.compile(r"^Appendix [IVX]+:")
END_SECTION = re.compile(r"^\[End of section\]", re.IGNORECASE)
END_TABLE_FIGURE = re.compile(r"^\[End of (table|figure)\]", re.IGNORECASE)
END_LETTER = re.compile(r"^\[End of letter\]", re.IGNORECASE)
FOOTNOTES = re.compile(r"^Footnotes:?$")
CAPTION = re.compile(r"^(Table|Figure) \d+:")

BACK_MATTER_START = re.compile(
    r"^(Appendix [IVX]+:\s*)?(A )?GAO Contact( and Staff( A?cknowledgments)?)?:?$"
    r"|^Related GAO Products:?$"
    r"|^GAO.s Mission\b"  # the original-layout back cover runs heading and text together
    r"|^The (General Accounting|Government Accountability) Office, the (investigative|audit)"  # older back cover, no heading
    r"|^Obtaining Copies of( GAO Reports and Testimony)?:?$",
    re.IGNORECASE,
)
CONTENTS_START = "Contents:"
HIGHLIGHTS_START = "GAO Highlights:"
COMMENTS_START = re.compile(r"^Appendix [IVX]+: Comments from the\b", re.IGNORECASE)
TRAILING_PAGE_NUMBER = re.compile(r"\s\d{1,3}$")  # table-of-contents entry, not a section heading

ADDRESS_LINE = re.compile(r"^Washington,? D\.?\s?C\.?\b.{0,20}$|^\d{1,5} [A-Z][\w.]*( [\w.]+){0,3} (Street|Avenue|Pentagon)\b.{0,12}$")
GAO_LETTER_ADDRESS = re.compile(r"^Washington,? D\.?\s?C\.? 20548:?$")  # accessible text: the letter starts here
CONTENTS_MAX_LINES = 150  # safety cap: a contents list never runs this long
DRAFT_REPORT_LINE = re.compile(r"GAO Draft Report Dated", re.IGNORECASE)
REFER_TO_PDF = re.compile(r"^\[Refer to PDF", re.IGNORECASE)
SOURCE_LINE = re.compile(r"^Sources?:")

UNIT_END = (";", ":", ".")  # a line ending with one of these completes a unit (cell, header line, sentence)
CELL_MAX_WORDS = 8
CELL_MAX_CHARS = 60
LETTER_LINE_MAX_CHARS = 70
QUOTE_MAX_LINES = 3

ADMIN_SENTENCE = re.compile(
    "|".join(
        [
            r"\S+@\S+\.\w+",                              # e-mail address
            r"\(?\b\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b",     # telephone number
            r"\bpoint of contact\b",
            r"^of contact (is|for)\b",                    # "My point / of contact is ..." split across pages
            r"^My point$",
            r"\bplease contact\b",
            r"\bcontact me at\b",
            r"\bFor more information, contact\b",
            r"\bIf you or your staff have any questions\b",
            r"\bContact points for our Offices of Congressional Relations\b",
            r"\bWe appreciate the opportunity to comment\b",
            r"\bTo view the full product\b",
            r"\bStaff members (making|who made) key contributions\b",
            r"\bKey contributors to this report\b",
            r"\bWe are sending copies of this report\b",
            r"\bavailable at no charge on (the )?GAO.{0,3} Web ?site\b",
            r"\bresponse to the GAO draft report\b",
            r"\bcomments on the report recommendations are enclosed\b",
            r"\bincluded in the enclosure\b",
            r"\bThis is a work of the U\.S\. government\b",
            r"\bmay be reproduced and distributed in its entirety\b",
            r"\bmay contain copyrighted images\b",
            r"^Signed by\b",
            r"^Sincerely\b",
        ]
    ),
    re.IGNORECASE,
)
SENTENCE_BREAK = re.compile(r"(?<=[.!?])(?<!\b[A-Z]\.)\s+")  # no break after an initial ("Michael J. Sullivan")
MIN_PARAGRAPH_CHARS = 20


def is_heading(pattern: re.Pattern, line: str) -> bool:
    """True if ``line`` is the section heading itself, not a contents entry such as '... 45'."""
    return bool(pattern.match(line)) and not TRAILING_PAGE_NUMBER.search(line)


def is_cell_fragment(line: str) -> bool:
    """A short label/value table cell that completes on one line, e.g. 'Aircraft: BF3;' or '2016:'."""
    return line.endswith(UNIT_END) and len(line) <= CELL_MAX_CHARS and len(line.split()) <= CELL_MAX_WORDS


class HygieneTracker:
    """Line-level hygiene state for one document; state carries across pages."""

    def __init__(self, layout: str):
        self.layout = layout
        self.enabled = layout.startswith("gao")
        self.front_matter = layout == "gao_accessible_text"
        self.excluded: str | None = None  # rule name while inside an excluded section
        self.in_comments = False
        self.in_table = False
        self.quote_lines = 0
        self.prev: str | None = None
        self.page: int | None = None
        self.excluded_lines = 0
        self.warnings: list[str] = []  # collected by clean_page into the page warnings

    def check(self, line: str, pdf_page: int) -> str | None:
        """Return the rule name if ``line`` (stripped, non-empty) should be removed, else None."""
        if not self.enabled:
            return None
        if pdf_page != self.page:
            self.page = pdf_page
            if self.layout == "gao_original":
                # Original-layout appendices repeat their title as a running head on every page,
                # so the comments state is set per page and never carries into the next page.
                self.in_comments = False
        standalone = self.prev is None or self.prev.endswith(UNIT_END)
        rule = self._rule(line, pdf_page, standalone)
        self.prev = None if rule else line  # a removed line is a unit boundary for the next line
        return rule

    def _rule(self, s: str, pdf_page: int, standalone: bool) -> str | None:
        if self.front_matter:
            if s == HIGHLIGHTS_START or pdf_page > 1:
                self.front_matter = False
            else:
                return "front_matter"

        if self.excluded:
            self.excluded_lines += 1
            if self.excluded == "contents" and GAO_LETTER_ADDRESS.match(s):
                self.excluded = None  # no "[End of section]": the letter's address block starts here
                return "contents"
            if self.excluded == "contents" and self.excluded_lines > CONTENTS_MAX_LINES:
                self.excluded = None
                self.warnings.append(f"contents exclusion stopped after {CONTENTS_MAX_LINES} lines without an end marker")
            ends = END_SECTION.match(s) or (
                # back matter can also end at endnotes or a later appendix; the contents list
                # names every appendix, so it ends only at its own end marker (or the cap)
                self.excluded == "back_matter"
                and (FOOTNOTES.match(s) or (APPENDIX.match(s) and not is_heading(BACK_MATTER_START, s)))
            )
            if ends:
                self.excluded = None  # section over; this line is handled normally below
            elif self.excluded:
                return self.excluded

        if is_heading(BACK_MATTER_START, s):
            self.excluded, self.excluded_lines = "back_matter", 0
            self.in_comments = self.in_table = False
            return "back_matter"
        if self.layout == "gao_accessible_text" and s == CONTENTS_START:
            self.excluded, self.excluded_lines = "contents", 0
            return "contents"

        if is_heading(COMMENTS_START, s):
            self.in_comments = True
            return "agency_letter_furniture"
        if self.in_comments:
            if END_SECTION.match(s) or APPENDIX.match(s):
                self.in_comments = False
            else:
                rule = self._letter_rule(s, standalone)
                if rule:
                    return rule

        if self.layout == "gao_accessible_text":
            if not self.in_table and CAPTION.match(s):
                self.in_table = True
                return None  # the caption itself is kept
            if self.in_table:
                if END_TABLE_FIGURE.match(s) or END_SECTION.match(s):
                    self.in_table = False
                    return None
                if REFER_TO_PDF.match(s) or SOURCE_LINE.match(s):
                    return "table_furniture"
                if standalone and is_cell_fragment(s):
                    return "table_cell_fragment"
        return None

    def _letter_rule(self, s: str, standalone: bool) -> str | None:
        if self.quote_lines:  # continuing a quoted report-title restatement
            self.quote_lines = 0 if s.endswith('"') or self.quote_lines >= QUOTE_MAX_LINES else self.quote_lines + 1
            return "agency_letter_furniture"
        if standalone and s.startswith('"') and "." not in s:
            self.quote_lines = 0 if s.rstrip().endswith('"') and len(s) > 1 else 1
            return "agency_letter_furniture"
        if END_LETTER.match(s) or s.rstrip(",") == "Sincerely" or s.startswith("Signed by") or ADDRESS_LINE.match(s):
            return "agency_letter_furniture"
        if DRAFT_REPORT_LINE.search(s) and len(s) <= 100:
            return "agency_letter_furniture"
        if standalone and s.endswith(":") and len(s) <= LETTER_LINE_MAX_CHARS:
            return "agency_letter_furniture"  # header, salutation and signature lines
        return None


def strip_admin_sentences(text: str) -> tuple[str, list[str]]:
    """Remove administrative sentences from a paragraph. Returns (kept text, removed sentences)."""
    kept, removed = [], []
    for sentence in SENTENCE_BREAK.split(text):
        (removed if ADMIN_SENTENCE.search(sentence) else kept).append(sentence)
    result = " ".join(kept).strip()
    if removed and len(result) < MIN_PARAGRAPH_CHARS:  # only scraps left
        if result:
            removed.append(result)
        result = ""
    return result, removed
