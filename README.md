# AINotes

A digital textbook + RAG chat for the "Beyond RAG" course (Enterprise Search &
Retrieval-Augmented Generation). Read hand-authored concept pages for all 5+
weeks in a textbook-style reader (left: topic tree, center: page, right:
chat), or ask the chat anything — it retrieves from the actual lesson-plan
PDFs, recap summaries, lecture-video transcripts, and a practical lab corpus,
then answers with citations and implementation-focused guidance.

## Quickstart

Use the project Python environment:

```bash
cd <repo-root>
python -m app.server
```

Open:

```text
http://localhost:8014
```

Or, for auto-reload on code changes while developing:

```bash
cd <repo-root>
python -m uvicorn app.server:app --port 8014 --reload
```

The port defaults to `8014` (`app/config.py: SERVER_PORT`, override with the
`PORT` env var).

This assumes the SV Ray cluster (embeddings + `gpt-oss-20b` chat) and Qdrant
are already reachable at the URLs in `app/config.py` — see **Configuration**
below if you're pointing at different infrastructure. The content itself
(pages, indexes, transcripts, lab chunks) is built from the source folders and
re-indexed when you run the ingest scripts.

## Architecture, in one paragraph

Three Qdrant collections now support different jobs. `siva_beyond_rag_pages`
holds the hand-authored concept pages (`content/pages/*.md`) and backs the
sidebar's "search the textbook" box. `siva_beyond_rag_sources` holds raw
chunked lesson-plan PDFs, recap PDFs, and YouTube transcripts, and is what
actually grounds the chat in the lecture material. `siva_beyond_rag_labs`
holds practical lab docs and implementation examples from the separate
`$RAG_LABS_ROOT` (default `../rag-labs`) codebase, enabling the chat to answer
"how do I build this in production?" style questions. The chat pipeline itself
is still three sequential LLM calls: **rewrite** → **draft** → **teach**.
The difference is that retrieval now blends the lecture corpus with the lab
pattern corpus, using a slightly stronger preference for lab results when the
question is implementation-oriented.

## Rebuild the data sources

Everything below reads its tunable values from **`app/config.py`** — the one
file to check or edit when a new source path or collection needs adjusting.

### Rebuild the lesson-plan / recap / transcript corpus

```bash
cd <repo-root>
python -m ingest.extract_pdfs
python -m ingest.fetch_transcripts
python -m ingest.index_sources
```

### Rebuild the lab corpus

```bash
cd <repo-root>
python -m ingest.index_labs
```

This indexes the practical lab material under the collection named
`siva_beyond_rag_labs` using the repo at
`$RAG_LABS_ROOT` (default `../rag-labs`).

### Rebuild the textbook page search index

```bash
cd <repo-root>
python -m ingest.build_tree
python -m ingest.index_qdrant
```

### Full rebuild from scratch

```bash
cd <repo-root>
python -m ingest.extract_pdfs
python -m ingest.fetch_transcripts
python -m ingest.index_sources
python -m ingest.build_tree
python -m ingest.index_qdrant
python -m ingest.index_labs
```

### Sanity check for lab retrieval

```bash
cd <repo-root>
python - <<'PY'
from app import rag
for q in [
    'How do I build a production retrieval funnel step by step?',
    'What is the best way to test a RAG pipeline?',
    'How do I design a guardrail for prompt injection?',
]:
    print('\nQUERY:', q)
    for h in rag.search_labs(q, limit=3):
        print('-', h['title'], '|', h['kind'], '|', h['section'])
PY
```

## Configuration

All of it lives in `app/config.py`: cluster endpoints, Qdrant collection
names, content paths, the labs root path, chunk sizes, equation-citation
matching thresholds, and the three chat passes' token/temperature settings.
Endpoints can be overridden with env vars (`LLM_BASE_URL`, `LLM_API_KEY`,
`QDRANT_URL`, `PORT`, `RAG_LABS_ROOT`, ...) without touching code.

## Project layout

