#!/usr/bin/env python3
"""Recreate the legacy 12-by-18-only convenience PDF.

This optional provenance step is not part of the trusted proof checker.  The
arXiv source of record is main.tex.  The current source also records the
12-by-17 and 12-by-19 results, so this script intentionally produces only the retained
earlier rendering and should not be used as an arXiv source generator.
Requires PyMuPDF (fitz).
"""
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reference_pdf" / "Z1218_exact_108_base.pdf"
OUTPUT = ROOT / "reference_pdf" / "Z1218_exact_108.pdf"


def main() -> None:
    doc = fitz.open(SOURCE)
    page = doc[4]
    heading = page.search_for("Acknowledgment of computational assistance")
    if len(heading) != 1:
        raise RuntimeError(f"expected one old heading, found {len(heading)}")
    if not page.search_for("The investigation, implementation, checking and packaging used extensive AI assistance."):
        raise RuntimeError("old acknowledgement body was not found")
    for rect in (heading[0], fitz.Rect(71.5, 226.5, 541.0, 269.0)):
        page.add_redact_annot(rect, fill=(1, 1, 1))
    page.apply_redactions()
    page.insert_text((72, 211.6), "Acknowledgements", fontname="times-bold",
                     fontsize=14.3462, color=(0, 0, 0))
    body = (
        "OpenAI GPT 5.6 Sol High was used for assistance with exploratory reasoning, "
        "implementation, verification and packaging. The author is solely responsible "
        "for the mathematical claims and final manuscript. No heuristic solver status "
        "is used as a theorem."
    )
    result = page.insert_textbox(
        fitz.Rect(72, 228, 541, 274), body, fontname="times-roman",
        fontsize=10.9, lineheight=1.25, color=(0, 0, 0)
    )
    if result < 0:
        raise RuntimeError(f"acknowledgement did not fit: {result}")

    # Synchronize the literature paragraph and bibliography with main.tex.
    intro_page = doc[0]
    old_intro_anchor = intro_page.search_for("bounds for many small Zarankiewicz parameters")
    old_gap_anchor = intro_page.search_for("Z(12, 22; 3, 3) = 132 [2].")
    old_intro_line = [fitz.Rect(71.5, 565.5, 542.5, 578.0)]
    old_gap_line = [fitz.Rect(71.5, 592.5, 542.5, 605.5)]
    if len(old_intro_anchor) != 1 or len(old_gap_anchor) != 1:
        raise RuntimeError("old literature paragraph was not found")
    for rect in (old_intro_line[0], old_gap_line[0]):
        intro_page.add_redact_annot(rect, fill=(1, 1, 1))
    intro_page.apply_redactions()
    intro_page.insert_text(
        (72, 574.9),
        "bounds for many small Zarankiewicz parameters [1]. Bhan, Nobili and Langer subse-",
        fontname="times-roman", fontsize=10.9, color=(0, 0, 0)
    )
    intro_page.insert_text(
        (72, 602.0),
        "Z(12, 22; 3, 3) = 132 [2]. Prior bounds were 108--113; this work proves equality at 108.",
        fontname="times-roman", fontsize=10.9, color=(0, 0, 0)
    )

    bib_page = doc[5]
    old_bib_anchor = bib_page.search_for("Raghuraman")
    old_bib_line = [fitz.Rect(71.5, 413.0, 541.5, 426.0)]
    if len(old_bib_anchor) != 1:
        raise RuntimeError("old bibliography line was not found")
    bib_page.add_redact_annot(old_bib_line[0], fill=(1, 1, 1))
    bib_page.apply_redactions()
    bib_page.insert_text(
        (72, 424.7),
        "[2] J. Bhan, N. Nobili and P. Langer, New Bounds for Zarankiewicz Numbers via",
        fontname="times-roman", fontsize=10.9, color=(0, 0, 0)
    )
    doc.save(OUTPUT, garbage=4, deflate=True, no_new_id=True)


if __name__ == "__main__":
    main()
