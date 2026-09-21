"""FastAPI server for AINotes.

Serves the single-page reader UI plus a small JSON API:

  GET  /api/tree        -> topic tree for the left navigation
  GET  /api/page/{id}   -> one concept page (markdown + metadata + equation citations)
  GET  /api/search?q=   -> semantic search hits over the textbook
  POST /api/chat        -> RAG answer with cited sources

Run with either:
  python -m app.server                              (uses config.SERVER_PORT, no auto-reload)
  uvicorn app.server:app --port 8014 --reload        (auto-reloads on code changes; see README)
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config, content_store, rag

app = FastAPI(title="AINotes")


class ChatRequest(BaseModel):
    """Body for POST /api/chat.

    Attributes
    ----------
    question : str
        The student's question.
    history : list[dict]
        Prior chat turns, each {"role": "user"|"assistant", "content": str}.
    """

    question: str
    history: list[dict] = []


@app.get("/api/tree")
def tree():
    """Return the topic tree (weeks -> topics -> concepts) for the sidebar."""
    return content_store.get_tree()


@app.get("/api/page/{page_id}")
def page(page_id: str):
    """Return one concept page: metadata, markdown body, and per-equation
    source citations (index-aligned with the page's $$...$$ blocks)."""
    p = content_store.get_page(page_id)
    if p is None:
        raise HTTPException(404, f"unknown page: {page_id}")
    p = dict(p)
    p["equation_citations"] = content_store.get_equation_citations(page_id)
    return p


@app.get("/api/search")
def api_search(q: str, limit: int = config.RETRIEVAL_LIMIT_PAGES):
    """Semantic search over the authored textbook pages; returns scored hits."""
    try:
        return {"hits": rag.search_pages(q, limit=limit)}
    except Exception as e:
        raise HTTPException(502, f"search backend error: {e}")


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    """RAG chat: retrieve top chunks, answer with the cluster LLM, cite sources."""
    if not req.question.strip():
        raise HTTPException(400, "empty question")
    try:
        return rag.chat(req.question, history=req.history)
    except Exception as e:
        raise HTTPException(502, f"chat backend error: {e}")


@app.get("/")
def index():
    """Serve the single-page reader UI."""
    return FileResponse(config.STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.server:app", host="0.0.0.0", port=config.SERVER_PORT)