```
app/
  server.py          FastAPI app — the whole HTTP API + static file serving
  rag.py             retrieval + the 3-pass chat pipeline
  content_store.py   loads content/pages/*.md and content/tree.json
  config.py          every tunable value, in one place
  static/            reader UI (index.html, app.js, styles.css, vendored JS libs)
ingest/
  extract_pdfs.py      lesson_plans/*.pdf, recap/*.pdf, agents_notes/*.pdf
                          -> content/sources/{lesson_plans,recap,agents_recap}/*.txt
  fetch_transcripts.py youtube_video_links.yaml, agents_notes/all_weeks_classes_theory
                          -> content/sources/{transcripts,agents_transcripts}/*.json
  fetch_blogs.py        config.AGENTS_BLOG_SOURCES  -> content/sources/agents_blogs/*.txt
  index_sources.py     content/sources/**           -> Qdrant (siva_beyond_rag_sources) — grounds chat
                          (both courses, tagged by "course" field)
  index_labs.py        rag-labs -> Qdrant (siva_beyond_rag_labs) — practical patterns
  build_tree.py        content/pages/*.md           -> content/tree.json — sidebar nav (courses -> weeks -> topics)
  index_qdrant.py      content/pages/*.md           -> Qdrant (siva_beyond_rag_pages) — page search
  link_equations.py    content/pages/*.md + sources -> content/equation_citations.json
content/
  pages/               hand-authored concept pages: w{N}-*.md (Beyond RAG), a{N}-*.md (AI Agents Bootcamp)
  sources/             extracted/derived text — safe to delete and regenerate
  tree.json, equation_citations.json   generated — safe to delete and regenerate
lesson_plans/, recap/  the original Beyond RAG course PDFs
agents_notes/          the original AI Agents Bootcamp weekly-summary PDFs + all_weeks_classes_theory (video/blog links)
youtube_video_links.yaml  Beyond RAG lecture video URLs, grouped by week
```

## Why the lab layer matters

The lecture material tells you what the concept is. The recap material helps
refresh it. The lab material tells you how to actually build, evaluate,
measure, and deploy the idea in a real production system. That is the missing
piece for implementation-style questions, and it's why the repo now keeps a
separate lab corpus in Qdrant rather than mixing it into the lecture sources.

## Book-style chapter template for the main reader

The main page experience should feel like a real textbook, not a note card.
Each concept page should follow the same learning arc:

1. Core intuition — explain in plain English, no jargon first.
2. Why it matters — what problem this solves and when it breaks.
3. Instructor framing — how the lesson fits the course story.
4. Worked example — a concrete numeric or conceptual example.
5. Math explained step by step — formula, each symbol, one small derivation.
6. Practical pattern — how to build it in code or production.
7. Common traps — what usually causes confusion.
8. Takeaways — one crisp summary list.

Use this structure in new pages:

```markdown
---
id: w7-01-example-page
title: "A Concept, Taught the Way a Good Book Teaches It"
week: 7
topic: "A Good Topic Name"
order: 1
summary: A short one-sentence explanation of what the learner will understand.
---

## Core intuition

Explain the idea in plain English first.

## Why it matters

What problem it solves and why the reader should care.

## Instructor framing

Connect it back to the course story and the previous ideas.

## Worked example

Give a small concrete example, a numeric example, or a tiny scenario.

## Math explained step by step

State the formula, explain each symbol, and walk through the logic.

## Practical pattern

Show the production pattern, implementation notes, or lab reference.

## Common traps

List the mistakes students typically make.

## Takeaways

- One key insight
- One method to remember
- One practical action
```

This gives the main page a deeper learning arc while keeping the chat layer for
interactive explanations and retrieval.

## Editorial tone and structure policy

This project is intentionally written like a real book, not like a notes dump or
an AI-generated summary. The aim is to teach the reader how to think, not merely
what to memorize.

### Tone

The writing should feel:

