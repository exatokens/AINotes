"""RAG core: embed queries, search Qdrant, and answer with the cluster LLM.

Uses plain HTTP (requests) against:
  * the SV Ray cluster text-embedding endpoint (all-MiniLM-L6-v2, 384-dim)
  * Qdrant's REST search API
  * the cluster's OpenAI-compatible chat endpoint (openai/gpt-oss-20b)
"""

import re

import requests

from . import config

COURSE_BLURB = """\
"Beyond RAG" is a five-week course on enterprise search and \
Retrieval-Augmented Generation:
  Week 1 - When Meaning Becomes Geometry (embeddings, attention, anisotropy)
  Week 2 - The Shape of a Decision (softmax, NLL, cross-entropy, contrastive learning)
  Week 3 - Measuring the Size of Thoughts (chunking)
  Week 4 - The Understudy (derivative artifacts, RAPTOR)
  Week 5 - When the Library Becomes a City (GraphRAG)\
"""

# Pass 0: turns the student's raw message into a clean retrieval query before
# it's ever embedded — fixes typos, drops filler, and (using the recent chat
# history) resolves pronouns/references from earlier turns ("it", "that
# equation") into the actual topic. This is "query transformation," which the
# course itself teaches — retrieval is only as good as the query you hand it.
REWRITE_SYSTEM_PROMPT = """\
Rewrite the student's latest message into a clean, well-formed search query \
for a retrieval system. Fix typos, drop filler words, and if the message \
refers back to something in the chat history (e.g. "it", "that", "the \
equation above"), resolve the reference using the history so the query \
stands alone. Preserve all technical terms and the original intent exactly \
— do not answer the question or add new topics.

Do not explain your reasoning. Respond with EXACTLY one line, in this form \
and nothing else:
QUERY: <the rewritten query>
"""

_QUERY_LINE = re.compile(r"QUERY:\s*(.+)", re.IGNORECASE)


def rewrite_query(question, history=None):
    """Clean up a raw user message into a standalone retrieval query.

    Parameters
    ----------
    question : str
        The student's raw message, possibly typo'd or context-dependent.
    history : list[dict] | None
        Prior turns, used only to resolve references like "it" or "that".

    Returns
    -------
    str
        The rewritten query, or the original question if rewriting fails.

    Notes
    -----
    gpt-oss-20b sometimes "thinks out loud" in the visible content before
    answering (unlike its hidden reasoning channel, this counts against
    max_tokens) — a tight token budget can cut it off mid-thought before it
    ever reaches the actual answer. We give it real room (300 tokens) and
    look for the "QUERY:" marker rather than trusting the whole response to
    be clean; if the marker never appears, we fall back to the response's
    last non-empty line, which is usually the answer after any preamble.
    """
    messages = [{"role": "system", "content": REWRITE_SYSTEM_PROMPT}]
    for turn in (history or [])[-2:]:
        if turn.get("role") in ("user", "assistant") and turn.get("content"):
            messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": question})
    raw, _ = _complete(messages, max_tokens=config.REWRITE_MAX_TOKENS, temperature=config.REWRITE_TEMPERATURE)

    m = _QUERY_LINE.search(raw)
    if m:
        return m.group(1).strip().strip('"').splitlines()[0].strip() or question
    lines = [l.strip().strip('"') for l in raw.splitlines() if l.strip()]
    return lines[-1] if lines else question


# Pass 1: a plain research/drafting pass. Grounding and completeness are all
# that matter here — a smaller open model reliably does this well, but (in
# testing) reliably ignores elaborate tone/structure instructions when it
# also has to juggle raw retrieved fragments at the same time. So tone is
# deliberately NOT this pass's job; see TEACH_SYSTEM_PROMPT below.
DRAFT_SYSTEM_PROMPT = f"""\
You are a research assistant for the "Beyond RAG" course.

{COURSE_BLURB}

The context passages given to you come from the actual lesson-plan PDFs,
recap summaries, and lecture-video transcripts for this course. Using ONLY
those passages, write as complete and accurate an answer as you can to the
student's question. Cite every fact inline as [n], matching the passage
number. Include any equations exactly as given in the passages, with correct
LaTeX. If the passages don't cover the question, say so plainly and suggest
which week likely does. Do not invent facts. Favor completeness and
correctness over brevity or tone — a later editing pass will make this
beginner-friendly.
"""

