# SupportVector NoteAI

A digital textbook + RAG chat for the "Beyond RAG" course (Enterprise Search &
Retrieval-Augmented Generation). Read hand-authored concept pages for all 5
weeks in a textbook-style reader (left: topic tree, center: page, right:
chat), or ask the chat anything — it retrieves from the actual lesson-plan
PDFs, recap summaries, and lecture-video transcripts and answers with
citations (clickable video timestamps where available).

## Quickstart

```bash
pip install -r requirements.txt
python -m app.server                 # http://localhost:8014
```

Or, for auto-reload on code changes while developing:

```bash
uvicorn app.server:app --port 8014 --reload
```

The port defaults to `8014` (`app/config.py: SERVER_PORT`, override with the
`PORT` env var).

This assumes the SV Ray cluster (embeddings + `gpt-oss-20b` chat) and Qdrant
are already reachable at the URLs in `app/config.py` — see **Configuration**
below if you're pointing at different infrastructure. The content itself
(pages, indexes, transcripts) is already built and checked into `content/`,
so a fresh clone can just run the server — you only need the ingest steps
below when *adding new material*.

## Architecture, in one paragraph

Two Qdrant collections do two different jobs. `siva_beyond_rag_pages` holds
the hand-authored concept pages (`content/pages/*.md`) and backs only the
sidebar's "search the textbook" box, which jumps to a reader page.
`siva_beyond_rag_sources` holds raw chunked lesson-plan PDFs, recap PDFs, and
YouTube transcripts, and is what actually grounds the chat — so chat answers
cite the real course material (with clickable video timestamps), not my
paraphrase of it. The chat pipeline itself is three sequential LLM calls:
**rewrite** (clean up typos/pronouns in the question before embedding it) →
**draft** (grounded, cited answer from retrieved passages) → **teach**
(rewrite the draft into an actual taught explanation — intuition first,
worked numeric examples, diagrams). See the docstrings in `app/rag.py` for
why it's split this way.

## Adding new data

Everything below reads its tunable values (chunk sizes, model names, score
thresholds, LLM params) from **`app/config.py`** — that's the one file to
check or edit if something needs adjusting; no ingest script defines its own
constants.

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

### Rebuild everything from scratch

```bash
python -m ingest.extract_pdfs
python -m ingest.fetch_transcripts
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
overridden with env vars (`SV_BASE_URL`, `SV_API_KEY`, `QDRANT_URL`, `PORT`,
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