- clear and direct, like a serious textbook rather than a social-media post
- precise without being pompous or obscure
- concrete and practical, with examples before abstractions become too dense
- disciplined and skeptical, with explicit assumptions and trade-offs
- calm and explanatory, not hype-heavy or promotional

The style is closest to a rigorous, readable investment-textbook tradition:
plain English first, then structure, then math, then operational guidance. In
other words, the reader should always understand the problem before the formula,
and the formula before the implementation.

### Structural principles

Every chapter should teach in the same sequence:

1. Core intuition — explain the idea in ordinary language.
2. Why it matters — connect it to failure modes, trade-offs, or practical pain.
3. Instructor framing — place it in the larger story of the course.
4. Worked example — show the idea with a concrete scenario or numeric case.
5. Math explained step by step — define the formula and explain each symbol.
6. Practical pattern — show how engineers actually use it in production.
7. Common traps — name the mistakes readers typically make.
8. Takeaways — end with a crisp summary of the lesson.

This makes the main page feel like a learning arc, not a collection of fragments.

### What we considered while rewriting the book

The rewrite was designed around a few concrete goals:

- theory first, but grounded in examples and lived intuition
- practical engineering guidance, not just abstract concepts
- a clear distinction between retrieval, ranking, and generation
- explanations that can be followed by a learner without needing a lecture
- math that is brief, readable, and useful rather than ornamental
- chapter continuity so the reader can feel the course unfolding over time
- examples that connect to real pain points in enterprise search, RAG, and guardrails
- a balance between conceptual clarity and operational realism

The content also tries to keep both voices in view:

- Meera — the student who wants the idea explained simply and correctly
- Ravi — the builder who wants the trade-offs, the implementation pattern, and the practical payoff

That gives the book a more complete teaching shape than a single abstract tone
could provide. The end result is a chapter sequence that reads as a coherent
textbook and still remains useful for a production practitioner.

## Adding new data

Everything below reads its tunable values (chunk sizes, model names, score
thresholds, LLM params) from **`app/config.py`** — that's the one file to
check or edit if something needs adjusting; no ingest script defines its own
constants.

This reader now serves **two courses** that share one Qdrant collection per
layer (pages, sources): `beyond_rag` and `ai_agents`. Both reuse Week 1-13
numbering, so every page and every indexed chunk carries a `course` field
(`config.BEYOND_RAG_COURSE` / `config.AGENTS_COURSE`) to keep citations from
colliding — see `content_store.py`'s module docstring and
`ingest/index_sources.py`'s module docstring for the full data-flow. The
sections below are written for Beyond RAG; the "AI Agents Bootcamp" section
right after covers the second course's equivalents.

### A new lesson-plan or recap PDF

```bash
cp your-file.pdf lesson_plans/            # or recap/
python -m ingest.extract_pdfs             # extracts text, skips files already up to date
python -m ingest.index_sources            # re-chunks + re-embeds + re-indexes everything
```

That's it for a normally-named file (anything with `week`+a digit in the
name, e.g. `week-6-summer-lesson-plan.pdf`) — week number and title are
auto-inferred. If the filename has no week number in it, or you want a nicer
display title, add one line to `app/config.py`:

```python
DOC_WEEK_OVERRIDES  = {"my-weird-filename": 6}
DOC_TITLE_OVERRIDES = {"my-weird-filename": "Week 6 Lesson Plan — My Title"}
```

### A new YouTube lecture video

Add the URL to `youtube_video_links.yaml` under a `Week_N_Main_class` or
`Week_N_Summary_class` key (week number and Main/Summary are parsed from that
key name), then:

```bash
python -m ingest.fetch_transcripts        # downloads transcripts, skips ones already cached
python -m ingest.index_sources            # re-index (picks up new transcripts automatically)
```

### A new authored concept/reader page

Create `content/pages/w{N}-{NN}-{slug}.md` with the same flat frontmatter as
any existing page (copy one as a template — `id`, `title`, `week`, `topic`,
`order`, `summary`, then the markdown body). Then:

