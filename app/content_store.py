"""Load and serve the authored textbook content (markdown pages + topic tree).

Pages live in content/pages/*.md, each with a simple YAML-ish frontmatter block:

    ---
    id: w1-semantic-search
    title: Semantic vs Lexical Search
    week: 1
    topic: "Act I: The Magic, and the Map"
    order: 2
    summary: One-line summary used in search results and the tree tooltip.
    course: beyond_rag
    ---
    (markdown body)

The frontmatter is intentionally flat key: value pairs, parsed without a YAML
dependency. ``course`` distinguishes the two courses sharing this reader
(config.BEYOND_RAG_COURSE / config.AGENTS_COURSE) and defaults to
beyond_rag when omitted, since that's every page written before the AI
Agents Bootcamp content was added.
"""

import json
import re

from . import config


def parse_frontmatter(text):
    """Split a page file into (meta dict, markdown body).

    Parameters
    ----------
    text : str
        Full file contents starting with a ``---`` frontmatter fence.

    Returns
    -------
    tuple[dict, str]
        Metadata (values are str, ``week``/``order`` coerced to int) and body.

    Raises
    ------
    ValueError
        If the frontmatter fence is missing.
    """
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError("missing frontmatter")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip().strip('"')
    for key in ("week", "order"):
        if key in meta:
            meta[key] = int(meta[key])
    meta.setdefault("course", config.BEYOND_RAG_COURSE)
    return meta, m.group(2).strip()


def all_pages():
    """Load every page in content/pages, fresh from disk on every call.

    Not cached: the corpus is small (~65 short markdown files), reading it
    is cheap, and this is authored content that gets edited while the app
    is running — a stale cache would silently keep serving old prose after
    an edit until the process restarted.

    Returns
    -------
    dict[str, dict]
        Map of page id -> {id, title, week, topic, order, summary, markdown}.
    """
    pages = {}
    for f in sorted(config.PAGES_DIR.glob("*.md")):
        meta, body = parse_frontmatter(f.read_text())
        meta["markdown"] = body
        pages[meta["id"]] = meta
    return pages


def get_page(page_id):
    """Return one page dict by id, or None if unknown."""
    return all_pages().get(page_id)


def get_tree():
    """Return the topic tree (weeks -> topics -> concept refs) as parsed JSON."""
    return json.loads(config.TREE_FILE.read_text())


def get_equation_citations(page_id):
    """Return the source citation for each of a page's display equations.

    Parameters
    ----------
    page_id : str

    Returns
    -------
    list[dict | None]
        Index-aligned with the page's ``$$...$$`` blocks in document order
        (see ingest/link_equations.py); each entry is either
        {title, section, kind, url, score} or None if no confident source
        match was found for that equation. Empty list if the citations file
        hasn't been built yet or the page has no equations.
    """
    if not config.EQUATION_CITATIONS_FILE.exists():
        return []
    data = json.loads(config.EQUATION_CITATIONS_FILE.read_text())
    return data.get(page_id, [])
