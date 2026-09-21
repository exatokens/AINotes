"""Chunk and index the RAW course material — lesson plans, recaps, video
transcripts, and blog posts — into Qdrant, to ground the RAG chat in the
actual course content (as opposed to the hand-authored textbook pages, which
are indexed separately by index_qdrant.py and used only for sidebar page
search).

Two courses share this one collection, distinguished by a "course" field on
every payload (config.BEYOND_RAG_COURSE / config.AGENTS_COURSE) since both
reuse Week 1-13 numbering:

  Beyond RAG (see README.md "Adding new data" for how each gets here):
    content/sources/lesson_plans/*.txt - from ingest/extract_pdfs.py
    content/sources/recap/*.txt        - from ingest/extract_pdfs.py
    content/sources/transcripts/*.json - from ingest/fetch_transcripts.py

  AI Agents Bootcamp:
    content/sources/agents_recap/*.txt       - from ingest/extract_pdfs.py
    content/sources/agents_transcripts/*.json - from ingest/fetch_transcripts.py
    content/sources/agents_blogs/*.txt        - from ingest/fetch_blogs.py

Each lesson-plan/recap file's week and title are auto-inferred from its
filename (see config.DOC_WEEK_OVERRIDES / config.DOC_TITLE_OVERRIDES, and the
AI Agents equivalent config.AGENTS_DOC_WEEK_OVERRIDES, for filenames that
need a manual override) — adding a new, sensibly-named PDF requires no code
changes here at all.

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


def infer_week(stem, overrides=config.DOC_WEEK_OVERRIDES):
    """Work out which course week a lesson-plan/recap file belongs to.

    Parameters
    ----------
    stem : str
        Filename without extension, e.g. "week-3-summer-lesson-plan".
    overrides : dict[str, int]
        Manual stem -> week overrides to check first (defaults to the
        Beyond RAG table; pass config.AGENTS_DOC_WEEK_OVERRIDES for AI Agents).

    Returns
    -------
    int

    Raises
    ------
    ValueError
        If the filename has no "weekN" pattern and isn't listed in overrides.
    """
    if stem in overrides:
        return overrides[stem]
    m = WEEK_RE.search(stem)
    if not m:
        raise ValueError(
            f"can't infer week for {stem!r} (no 'weekN' in the filename) — "
            f"add it to the relevant *_WEEK_OVERRIDES table in app/config.py"
        )
    return int(m.group(1))


def infer_title(stem, week, kind, course=config.BEYOND_RAG_COURSE):
    """Work out a display title for a lesson-plan/recap file.

    Parameters
    ----------
    stem : str
    week : int
    kind : str
        "lesson_plan" or "recap".
    course : str
        Prefixed onto the title for non-Beyond-RAG courses, since both
        courses reuse Week 1-13 and a bare "Week 5 Recap" would otherwise be
        ambiguous in chat citations.

    Returns
    -------
    str
        config.DOC_TITLE_OVERRIDES[stem] if present, else a generic
        "Week {week} Lesson Plan" / "Week {week} Recap".
    """
    if stem in config.DOC_TITLE_OVERRIDES:
        return config.DOC_TITLE_OVERRIDES[stem]
    label = "Lesson Plan" if kind == "lesson_plan" else "Recap"
    title = f"Week {week} {label}"
    if course != config.BEYOND_RAG_COURSE:
        title = f"AI Agents — {title}"
    return title


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


def chunk_blog_text(text):
    """Split a blog post's plain text into ~config.SOURCE_CHUNK_CHARS chunks.

    Parameters
    ----------
    text : str
        Plain prose (no page markers), paragraphs separated by blank lines.

    Returns
    -------
    list[str]
    """
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, buf = [], ""
    for p in paragraphs:
        candidate = f"{buf}\n\n{p}".strip() if buf else p
        if len(candidate) > config.SOURCE_CHUNK_CHARS and buf:
            chunks.append(buf.strip())
            buf = p
        else:
            buf = candidate
    if buf.strip():
        chunks.append(buf.strip())
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
        fields (course, kind, week, title, section, text, url).
    """
    points = []

    for course, kind, text_dir, overrides in [
        (config.BEYOND_RAG_COURSE, "lesson_plan", config.LESSON_PLANS_TEXT_DIR, config.DOC_WEEK_OVERRIDES),
        (config.BEYOND_RAG_COURSE, "recap", config.RECAP_TEXT_DIR, config.DOC_WEEK_OVERRIDES),
        (config.AGENTS_COURSE, "recap", config.AGENTS_RECAP_TEXT_DIR, config.AGENTS_DOC_WEEK_OVERRIDES),
    ]:
        for f in sorted(text_dir.glob("*.txt")):
            week = infer_week(f.stem, overrides)
            title = infer_title(f.stem, week, kind, course)
            for section, text in chunk_doc_text(f.read_text()):
                points.append({
                    "payload": {
                        "course": course, "kind": kind, "week": week, "title": title,
                        "section": section, "text": text, "url": None,
                    },
                    "_embed": f"{title} — {section}. {text}",
                })

    for course, transcripts_dir, label_re in [
        (config.BEYOND_RAG_COURSE, config.TRANSCRIPTS_DIR, re.compile(r"Week_(\d+)_(Main|Summary)_class", re.IGNORECASE)),
        (config.AGENTS_COURSE, config.AGENTS_TRANSCRIPTS_DIR, re.compile(r"AgentsWeek_(\d+)", re.IGNORECASE)),
    ]:
        for f in sorted(transcripts_dir.glob("*.json")):
            data = json.loads(f.read_text())
            m = label_re.match(data["label"])
            week = int(m.group(1)) if m else 0
            kind_label = "Main Class" if (m and m.re.groups > 1 and m.group(2).lower() == "main") else "Class"
            title = f"Week {week} {kind_label} (video)"
            if course != config.BEYOND_RAG_COURSE:
                title = f"AI Agents — {title}"
            for section, start_s, text in chunk_transcript(data["segments"]):
                points.append({
                    "payload": {
                        "course": course, "kind": "transcript", "week": week, "title": title,
                        "section": section, "text": text,
                        "url": f"{data['url']}&t={int(start_s)}s",
                    },
                    "_embed": f"{title} — {section}. {text}",
                })

    for f in sorted(config.AGENTS_BLOGS_TEXT_DIR.glob("*.txt")):
        raw = f.read_text()
        title, url, *rest = raw.split("\n", 2)
        body = rest[0] if rest else ""
        for i, text in enumerate(chunk_blog_text(body), start=1):
            points.append({
                "payload": {
                    "course": config.AGENTS_COURSE, "kind": "blog", "week": None,
                    "title": title, "section": f"part {i}", "text": text, "url": url,
                },
                "_embed": f"{title} — part {i}. {text}",
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
    print(f"{len(points)} chunks from lesson plans + recaps + transcripts + blogs; embedding…")
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
