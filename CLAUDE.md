# Handoff for Claude

## Project goal
This repo is a digital textbook + RAG chat for the "Beyond RAG" course. The app combines:

- a hand-authored textbook experience in `content/pages/*.md`
- a searchable course index and sidebar navigation via `content/tree.json`
- a Qdrant-backed retrieval layer for lecture material, recap material, and lab patterns
- an interactive reader interface served by the FastAPI app in `app/server.py`

The design is intentionally different from a generic note app: the main reader should teach like a book, while the chat acts as a retrieval-augmented teaching assistant.

---

## What we have already done

### 1. Rebuilt the project around a textbook model
We shifted the content from vague notes into a more coherent, book-like teaching flow.

Each chapter follows a consistent structure:

1. Core intuition
2. Why it matters
3. Instructor framing
4. Worked example
5. Math explained step by step
6. Practical pattern
7. Common traps
8. Takeaways

This pattern is now reflected across the main content pages, so the reader gets a learning arc instead of isolated fragments.

### 2. Reworked the content voice and pedagogy
The writing now emphasizes:

- plain-English intuition before formal math
- concrete examples before abstract exposition
- practical engineering guidance
- explicit trade-offs and failure modes
- a clear teacher/learner flow rather than a summary dump

The project intentionally aims to feel like a serious textbook, not a notes page or lightweight AI summary.

### 3. Organized and documented the repo workflow
The repo now has clearer operational guidance in [README.md](README.md), including:

- how to run the app
- how the app architecture is structured
- how to rebuild the sources and indexes
- how to reindex the textbook pages and labs
- how to add new content and new lecture PDFs/videos
- how the lab corpus differs from the lecture corpus

### 4. Kept the technical app structure intact
The core stack remains:

- FastAPI app in `app/server.py`
- retrieval/chat logic in `app/rag.py`
- content loading in `app/content_store.py`
- config in `app/config.py`
- static frontend in `app/static/`

The app continues to serve:

- the main textbook reader
- left-side chapter navigation
- chat with citation-grounded responses
- page search over the authored textbook
- semantic retrieval over source and lab corpora

### 5. Validated the content and app health
We ran validation checks successfully after the latest editorial pass.

Commands used:

```bash
cd <root-path>
<venv>/bin/python - <<'PY'
from pathlib import Path
required=['## Core intuition','## Why it matters','## Instructor framing','## Worked example','## Math explained step by step','## Practical pattern']
missing=[]
for f in sorted(Path('content/pages').glob('w2-0*.md')):
    txt=f.read_text(errors='ignore')
    missing_sections=[sec for sec in required if sec not in txt]
    if missing_sections:
        missing.append((f.name, missing_sections))
print('missing_in_w2=', len(missing))
for name, secs in missing[:10]:
    print(name, '->', secs)
PY
node --check app/static/app.js && <venv>/bin/python -m py_compile app/*.py ingest/*.py
```

Observed output:

- `missing_in_w2= 0`
- `node --check app/static/app.js` passed
- `python -m py_compile app/*.py ingest/*.py` passed

This is the current evidence that the app and the chapter structure are still valid after the major book polish pass.

---

## Current repo state

### Main content source
The main textbook pages live under:

- `content/pages/`

These pages are the core reading experience and should be treated as the primary learning content.

### Generated data
The repo also generates and maintains:

- `content/tree.json`
- `content/equation_citations.json`
- source and transcript extracted text under `content/sources/`

These are derived artifacts and can be regenerated through the ingest scripts.

### Retrieval corpus split
The system is built around three retrieval collections:

- textbook pages collection for the sidebar search / page lookup
- lecture-source collection for course material and transcripts
- lab corpus for implementation guidance and production patterns

This separation is important: the chat is stronger when the lecture theory and practical implementation patterns are kept distinct.

---

## How to run the app

From the repo root:

```bash
cd <root-path>
<venv>/bin/python -m app.server
```

Then open:

```text
http://localhost:8014
```

Optional reload mode during development:

```bash
cd <root-path>
<venv>/bin/python -m uvicorn app.server:app --port 8014 --reload
```

---

## Rebuild workflow

The repo has a practical rebuild path for all source data:

```bash
cd <root-path>
<venv>/bin/python -m ingest.extract_pdfs
<venv>/bin/python -m ingest.fetch_transcripts
<venv>/bin/python -m ingest.index_sources
<venv>/bin/python -m ingest.build_tree
<venv>/bin/python -m ingest.index_qdrant
<venv>/bin/python -m ingest.index_labs
```

The important idea is that the content pages, the extracted corpora, and the vector indexes are treated as separate layers. The reader and the chat are meant to work together, not as one flat blob of text.

---

## Important design decisions

### Textbook first, chat second
The app is not only a chat UI. The chapter reader is central. The chat is a support layer for follow-up questions and retrieval, not a replacement for the learning material.

### Retrieval grounded in real course artifacts
The material is not being answered from generic model memory alone. The app is designed to ground responses in:

- course PDFs
- recap documents
- transcript data
- practical lab patterns
- hand-authored textbook pages

### Teaching quality over raw AI output
The editorial direction is to explain the idea, then show the math, then show the operational pattern. This is a better fit for a learning product than a generic retrieval answer.

---

## What Claude should focus on next

If Claude continues from here, the best next moves are:

1. Continue the book-polish pass for the remaining weeks and maintain the same teaching template.
2. Review the remaining chapter files for consistency in tone, examples, and structure.
3. Check whether the app title/branding is fully aligned with the final product name.
4. Improve the reader experience if any chapters are still vague or too terse.
5. Continue to keep the repo operational, with README and build flow in sync with any content changes.

---

## Final status
The repo is in a stable state for continued content refinement and app work. The chapter structure has been tightened significantly, the documentation has been refreshed, and the project remains valid under the checks we ran.

This is the current handoff point: the system is working as a book-like learning interface, and the next phase is refinement rather than architectural rework.