```bash
python -m ingest.build_tree               # rebuilds content/tree.json (the sidebar nav)
python -m ingest.index_qdrant             # re-indexes pages for the sidebar search box
python -m ingest.link_equations           # (re)matches every $$...$$ equation to a source citation
```

### AI Agents Bootcamp: a new weekly-summary PDF, video, or blog post

```bash
cp your-file.pdf agents_notes/                        # weekly-summary PDF
python -m ingest.extract_pdfs                         # -> content/sources/agents_recap/*.txt
python -m ingest.index_sources
```

Filenames in `agents_notes/` are unusually inconsistent, so week numbers are
**not** regex-inferred — every file's week is listed explicitly in
`config.AGENTS_DOC_WEEK_OVERRIDES`. Add an entry there for a new PDF (keyed
by the filename stem: lowercased, spaces replaced with `_`).

For a new lecture video, add the URL to
`agents_notes/all_weeks_classes_theory` under a `weekN:` line (that file is a
free-form text dump, not YAML — see `ingest/fetch_transcripts.py`'s
`parse_agents_links()` for the exact format it expects), then:

```bash
python -m ingest.fetch_transcripts        # -> content/sources/agents_transcripts/*.json
python -m ingest.index_sources
```

For a new blog post, add an entry to `config.AGENTS_BLOG_SOURCES` (slug,
title, url), then:

```bash
python -m ingest.fetch_blogs              # -> content/sources/agents_blogs/*.txt
python -m ingest.index_sources
```

A new authored AI Agents Bootcamp page works exactly like a Beyond RAG page
(see above), except: use the `a{N}-{NN}-{slug}.md` filename prefix instead of
`w{N}-{NN}-{slug}.md` (avoids colliding with Beyond RAG's files), and add
`course: ai_agents` to the frontmatter. Then run the same
`build_tree` / `index_qdrant` / `link_equations` steps.

### Rebuild everything from scratch

```bash
python -m ingest.extract_pdfs
python -m ingest.fetch_transcripts
python -m ingest.fetch_blogs
python -m ingest.index_sources
python -m ingest.build_tree
python -m ingest.index_qdrant
python -m ingest.link_equations
```

Each step is idempotent / recreates its own output, so this is always safe
to re-run in full.

## Configuration


All of it lives in `app/config.py`: cluster endpoints, Qdrant collection
names, content paths, chunk sizes, equation-citation matching thresholds, and
the three chat passes' token/temperature settings. Endpoints can be
overridden with env vars (`LLM_BASE_URL`, `LLM_API_KEY`, `QDRANT_URL`, `PORT`,
...) without touching code — see the top of that file for the full list.

## Project layout

```
app/
  server.py          FastAPI app — the whole HTTP API + static file serving
  rag.py              retrieval + the 3-pass chat pipeline
  content_store.py    loads content/pages/*.md and content/tree.json
  config.py           every tunable value, in one place
  static/              reader UI (index.html, app.js, styles.css, vendored JS libs)
ingest/
  extract_pdfs.py      lesson_plans/*.pdf, recap/*.pdf  ->  content/sources/{lesson_plans,recap}/*.txt
  fetch_transcripts.py youtube_video_links.yaml         ->  content/sources/transcripts/*.json
  index_sources.py     content/sources/**               ->  Qdrant (siva_beyond_rag_sources) — grounds chat
  build_tree.py        content/pages/*.md               ->  content/tree.json — sidebar nav
  index_qdrant.py       content/pages/*.md              ->  Qdrant (siva_beyond_rag_pages) — page search
  link_equations.py     content/pages/*.md + sources     ->  content/equation_citations.json
content/
  pages/               hand-authored concept pages (the textbook itself)
  sources/             extracted/derived text — safe to delete and regenerate
  tree.json, equation_citations.json   generated — safe to delete and regenerate
lesson_plans/, recap/  the original course PDFs
youtube_video_links.yaml  lecture video URLs, grouped by week
```
