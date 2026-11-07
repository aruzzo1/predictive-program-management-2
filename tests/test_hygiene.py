"""Tests for the retrieval-hygiene rules (administrative text removal)."""

import json
from pathlib import Path

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.ingestion.chunking import chunk_pages
from ppm_agent.ingestion.corpus_selection import PrototypeDocument
from ppm_agent.ingestion.hygiene import HygieneTracker, strip_admin_sentences
from ppm_agent.ingestion.page_extraction import HighlightsTracker, clean_page

SUBSTANTIVE = (
    "Software delivery to the test program that is essential to demonstrating full system capability "
    "is now expected in late 2014, a 3-year delay."
)


def make_doc(layout="gao_accessible_text", document_id="GAO-11-325"):
    return PrototypeDocument(
        document_id=document_id, filename=f"{document_id}.pdf", path=Path(f"{document_id}.pdf"),
        document_hash="ab" * 32, title="Test", organization="GAO", publication_date="2011-04-07",
        publication_date_review_flag=None, source_type="GAO report", layout=layout,
        pdf_page_range=None, printed_page_method="none", printed_page_map={},
    )


def clean_pages(raw_pages, layout="gao_accessible_text", first_page=5):
    """Run clean_page over consecutive pages with shared trackers (state carries across pages)."""
    doc = make_doc(layout)
    highlights, hygiene = HighlightsTracker(layout), HygieneTracker(layout)
    return [clean_page(raw, first_page + i, doc, highlights, hygiene) for i, raw in enumerate(raw_pages)]


def text_of(page):
    return " ".join(p["text"] for p in page.paragraphs)


def removed_rules(page):
    return {r["rule"] for r in page.removed}


# --- known boilerplate is excluded --------------------------------------------------


def test_back_matter_is_excluded_but_footnotes_after_it_are_kept():
    page = clean_pages([
        f"{SUBSTANTIVE}\n[End of section]\n"
        "Appendix IV: GAO Contact and Staff Acknowledgments:\n"
        "GAO Contact:\nMichael Sullivan (202) 512 4841 or sullivanm@gao.gov:\n[End of section]\n"
        "Related GAO Products:\nJoint Strike Fighter: Progress Made and Challenges Remain. GAO-07-360.\n[End of section]\n"
        "Footnotes:\n[14] Out of station work occurs when manufacturing steps are not completed at its designated\n"
        "work station and must be finished elsewhere later in production.\n"
    ])[0]

    text = text_of(page)
    assert "3-year delay" in text
    assert "Out of station work occurs" in text  # endnotes are evidence, not back matter
    assert "sullivanm@gao.gov" not in text and "Progress Made and Challenges Remain" not in text
    assert "back_matter" in removed_rules(page)


def test_contents_entry_with_page_number_does_not_start_back_matter():
    # Regression: a table-of-contents line must not open an exclusion that swallows the letter.
    pages = clean_pages([
        "Appendix IV: GAO Contact and Staff Acknowledgments 45\nRelated GAO Products 47\n",
        f"{SUBSTANTIVE}\n",
    ], layout="gao_original")
    assert "3-year delay" in text_of(pages[1])
    assert not any("back_matter" in removed_rules(p) for p in pages)


def test_contact_sentences_are_removed_and_technical_sentence_kept():
    text, removed = strip_admin_sentences(
        f"{SUBSTANTIVE} If you or your staff have any questions concerning this report, please contact me at "
        "(202) 512-4841. My point of contact is CAPT Gregg Sears, 703-695-3015, gregg.sears@osd.mil."
    )
    assert text == SUBSTANTIVE
    assert len(removed) == 2


def test_agency_letter_furniture_is_removed_but_dod_response_is_kept_and_tagged():
    pages = clean_pages([
        "[End of section]\nAppendix III: Comments from the Department of Defense:\n"
        "Office Of The Under Secretary Of Defense:\n3000 Defense Pentagon:\nWashington, DC 20301-3000\n"
        "Mr. Michael Sullivan:\nDear Mr. Sullivan:\n"
        "This is the Department of Defense (DoD) response to the GAO Draft Report, GAO-11-325.\n",
        "Sincerely,\nSigned by:\nDavid G. Ahern:\nDeputy Assistant Secretary of Defense:\n[End of letter]\n"
        "GAO Draft Report Dated February 28, 2011:\nGAO-11-325 (GAO Code 120918):\n"
        '"JOINT STRIKE FIGHTER: RESTRUCTURING PLACES PROGRAM ON FIRMER FOOTING,\n'
        'BUT PROGRESS IS STILL LAGGING OVERALL"\n'
        "The F-35 Program Executive Officer executed an extensive bottoms-up Technical Baseline Review\n"
        "involving over 120 tactical aircraft experts to evaluate every aspect of the SDD phase.\n"
        "The topics and metrics that are assessed include, but are not limited to,\n"
        "the following:\n",
    ])

    kept = text_of(pages[1])
    assert "Technical Baseline Review" in kept
    assert "the following:" in kept  # a wrapped prose line ending in ':' is not letter furniture
    for furniture in ("Pentagon", "Dear Mr.", "Signed by", "Ahern", "GAO Code", "LAGGING OVERALL", "response to the GAO Draft"):
        assert furniture not in text_of(pages[0]) + kept
    assert {p["section_type"] for p in pages[1].paragraphs} == {"agency_comments"}


