"""Extract text from lesson-plan, recap, and AI-Agents-summary PDFs into
content/sources/.

This is the first step whenever you add new course material as a PDF: drop
the file into lesson_plans/, recap/, or agents_notes/ (the top-level repo
dirs) and run this script. It writes page-marked text to
content/sources/lesson_plans/*.txt, content/sources/recap/*.txt, or
content/sources/agents_recap/*.txt, which ingest/index_sources.py then
chunks and indexes.

Skips PDFs whose extracted .txt already exists and is newer than the PDF —
pass --force to re-extract everything regardless.

Run:  python -m ingest.extract_pdfs [--force]
"""

import argparse

import fitz  # PyMuPDF

from app import config


def extract_one(pdf_path, out_dir, force=False):
    """Extract one PDF's text into out_dir/{slug}.txt, page-marked.

    Parameters
    ----------
    pdf_path : Path
    out_dir : Path
    force : bool
        Re-extract even if an up-to-date .txt already exists.

    Returns
    -------
    bool
        True if a file was written, False if skipped (already up to date).
    """
    slug = pdf_path.stem.lower().replace(" ", "_")
    out_path = out_dir / f"{slug}.txt"
    if not force and out_path.exists() and out_path.stat().st_mtime >= pdf_path.stat().st_mtime:
        return False

    doc = fitz.open(pdf_path)
    text = "\n\n".join(f"--- page {i + 1} ---\n{page.get_text('text')}" for i, page in enumerate(doc))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text)
    print(f"  {pdf_path.name}: {doc.page_count} pages -> {out_path.relative_to(config.ROOT)}")
    return True


def main():
    """Extract every PDF in lesson_plans/ and recap/ that needs it."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="re-extract even if up to date")
    args = parser.parse_args()

    written = 0
    for pdf_dir, out_dir in [
        (config.LESSON_PLANS_PDF_DIR, config.LESSON_PLANS_TEXT_DIR),
        (config.RECAP_PDF_DIR, config.RECAP_TEXT_DIR),
        (config.AGENTS_RECAP_PDF_DIR, config.AGENTS_RECAP_TEXT_DIR),
    ]:
        for pdf in sorted(pdf_dir.glob("*.pdf")):
            written += extract_one(pdf, out_dir, force=args.force)

    print(f"\n{written} file(s) extracted (others already up to date).")
    if written:
        print("Next: python -m ingest.index_sources")


if __name__ == "__main__":
    main()