# Pass 2: takes pass 1's grounded draft and rewrites ONLY its presentation.
# Rewriting a single coherent draft into a teaching narrative is a much
# easier task for a 20B model to actually comply with than doing retrieval,
# synthesis, and tone all at once — this is why the split exists.
TEACH_SYSTEM_PROMPT = f"""\
You are a patient, encouraging teacher for the "Beyond RAG" course.

{COURSE_BLURB}

You will be given a technically-correct draft answer and the original
question. Your ONLY job is to rewrite the draft into a genuinely well-taught
explanation for a bright but new student — think a sharp 15-20 year old with
high-school math, not a colleague. Do not add facts beyond the draft. Keep
every [n] citation marker exactly where its claim appears (renumber only if
you reorder claims, keeping each marker attached to the same fact).

Structure the rewrite like this:
1. Start with one or two plain-English sentences giving the core intuition —
   zero jargon, zero equations. What is this idea *really* saying, in words
   a beginner already understands?
2. Build up gradually. Introduce each new term only when you need it, and
   define it in-line the first time it appears. Explain WHY the idea is
   needed before diving into HOW it works.
3. If an equation appears in the draft, never just drop it. First say in
   words what it computes, then show it, then walk through what each symbol
   means, then work through one tiny concrete numeric example by hand.
4. If the concept is a process, pipeline, or has clear stages/components,
   include one small mermaid diagram (```mermaid fences, flowchart LR/TD)
   with short labels — only when a diagram genuinely clarifies the structure,
   not as decoration.
5. Close with one sentence connecting it back to why this matters in the
   course's own story.

For math, use ONLY dollar-sign LaTeX delimiters: $...$ for inline math and
$$...$$ for display equations. Never use \\[...\\] or \\(...\\) delimiters.
Favor clarity over brevity — use as much space as the explanation genuinely
needs, but don't pad or repeat yourself.

Here is the tone and depth to match exactly (topic differs from any real
course question — this is a style guide only, do not reuse its content):

Q: "What is cosine similarity and why do we use it?"
A: "Imagine two arrows drawn from the same starting point — cosine
similarity just asks how much they point in the same direction, ignoring
how long each arrow is.

Formally, for two vectors $u$ and $v$:

$$\\text{{sim}}_{{\\cos}}(u, v) = \\frac{{u \\cdot v}}{{\\|u\\|\\,\\|v\\|}}$$

Here $u \\cdot v$ is the dot product — multiply matching coordinates and add
them up — and $\\|u\\|$ is the vector's length. Dividing by the two lengths
is what strips away magnitude and leaves only direction.

Concretely: if $u = [1, 0]$ and $v = [0, 1]$, the dot product is
$1 \\times 0 + 0 \\times 1 = 0$, so the similarity is $0$ — a right angle,
completely unrelated. If instead $v = [2, 0]$ (same direction as $u$, just
twice as long), the dot product is $2$, the lengths are $1$ and $2$, so the
similarity is $2 / (1 \\times 2) = 1$ — perfectly aligned, even though $v$ is
longer.

That is why retrieval systems use cosine instead of the raw dot product: a
long, wordy chunk that happens to share a topic with a short query should
still score as similar, and cosine ignores length so that's exactly what
happens."

Notice: an everyday-language hook first, terms defined as they appear, the
formula explained piece by piece, one small worked numeric example, and a
closing line tying it back to why it's useful. Match that shape and depth.
"""


def embed(texts):
    """Embed a list of strings with all-MiniLM-L6-v2 on the cluster.

    Parameters
    ----------
    texts : list[str]

    Returns
    -------
    list[list[float]]
        One 384-dim vector per input, in order.

    Raises
    ------
    requests.HTTPError
        If the embedding service returns a non-2xx status.
    """
    r = requests.post(
        config.EMBED_TEXT_URL,
        json={"model": config.EMBED_MODEL, "input": texts},
        timeout=30,
    )
    r.raise_for_status()
    data = sorted(r.json()["data"], key=lambda d: d["index"])
    return [d["embedding"] for d in data]


def search_pages(query, limit=config.RETRIEVAL_LIMIT_PAGES):
    """Semantic search over the authored textbook pages (sidebar search box).

    Parameters
    ----------
    query : str
        Natural-language question or search phrase.
    limit : int
        Max number of chunks to return.

    Returns
    -------
    list[dict]
        Hits with keys: page_id, title, section, text, score — best first.

    Raises
    ------
    requests.HTTPError
        If embedding or Qdrant search fails.
    """
    vec = embed([query])[0]
    r = requests.post(
        f"{config.QDRANT_URL}/collections/{config.COLLECTION_PAGES}/points/search",
        json={"vector": vec, "limit": limit, "with_payload": True},
        timeout=30,
    )
    r.raise_for_status()
    hits = []
    for h in r.json()["result"]:
        p = h["payload"]
        hits.append(
            {
                "page_id": p["page_id"],
                "title": p["title"],
                "section": p.get("section", ""),
                "text": p["text"],
                "score": round(h["score"], 4),
            }
        )
    return hits


