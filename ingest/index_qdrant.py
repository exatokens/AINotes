"""Chunk the authored textbook pages and index them into Qdrant.

This collection (config.COLLECTION_PAGES) backs only the sidebar "search the
textbook" box — it lets a search jump straight to a reader page. It is
separate from config.COLLECTION_SOURCES (see index_sources.py), which holds
raw lesson-plan/recap/transcript chunks and grounds the RAG chat.

Each page is split on ``##`` headings; each section becomes one chunk (long
sections are further split on paragraph boundaries at ~1800 chars). Chunks are
embedded with all-MiniLM-L6-v2 on the SV cluster and upserted into Qdrant
(the collection is recreated on every run — safe, it only holds derived data).

Run:  python -m ingest.index_qdrant
"""

import re
import uuid

import requests

from app import config
from app.content_store import all_pages
from app.rag import embed


def strip_markdown(md):
    """Remove markdown/mermaid syntax so embeddings see clean prose.

    Parameters
    ----------
    md : str

    Returns
    -------
    str
        Prose with code fences kept (code is meaningful), mermaid dropped,
        emphasis/links unwrapped.
    """
    md = re.sub(r"```mermaid.*?```", "", md, flags=re.DOTALL)
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    md = re.sub(r"[*_`#>]+", " ", md)
    return re.sub(r"[ \t]+", " ", md).strip()


def chunk_page(page):
    """Split one page into (section_title, text) chunks.

    Parameters
    ----------
    page : dict
        Page dict from content_store.all_pages().

    Returns
    -------
    list[tuple[str, str]]
        Section title + cleaned chunk text pairs.
    """
    md = page["markdown"]
    parts = re.split(r"^## +(.+)$", md, flags=re.MULTILINE)
    sections = [("Overview", parts[0])] if parts[0].strip() else []
    for i in range(1, len(parts), 2):
        sections.append((parts[i].strip(), parts[i + 1]))

    chunks = []
    for title, body in sections:
        text = strip_markdown(body)
        if not text:
            continue
        while len(text) > config.PAGE_CHUNK_CHARS:
            cut = text.rfind("\n", 0, config.PAGE_CHUNK_CHARS)
            cut = cut if cut > config.PAGE_CHUNK_CHARS // 2 else config.PAGE_CHUNK_CHARS
            chunks.append((title, text[:cut].strip()))
            text = text[cut:].strip()
        chunks.append((title, text))
    return chunks


def main():
    """Recreate the collection and index every chunk of every page."""
    q = config.QDRANT_URL
    requests.delete(f"{q}/collections/{config.COLLECTION_PAGES}", timeout=30)
    r = requests.put(
        f"{q}/collections/{config.COLLECTION_PAGES}",
        json={"vectors": {"size": config.EMBED_DIM, "distance": "Cosine"}},
        timeout=30,
    )
    r.raise_for_status()

    points = []
    for page in all_pages().values():
        for section, text in chunk_page(page):
            # prefix with page context so the embedding carries the topic
            embed_text = f"{page['title']} — {section}. {text}"
            points.append(
                {
                    "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{page['id']}#{section}#{text[:60]}")),
                    "payload": {
                        "page_id": page["id"],
                        "title": page["title"],
                        "week": page["week"],
                        "section": section,
                        "text": text,
                    },
                    "_embed": embed_text,
                }
            )

    print(f"{len(points)} chunks from {len(all_pages())} pages; embedding…")
    for i in range(0, len(points), 32):
        batch = points[i : i + 32]
        vecs = embed([p.pop("_embed") for p in batch])
        for p, v in zip(batch, vecs):
            p["vector"] = v
        r = requests.put(
            f"{q}/collections/{config.COLLECTION_PAGES}/points?wait=true",
            json={"points": batch},
            timeout=60,
        )
        r.raise_for_status()
        print(f"  upserted {min(i + 32, len(points))}/{len(points)}")
    print("done.")


if __name__ == "__main__":
    main()