def test_original_layout_comments_running_head_does_not_leak_to_next_page():
    pages = clean_pages([
        "Appendix III: Comments from the Department\n",  # image-only appendix page: only the running head
        f"{SUBSTANTIVE}\n",
    ], layout="gao_original")
    assert pages[0].skipped_reason.startswith("administrative content only")
    assert [p["section_type"] for p in pages[1].paragraphs] == [None]


def test_original_layout_back_cover_is_excluded():
    page = clean_pages([
        "GAO’s Mission The Government Accountability Office, the audit, evaluation, and investigative arm\n"
        "of Congress, exists to support Congress in meeting its constitutional responsibilities.\n"
        "Obtaining Copies of\nGAO Reports and\nTestimony\n",
    ], layout="gao_original")[0]
    assert page.skipped_reason == "administrative content only (back_matter)"


def test_accessible_table_cell_fragments_removed_prose_cells_and_caption_kept():
    page = clean_pages([
        "Figure 3: JSF Labor Hours for Manufacturing Test Aircraft:\n"
        "[Refer to PDF for image: multiple line graph]\n"
        "Aircraft: BF3;\n2007 Budget: 179,892;\nAircraft: BF4;\n"
        "Explanation: The schedule should use logic and durations in order to\n"
        "reflect realistic start and completion dates;\n"
        "Source: GAO analysis of DOD data.\n[End of figure]\n"
        f"{SUBSTANTIVE}\n"
    ])[0]

    text = text_of(page)
    assert "Figure 3: JSF Labor Hours" in text
    assert "logic and durations" in text and "completion dates;" in text  # wrapped prose cell intact
    assert "Aircraft: BF3" not in text and "Refer to PDF" not in text and "Source: GAO" not in text
    assert "3-year delay" in text
    assert {"table_cell_fragment", "table_furniture"} <= removed_rules(page)


def test_short_genuine_text_on_a_mostly_tabular_page_is_kept():
    pages = clean_pages([
        "Figure 2: Monthly Design Changes for JSF Aircraft:\n",
        "January;\nDesign changes (actual): 251.\n"
        "Program now anticipates 10,000 more design changes than anticipated in 2007.\n",
    ])
    assert pages[1].skipped_reason is None
    assert "10,000 more design changes" in text_of(pages[1])


def test_every_removal_is_logged_with_its_rule_and_text():
    page = clean_pages([f"Contents:\nLetter:\nBackground:\n[End of section]\n{SUBSTANTIVE}\n"])[0]
    assert page.removed[0]["rule"] == "contents"
    assert "Letter:" in page.removed[0]["text"] and "Background:" in page.removed[0]["text"]
    assert page.dropped["contents"] == 3


# --- rules are independent of the evaluation questions -------------------------------


def test_rules_do_not_depend_on_evaluation_question_wording():
    questions = json.loads((PROJECT_ROOT / "data/metadata/rag_evaluation_questions.json").read_text(encoding="utf-8"))
    for q in questions["questions"]:
        for field in ("question", "expected_evidence_type"):
            text = q[field]
            assert strip_admin_sentences(text) == (text, [])  # question vocabulary is never removed
            tracker = HygieneTracker("gao_accessible_text")
            tracker.front_matter = False
            assert tracker.check(text, pdf_page=5) is None


def test_dote_layout_only_drops_the_contractor_address_line():
    doc = make_doc("dote_annual_report", "DOTE-FY2010-F35")
    page = clean_page(
        "• The program incrementally provides mission capability:\nBlock 1 (initial), Block 2 (advanced), Block 3 (full).\n"
        "major contractor\nLockheed Martin, Aeronautics Division, Advanced Development\nPrograms – Fort Worth, Texas\n"
        "activity\n• All three F-35 variants had entered flight test by June 2010.\n",
        30, doc, HighlightsTracker(doc.layout), HygieneTracker(doc.layout),
    )
    text = text_of(page)
    assert "Block 1 (initial)" in text and "entered flight test" in text
    assert "Lockheed Martin" not in text
    assert removed_rules(page) == {"dote_contractor_line"}