def search_sources(query, limit=config.RETRIEVAL_LIMIT_SOURCES):
    """Semantic search over raw course material (lesson plans, recaps, video
    transcripts) — this is what grounds the RAG chat.

    Parameters
    ----------
    query : str
        The student's question.
    limit : int
        Max number of chunks to return.

    Returns
    -------
    list[dict]
        Hits with keys: kind, week, title, section, text, url, score.

    Raises
    ------
    requests.HTTPError
        If embedding or Qdrant search fails.
    """
    vec = embed([query])[0]
    r = requests.post(
        f"{config.QDRANT_URL}/collections/{config.COLLECTION_SOURCES}/points/search",
        json={"vector": vec, "limit": limit, "with_payload": True},
        timeout=30,
    )
    r.raise_for_status()
    hits = []
    for h in r.json()["result"]:
        p = h["payload"]
        hits.append(
            {
                "kind": p["kind"],
                "week": p["week"],
                "title": p["title"],
                "section": p.get("section", ""),
                "text": p["text"],
                "url": p.get("url"),
                "score": round(h["score"], 4),
            }
        )
    return hits


def chat(question, history=None, limit=config.RETRIEVAL_LIMIT_SOURCES):
    """Answer a question with retrieval-augmented generation.

    Parameters
    ----------
    question : str
        The student's question.
    history : list[dict] | None
        Prior turns as [{"role": "user"|"assistant", "content": str}, ...];
        only the last 6 turns are forwarded to the model.
    limit : int
        Number of context chunks to retrieve.

    Returns
    -------
    dict
        {"answer": str, "sources": list[dict], "search_query": str} where
        sources are the search hits (without full text) offered to the model,
        and search_query is the cleaned-up query actually used for retrieval
        (shown in the UI so a bad rewrite is visible, not silently wrong).
    """
    search_query = rewrite_query(question, history=history)
    hits = search_sources(search_query, limit=limit)
    context = "\n\n".join(
        f"[{i + 1}] (from “{h['title']}” — {h['section']})\n{h['text']}"
        for i, h in enumerate(hits)
    )

    draft_messages = [{"role": "system", "content": DRAFT_SYSTEM_PROMPT}]
    for turn in (history or [])[-6:]:
        if turn.get("role") in ("user", "assistant") and turn.get("content"):
            draft_messages.append({"role": turn["role"], "content": turn["content"]})
    draft_messages.append(
        {"role": "user", "content": f"Context passages:\n\n{context}\n\nQuestion: {question}"}
    )
    draft, _ = _complete(draft_messages, max_tokens=config.DRAFT_MAX_TOKENS, temperature=config.DRAFT_TEMPERATURE)

    teach_messages = [
        {"role": "system", "content": TEACH_SYSTEM_PROMPT},
        {"role": "user", "content": f"Question: {question}\n\nDraft answer to rewrite:\n\n{draft}"},
    ]
    answer, teach_finish = _complete(
        teach_messages, max_tokens=config.TEACH_MAX_TOKENS, temperature=config.TEACH_TEMPERATURE
    )
    if teach_finish == "length":
        # Ran out of budget mid-generation — gpt-oss-20b sometimes "thinks
        # out loud" in visible content before answering, and a long or
        # citation-heavy draft can push that past max_tokens before the
        # actual rewritten answer ever appears. The draft is always a
        # complete, correct (if less pedagogically polished) answer, so
        # show that rather than a truncated ramble.
        answer = draft

    for h in hits:
        h.pop("text", None)
    return {"answer": answer, "sources": hits, "search_query": search_query}


def _complete(messages, max_tokens, temperature):
    """One call to the cluster's chat endpoint; returns (text, finish_reason).

    Parameters
    ----------
    messages : list[dict]
        OpenAI-style chat messages.
    max_tokens : int
    temperature : float

    Returns
    -------
    tuple[str, str]
        (reply text, finish_reason). Text falls back to the reasoning
        channel if gpt-oss-20b's content came back empty — it spends tokens
        on a hidden reasoning channel and can run out of budget before
        writing content. finish_reason is "length" when the model got cut
        off mid-generation (sometimes mid "thinking out loud," before ever
        reaching its actual answer) — callers that can fall back to a
        simpler-but-complete alternative should check for that.
    """
    r = requests.post(
        f"{config.CHAT_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {config.CHAT_API_KEY}"},
        json={
            "model": config.CHAT_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
        timeout=120,
    )
    r.raise_for_status()
    choice = r.json()["choices"][0]
    msg = choice["message"]
    text = (msg.get("content") or "").strip()
    if not text:
        text = (msg.get("reasoning_content") or "").strip() or "(no answer produced — try again)"
    return text, choice.get("finish_reason")
