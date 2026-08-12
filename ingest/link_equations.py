"""Find the best-matching lecture/lesson-plan source for every display
equation ($$...$$) across all authored concept pages, so the reader can jump
straight to the video moment (or see the PDF reference) an equation actually
came from.

For each equation, the paragraph of prose immediately preceding it is used as
the search query against the raw-source Qdrant collection (config.
COLLECTION_SOURCES) — that surrounding prose is what actually describes the
equation in the page's own words, and matches far better than embedding raw
LaTeX would. Among the top hits, a transcript (clickable video timestamp) is
preferred over a PDF source if its score is close to the top match, since a
video citation is more useful to click through to than a static page number.

Writes content/equation_citations.json:
    { page_id: [ {title, section, kind, url, score} | null, ... ] }
index-aligned with the page's own $$...$$ blocks in document order (as they
appear after KaTeX rendering, one per .katex-display element); null means no
confident match was found.

Run:  python -m ingest.link_equations
"""

import json
import re

from app import config
from app.content_store import all_pages
from app.rag import search_sources

EQUATION_RE = re.compile(r"\$\$([\s\S]+?)\$\$")


def find_citation(query_text):
    """Search for the best source chunk matching an equation's context.

    Parameters
    ----------
    query_text : str
        The prose preceding the equation, plus the equation itself.

    Returns
    -------
    dict | None
        {title, section, kind, url, score}, or None if nothing scored above
        config.EQUATION_CITATION_MIN_SCORE.
    """
    hits = search_sources(query_text, limit=4)
    if not hits:
        return None
    best = hits[0]
    for h in hits[1:]:
        if h["kind"] == "transcript" and best["score"] - h["score"] <= config.EQUATION_CITATION_TRANSCRIPT_MARGIN:
            best = h
            break
    if best["score"] < config.EQUATION_CITATION_MIN_SCORE:
        return None
    return {
        "title": best["title"],
        "section": best["section"],
        "kind": best["kind"],
        "url": best.get("url"),
        "score": best["score"],
    }


def main():
    """Match every page's display equations to a source and write the JSON."""
    result = {}
    pages = all_pages()
    total_eq, total_matched = 0, 0

    for page in pages.values():
        md = page["markdown"]
        matches = list(EQUATION_RE.finditer(md))
        citations = []
        for m in matches:
            start = max(0, m.start() - config.EQUATION_CITATION_CONTEXT_CHARS)
            context = md[start:m.start()]
            context = re.sub(r"[#*>`_]", " ", context).strip()
            query = f"{context}\n{m.group(1)}".strip()[-(config.EQUATION_CITATION_CONTEXT_CHARS + 200):]
            citation = find_citation(query)
            citations.append(citation)
            total_eq += 1
            total_matched += citation is not None
        result[page["id"]] = citations
        if citations:
            print(f"  {page['id']}: {len(citations)} equations, "
                  f"{sum(1 for c in citations if c)} matched")

    config.EQUATION_CITATIONS_FILE.write_text(json.dumps(result, indent=2))
    print(f"\n{total_matched}/{total_eq} equations matched across {len(pages)} pages")


if __name__ == "__main__":
    main()