# --- general rules added for the RAG_EXPANDED_V2 sources --------------------------------


NARROW_PROSE = (  # every line <= 30 characters, as in a narrow DOT&E column
    "The program planned for the\nTR-3 upgrade to cut into\nthe production line in time\n"
    "to deliver with the Lot 15\naircraft in 2023.\n"
)


def dote_page(raw, layout="dote_annual_report"):
    doc = make_doc(layout, "DOTE-FY2024-F35")
    return clean_page(raw, 3, doc, HighlightsTracker(layout), HygieneTracker(layout))


def test_later_dote_running_heads_are_page_furniture():
    page = dote_page(f"Article 47\n{SUBSTANTIVE}\n45F-35 45\n44 F-35\n")
    assert text_of(page) == SUBSTANTIVE


def test_narrow_column_prose_is_kept_in_dote_layout_only():
    labels = "ALL VARIANTS\nFLIGHT SCIENCES\nMISSION SYSTEMS\n"
    dote = dote_page(NARROW_PROSE + labels)
    assert "TR-3 upgrade to cut into the production line in time" in text_of(dote)  # wrapped prose kept
    assert "FLIGHT SCIENCES" not in text_of(dote)                            # label residue still dropped

    gao = clean_pages([NARROW_PROSE + f"{SUBSTANTIVE}\n"], layout="gao_original")[0]
    assert "TR-3 upgrade" not in text_of(gao)  # GAO layouts are unchanged: short-line runs are still dropped


def test_split_major_contractors_heading_drops_contractor_lines():
    page = dote_page(
        f"{SUBSTANTIVE}\n» MAJOR\nCONTRACTORS:\n• Lockheed Martin Aeronautics\nCompany – Fort Worth, Texas\n"
        "• Pratt & Whitney, a subsidiary\nof RTX – East Hartford,\nConnecticut\n"
    )
    assert text_of(page) == SUBSTANTIVE
    assert "dote_contractor_line" in removed_rules(page)


def test_contents_without_end_marker_ends_at_the_letter_address():
    page = clean_pages([
        "Contents:\nLetter:\nResults in Brief:\nAbbreviations:\nDOD: Department of Defense:\n"
        "United States Government Accountability Office:\nWashington, DC 20548:\n"
        f"{SUBSTANTIVE}\n"
    ])[0]
    assert "3-year delay" in text_of(page)
    assert "Results in Brief" not in text_of(page)


def test_contents_exclusion_is_capped_and_warns():
    pages = clean_pages(["Contents:\n" + "Heading entry:\n" * 160 + f"{SUBSTANTIVE}\n"])
    assert "3-year delay" in text_of(pages[0])
    assert any("contents exclusion stopped" in w for w in pages[0].warnings)


def test_older_gao_back_cover_without_heading_is_excluded():
    page = clean_pages([
        "The General Accounting Office, the investigative arm of Congress, exists to\n"
        "support Congress in meeting its constitutional responsibilities.\n"
    ], layout="gao_original")[0]
    assert page.skipped_reason == "administrative content only (back_matter)"


def test_acknowledgment_and_signature_with_initials_are_removed():
    text, removed = strip_admin_sentences(
        f"{SUBSTANTIVE} Key contributors to this report were Robert Pelletier and Brian Mullins. "
        "Sincerely yours, Katherine V. Schinasi Director, Acquisition and Sourcing Management"
    )
    assert text == SUBSTANTIVE
    assert len(removed) == 2  # the signature is one sentence: no break after the initial "V."


def test_street_address_in_agency_letter_is_removed():
    pages = clean_pages([
        "Appendix I: Comments from the Department of Defense:\nMr. David M. Walker:\n441 G Street N.W.\n"
        "Washington, DC 20548\nThe Department partially concurs with the recommendation to delay the production decision.\n"
    ])
    assert "441 G Street" not in text_of(pages[0])
    assert "partially concurs" in text_of(pages[0])


# --- provenance is intact -------------------------------------------------------------


def test_page_and_source_metadata_survive_hygiene_and_chunking():
    page = clean_pages([
        f"{SUBSTANTIVE} For more information, contact Michael J. Sullivan at (202) 512-4841 or sullivanm@gao.gov.\n"
    ], first_page=31)[0]
    meta = make_doc().chunk_metadata()

    chunk = chunk_pages([page], meta)[0]

    assert chunk["text"] == SUBSTANTIVE
    assert chunk["pdf_page"] == 31
    assert chunk["chunk_id"] == "GAO-11-325-p031-c00"
    for key, value in meta.items():
        assert chunk[key] == value
