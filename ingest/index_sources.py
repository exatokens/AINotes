"""Chunk and index the RAW course material — lesson plans, recaps, and video
transcripts — into Qdrant, to ground the RAG chat in the actual course content
(as opposed to the hand-authored textbook pages, which are indexed separately
by index_qdrant.py and used only for sidebar page search).

Sources (see README.md "Adding new data" for how each gets here):
  content/sources/lesson_plans/*.txt - from ingest/extract_pdfs.py
  content/sources/recap/*.txt        - from ingest/extract_pdfs.py
  content/sources/transcripts/*.json - from ingest/fetch_transcripts.py

Each lesson-plan/recap file's week and title are auto-inferred from its
filename (see config.DOC_WEEK_OVERRIDES / config.DOC_TITLE_OVERRIDES for the
rare edge cases that need a manual override) — adding a new, sensibly-named
PDF requires no code changes here at all.

Each chunk's payload carries enough to cite it precisely: for PDFs, a page
range; for transcripts, a timestamp and a direct "jump to this moment" URL.

Run:  python -m ingest.index_sources
"""

import json
import re
import uuid

import requests

from app import config
from app.rag import embed

WEEK_RE = re.compile(r"week[-_]?(\d+)", re.IGNORECASE)


def infer_week(stem):
    """Work out which course week a lesson-plan/recap file belongs to.

    Parameters
    ----------
    stem : str
        Filename without extension, e.g. "week-3-summer-lesson-plan".

    Returns
    -------
    int

    Raises
    ------
    ValueError
        If the filename has no "weekN" pattern and isn't listed in
        config.DOC_WEEK_OVERRIDES.
    """
    if stem in config.DOC_WEEK_OVERRIDES:
        return config.DOC_WEEK_OVERRIDES[stem]
    m = WEEK_RE.search(stem)
    if not m:
        raise ValueError(
            f"can't infer week for {stem!r} (no 'weekN' in the filename) — "
            f"add it to config.DOC_WEEK_OVERRIDES"
        )
    return int(m.group(1))


def infer_title(stem, week, kind):
    """Work out a display title for a lesson-plan/recap file.

    Parameters
    ----------
    stem : str
    week : int
    kind : str
        "lesson_plan" or "recap".

    Returns
    -------
    str
        config.DOC_TITLE_OVERRIDES[stem] if present, else a generic
        "Week {week} Lesson Plan" / "Week {week} Recap".
    """
    if stem in config.DOC_TITLE_OVERRIDES:
        return config.DOC_TITLE_OVERRIDES[stem]
    label = "Lesson Plan" if kind == "lesson_plan" else "Recap"
    return f"Week {week} {label}"


def chunk_doc_text(text):
    """Split page-marked source text into (section_label, chunk_text) pairs.

    Parameters
    ----------
    text : str
        Full extracted text with ``--- page N ---`` markers.

    Returns
    -------
    list[tuple[str, str]]
        (page range label, chunk text), each chunk roughly
        <= config.SOURCE_CHUNK_CHARS.
    """
    pages = re.split(r"--- page (\d+) ---", text)
    # re.split with a capturing group yields [pre, num1, body1, num2, body2, ...]
    page_bodies = []
    for i in range(1, len(pages), 2):
        page_bodies.append((int(pages[i]), pages[i + 1].strip()))

    chunks = []
    buf, buf_start, buf_end = "", None, None
    for num, body in page_bodies:
        if not body:
            continue
        if buf_start is None:
            buf_start = num
        candidate = f"{buf}\n\n{body}".strip() if buf else body
        if len(candidate) > config.SOURCE_CHUNK_CHARS and buf:
            chunks.append((f"pages {buf_start}-{buf_end}", buf.strip()))
            buf, buf_start = body, num
        else:
            buf = candidate
        buf_end = num
    if buf.strip():
        chunks.append((f"pages {buf_start}-{buf_end}", buf.strip()))
    return chunks


def chunk_transcript(segments):
    """Group transcript segments into ~config.TRANSCRIPT_CHUNK_CHARS windows.

    Parameters
    ----------
    segments : list[dict]
        [{"text": str, "start": float, "duration": float}, ...]

    Returns
    -------
    list[tuple[str, float, str]]
        (mm:ss section label, start seconds, chunk text).
    """
    chunks = []
    buf, buf_start = [], None
    for seg in segments:
        if buf_start is None:
            buf_start = seg["start"]
        buf.append(seg["text"])
        if sum(len(t) for t in buf) > config.TRANSCRIPT_CHUNK_CHARS:
            text = " ".join(buf).strip()
            m, s = divmod(int(buf_start), 60)
            chunks.append((f"{m:02d}:{s:02d}", buf_start, text))
            buf, buf_start = [], None
    if buf:
        text = " ".join(buf).strip()
        m, s = divmod(int(buf_start), 60)
        chunks.append((f"{m:02d}:{s:02d}", buf_start, text))
    return chunks


def gather_points():
    """Build all (payload, embed_text) pairs from every source document.

    Returns
    -------
    list[dict]
        Each with an ``_embed`` key (text to embed) plus the final payload
        fields (kind, week, title, section, text, url).
    """
    points = []

    for kind, text_dir in [
        ("lesson_plan", config.LESSON_PLANS_TEXT_DIR),
        ("recap", config.RECAP_TEXT_DIR),
    ]:
        for f in sorted(text_dir.glob("*.txt")):
            week = infer_week(f.stem)
            title = infer_title(f.stem, week, kind)
            for section, text in chunk_doc_text(f.read_text()):
                points.append({
                    "payload": {
                        "kind": kind, "week": week, "title": title,
                        "section": section, "text": text, "url": None,
                    },
                    "_embed": f"{title} — {section}. {text}",
                })

    for f in sorted(config.TRANSCRIPTS_DIR.glob("*.json")):
        data = json.loads(f.read_text())
        m = re.match(r"Week_(\d+)_(Main|Summary)_class", data["label"], re.IGNORECASE)
        week = int(m.group(1)) if m else 0
        kind_label = "Main Class" if m and m.group(2).lower() == "main" else "Summary Class"
        title = f"Week {week} {kind_label} (video)"
        for section, start_s, text in chunk_transcript(data["segments"]):
            points.append({
                "payload": {
                    "kind": "transcript", "week": week, "title": title,
                    "section": section, "text": text,
                    "url": f"{data['url']}&t={int(start_s)}s",
                },
                "_embed": f"{title} — {section}. {text}",
            })

    return points


def main():
    """Recreate the sources collection and index every chunk."""
    q = config.QDRANT_URL
    requests.delete(f"{q}/collections/{config.COLLECTION_SOURCES}", timeout=30)
    r = requests.put(
        f"{q}/collections/{config.COLLECTION_SOURCES}",
        json={"vectors": {"size": config.EMBED_DIM, "distance": "Cosine"}},
        timeout=30,
    )
    r.raise_for_status()

    points = gather_points()
    print(f"{len(points)} chunks from lesson plans + recaps + transcripts; embedding…")
    for i in range(0, len(points), 32):
        batch = points[i:i + 32]
        vecs = embed([p.pop("_embed") for p in batch])
        payloads = [{"id": str(uuid.uuid4()), "vector": v, "payload": p["payload"]}
                    for p, v in zip(batch, vecs)]
        r = requests.put(
            f"{q}/collections/{config.COLLECTION_SOURCES}/points?wait=true",
            json={"points": payloads},
            timeout=60,
        )
        r.raise_for_status()
        print(f"  upserted {min(i + 32, len(points))}/{len(points)}")
    print("done.")


if __name__ == "__main__":
    main()
