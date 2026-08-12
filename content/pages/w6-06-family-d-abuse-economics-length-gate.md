---
id: w6-06-family-d-abuse-economics-length-gate
title: "Family D — Abuse, Economics, and the Cheapest Structural Gate"
week: 6
topic: "Act I: The Gatehouse — Keeping Bad Questions Out"
order: 6
summary: The last request-side family needs no forbidden word at all — it abuses the system by using it too much, spending its wallet, or exploiting its credulity — and one comparison operator, the length cap, retires most of it before a single classifier runs.
---

Not every threat needs a bad word. Some threats just need volume, or a sentence that quietly assumes something false.

## Rate limiting and the token bomb

The cheapest member of Family D is **rate limiting** — the bouncer who counts heads before anyone checks IDs. It operates on metadata, not content, and costs a counter lookup: cap queries per user, per session, per IP, and globally, and return a clean `429` with `Retry-After` rather than silently dropping the request. A knowledge worker asks a handful of questions a minute; fifty a minute is not research, it is automation.

Its economic sibling counts tokens, because the distinctive LLM-era abuse is the **token bomb** — one request engineered to be catastrophically expensive to serve, what the industry honestly calls **denial of wallet**.

## The Trojan paragraph, and why length is its antidote

A hard ceiling on query length does double duty: a 500-token "query" is a document, not a question, and the same ceiling defeats the **Trojan-paragraph** injection — an instruction buried in the middle of a benign wall of text. A human skims the top and bottom and sees nothing wrong; the model reads the middle and obeys. The length cap kills the vehicle before the payload is ever tokenized, and it costs a single integer comparison — the cheapest defense in the entire chapter.

## The loaded question

The subtlest member of this family has no syntactic signature at all. *"Why did the CEO embezzle money in 2022?"* embeds a **presupposition** — that the CEO embezzled — and a naive system takes the query at face value: it retrieves documents about the CEO's finances, finds a routine audit report, and generates an answer that engages the premise, manufacturing AI-authored text that associates a named person with a crime that may never have happened. The harm is not in any flaggable token; it's in a proposition the sentence takes for granted.

The tools are an NLI check — does the corpus actually entail "the CEO embezzled money"? — or a presupposition extractor that surfaces the buried claim so it can be tested. The best response is usually not refusal but **reframing**: *"Based on available documents, there is no evidence that the CEO embezzled money; here is what the record does say about the CEO's finances."* This is the first appearance of the graded, honest partial that Act III will make into a discipline.

## The cheapest structural gate: query length and complexity bounds

One comparison operator can retire an entire attack class before any classifier reads a word. In enterprise search logs, the median query runs **8-15 tokens**; the 95th percentile sits **under 50**. A 500-token "question" is either a mistake or an attack — either way, the right first response is not to embed it.

Enforce it in three graded tiers, so the cap is a scalpel and not a cleaver:

| Tier | Threshold | Action | False-positive cost |
|---|---|---|---|
| Hard ceiling | ~500 tokens | reject outright, non-punitive message | essentially zero — no legitimate enterprise query needs to be this long |
| Soft warning | ~100 tokens | admit, but raise scrutiny downstream | low — long *and* injection-flagged is now two signals, not one |
| Structural complexity | deeply nested delimiters, several instructions separated by newlines/bullets, embedded code fences | flag for review | natural questions rarely have this morphology |

```python
# toy three-tier length/complexity gate
def gate(query: str):
    tokens = query.split()
    n = len(tokens)
    if n > 500:
        return "hard_reject", "exceeds maximum length; please shorten or split your question"
    flags = []
    if n > 100:
        flags.append("soft_warning: unusually long, raise downstream scrutiny")
    bullet_like = query.count("\n") + query.count("- ") + query.count("```")
    if bullet_like >= 3:
        flags.append("structural_complexity: multiple embedded instructions")
    return "admit", flags or ["clean"]

for q in ["What is our leave policy?", " ".join(["word"] * 150), "Do X\n- also do Y\n- also do Z\n```run this```"]:
    print(gate(q))
```

> Length and structure are syntactic tells — countable, reliable, near-free — and belong at the very front precisely because they clear the field cheaply for the semantic gates that cannot.
