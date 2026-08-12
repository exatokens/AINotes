"""Central configuration for the SupportVector NoteAI app.

Every tunable value lives here — service endpoints, content paths, chunking
sizes, RAG generation parameters, and the small override tables used when
auto-discovering new source documents. Nothing outside this file should
define its own constants; ingest scripts and app modules just import from
here. Endpoints can be overridden with environment variables of the same
name (handy for pointing at a different cluster without editing code).
"""

import os
from pathlib import Path

# ── Cluster endpoints (see dealdeal/test_models.py for how these were found) ─
BASE_URL = os.getenv("SV_BASE_URL", "http://10.0.10.51:8000")
EMBED_TEXT_URL = f"{BASE_URL}/embed-text/v1/embeddings"
CHAT_BASE_URL = f"{BASE_URL}/v1"
CHAT_API_KEY = os.getenv("SV_API_KEY", "sv-openai-api-key")

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # 384-dim
CHAT_MODEL = "openai/gpt-oss-20b"

# ── Qdrant ───────────────────────────────────────────────────────────────────
# Two collections, two jobs:
#   COLLECTION_PAGES   - the authored digital-textbook pages (content/pages/*.md),
#                        used only for the sidebar "search the textbook" box.
#   COLLECTION_SOURCES - raw chunked lesson plans, recaps, and video transcripts,
#                        used to ground the RAG chat in the actual course material.
QDRANT_URL = os.getenv("QDRANT_URL", "http://10.0.10.65:6333")
COLLECTION_PAGES = os.getenv("QDRANT_COLLECTION_PAGES", "siva_beyond_rag_pages")
COLLECTION_SOURCES = os.getenv("QDRANT_COLLECTION_SOURCES", "siva_beyond_rag_sources")
EMBED_DIM = 384

# ── Server ───────────────────────────────────────────────────────────────────
SERVER_PORT = int(os.getenv("PORT", "8014"))

# ── Content paths ────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "app" / "static"

# Raw inputs you drop new material into:
LESSON_PLANS_PDF_DIR = ROOT / "lesson_plans"      # *.pdf
RECAP_PDF_DIR = ROOT / "recap"                     # *.pdf
YOUTUBE_LINKS_FILE = ROOT / "youtube_video_links.yaml"

# Extracted/derived data (safe to delete and regenerate — see README):
SOURCES_DIR = ROOT / "content" / "sources"
LESSON_PLANS_TEXT_DIR = SOURCES_DIR / "lesson_plans"   # extract_pdfs.py output
RECAP_TEXT_DIR = SOURCES_DIR / "recap"                 # extract_pdfs.py output
TRANSCRIPTS_DIR = SOURCES_DIR / "transcripts"          # fetch_transcripts.py output

# Authored content (hand-written, not regenerated):
PAGES_DIR = ROOT / "content" / "pages"
TREE_FILE = ROOT / "content" / "tree.json"                       # build_tree.py output
EQUATION_CITATIONS_FILE = ROOT / "content" / "equation_citations.json"  # link_equations.py output

# ── Auto-discovery overrides for lesson-plan / recap PDFs ──────────────────
# index_sources.py auto-infers each PDF's week (by regex on the filename,
# e.g. "week-3-summer-lesson-plan" -> 3) and a plain title ("Week 3 Lesson
# Plan"). Add an entry here ONLY when a filename doesn't contain "weekN" (the
# regex can't find a week) or when you want a nicer display title than the
# generic default. Keyed by filename stem (no extension).
DOC_WEEK_OVERRIDES = {
    "the-shape-of-a-decision-portal-skeleton": 2,  # no digit in the filename
}
DOC_TITLE_OVERRIDES = {
    "week-1-summer-lesson-plan": "Week 1 Lesson Plan — When Meaning Becomes Geometry",
    "week-2-summer-lesson-plan": "Week 2 Lesson Plan — The Shape of a Decision",
    "week-3-summer-lesson-plan": "Week 3 Lesson Plan — Measuring the Size of Thoughts",
    "week-4-summer-lesson-plan": "Week 4 Lesson Plan — The Understudy",
    "week-5-summer-lesson-plan": "Week 5 Lesson Plan — When the Library Becomes a City",
    "the-shape-of-a-decision-portal-skeleton": "Week 2 Portal Map (formula skeleton)",
}

# ── Chunking (ingest/index_sources.py, ingest/index_qdrant.py) ─────────────
SOURCE_CHUNK_CHARS = 1800       # lesson-plan / recap text chunks
TRANSCRIPT_CHUNK_CHARS = 1200   # transcript chunks (grouped by ~this many chars)
PAGE_CHUNK_CHARS = 1800         # authored concept-page chunks (page-search index)

# ── Equation-citation matching (ingest/link_equations.py) ──────────────────
EQUATION_CITATION_CONTEXT_CHARS = 350     # prose window before an equation, used as the search query
EQUATION_CITATION_MIN_SCORE = 0.35        # below this, show no citation rather than a bad guess
EQUATION_CITATION_TRANSCRIPT_MARGIN = 0.05  # prefer a clickable video within this margin of the top hit

# ── RAG generation (app/rag.py) ─────────────────────────────────────────────
# Three sequential LLM calls per chat turn — see rag.py's module docstring
# for why the pipeline is split this way.
RETRIEVAL_LIMIT_SOURCES = 6   # chunks retrieved to ground the chat answer
RETRIEVAL_LIMIT_PAGES = 8     # chunks retrieved for the sidebar page-search box

REWRITE_MAX_TOKENS = 300
REWRITE_TEMPERATURE = 0.0
DRAFT_MAX_TOKENS = 1400
DRAFT_TEMPERATURE = 0.2
# generous headroom: gpt-oss-20b's hidden "thinking out loud" in visible
# content also counts against this budget, and a long/citation-heavy draft
# can need real room before it reaches the actual rewritten answer — see
# chat()'s finish_reason=="length" fallback in rag.py for the safety net.
TEACH_MAX_TOKENS = 2400
TEACH_TEMPERATURE = 0.5
