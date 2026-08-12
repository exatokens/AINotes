---
id: w4-09-qa-pairs
title: "QA Pairs: Planting Query-Shaped Objects"
week: 4
topic: "Act II: The Derivative Artifacts — and the Proof"
order: 9
summary: Generating candidate questions per chunk turns retrieval into a same-genre match, question against question, instead of a cross-genre one, and a pointer back to the source keeps the artifact honest.
---

Of all the artifacts, the question–answer pair is the most mischievous — and the most direct attack on the costume problem.

The idea is simple: given a chunk, have an LLM generate the plausible questions that chunk could answer, paired with their answers, and embed both.

## Why it works

Retrieval is a matching problem, and matching is easiest when both sides speak the same dialect. A dense retriever compares a query embedding with document embeddings. Ordinarily this is a cross-genre comparison — a question measured against declarative prose. But if the indexed object was itself derived from a question, the comparison becomes same-genre: question against question. You have planted a query-shaped decoy that the retriever should find.

## Generating a good set

A good QA pipeline generates three to eight questions per chunk, varied:

- **in specificity** — from "what does this section discuss?" to "what learning rate did experiment 3 use?"
- **in formulation** — keyword-ish to natural-language
- **in abstraction** — factual to interpretive

Each pair stores a pointer back to its source chunk, because at generation time the model must see the chunk, not the synthetic question.

```python
# QA-pair generation, with the pointer that keeps generation honest
def generate_qa_pairs(chunk_id, chunk_text, llm_fn, n=(3, 8)):
    prompt = f"""Generate {n[0]}-{n[1]} question-answer pairs a user might ask
that this passage answers. Vary specificity, phrasing, and abstraction.

Passage:
{chunk_text}"""
    pairs = llm_fn(prompt)  # -> [{"question": ..., "answer": ...}, ...]
    for p in pairs:
        p["source_chunk_id"] = chunk_id   # never sever this pointer
    return pairs
```

## The failure mode to watch for

A careless synthetic question can mislead the retriever, promising an answer the source does not actually contain. Generation hygiene matters: read the artifacts, not just the aggregate metrics. Find the synthetic question whose answer the source does not actually contain — it is invisible in a Recall@k table and obvious on the page.
