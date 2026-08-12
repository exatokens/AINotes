---
id: w6-07-query-memory-duplicates-stuffing-frustration
title: "Giving the Gate a Memory: Duplicates, Keyword Stuffing, and Frustration"
week: 6
topic: "Act I: The Gatehouse — Keeping Bad Questions Out"
order: 7
summary: Every gate so far judges one query in isolation and forgets it instantly — but a whole class of pattern, from repeated jailbreak attempts to a frustrated user, is only visible across a sequence of queries.
---

Every gate we've built so far is amnesiac: it judges each query in isolation, remembering nothing of the one before. That statelessness is itself a vulnerability — and, separately, a missed opportunity to be kind to a struggling user.

## Duplicate and near-duplicate queries

Consider the **Monte Carlo jailbreak**: an adversary submits the same forbidden prompt fifty times, each with a trivial variation, betting that the generator's own stochasticity will eventually roll a compliant response. If the system has no memory, every attempt is an independent trial, and the attacker's chance of at least one success climbs relentlessly with the number of tries:

$$P(\text{at least one success in } n \text{ tries}) = 1 - (1-p)^n$$

**Walk the numbers.** Suppose the per-attempt success probability is a modest $p = 0.02$ (2%). Over $n = 50$ tries:

$$1 - (1 - 0.02)^{50} = 1 - 0.98^{50} \approx 1 - 0.36 = 0.64$$

A near-certain breach, assembled entirely out of fifty individually-rejected-looking attempts. Duplicate detection collapses that geometry: recognize the fiftieth attempt as the first wearing a hat, and the attacker gets one roll, not fifty.

Two mechanisms, cheap then slightly less cheap:

- **Exact-match deduplication** hashes the normalized query and checks it against a per-user, time-windowed hash set (say, the last 15 minutes); a hit suppresses or redirects in microseconds.
- **Near-duplicate detection** embeds the query and compares it against the user's recent query embeddings, flagging any whose cosine similarity exceeds a high threshold — $\cos\theta > 0.95$ is a common operating point — since exact matching is trivially defeated by paraphrase ("Tell me about X" → "What can you say about X?").

The sliding window is the one real tuning knob: too short (30 seconds) and slow-drip probing walks through the gaps; too long (24 hours) and you block a legitimate user who genuinely needs to re-ask a question later. Not every duplicate is malicious — a repeated query is just as often a frustrated user re-submitting because the last answer missed, which is exactly the signal the frustration gate below is built to read.

```python
# toy near-duplicate detector using cosine similarity over a fake embedding
import math

def fake_embed(text):
    # stand-in for a real embedding model: a bag-of-words vector
    words = text.lower().split()
    return {w: words.count(w) for w in set(words)}

def cosine(a, b):
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    return dot / (norm_a * norm_b + 1e-9)

recent = fake_embed("tell me about our vacation policy")
new_query = fake_embed("what can you say about our vacation policy")
print("cosine similarity:", round(cosine(recent, new_query), 3), "-> near-duplicate if > 0.95")
```

## Keyword stuffing and retrieval manipulation

For a decade, search-engine spammers packed pages with repeated high-value keywords to game the ranker; a RAG system faces the same maneuver from the query side. A query like *"tell me about safety protocols safety compliance safety regulations safety standards safety training…"* biases retrieval toward a narrow region of the embedding space, floods the context window with redundant near-identical chunks, and exploits sparse relevance scoring (BM25/SPLADE reward documents matching more query terms, so repeating a term inflates its apparent importance).

The detectors are cheap and statistical, because the attack leaves a countable fingerprint. The sharpest is the **type-token ratio** — unique tokens over total tokens: natural language rarely falls below 0.5, while a stuffed query can plunge below 0.2.

```python
# toy type-token-ratio stuffing detector
def type_token_ratio(query: str) -> float:
    tokens = query.lower().split()
    return len(set(tokens)) / len(tokens)

stuffed = "safety safety compliance safety regulations safety standards safety training safety"
natural = "what are our current safety training requirements for new hires"
print("stuffed ttr:", round(type_token_ratio(stuffed), 2))   # well below 0.5
print("natural ttr:", round(type_token_ratio(natural), 2))
```

## Not every hard query is an attack: frustration and sentiment

Step back from the adversary for a moment, because the gatehouse's posture of suspicion — correct as it is — can blind us to a query that's difficult for a wholly different reason: the user is not attacking, they are angry. A message typed in all capitals — *"why is this system so useless, i have been trying for an hour"* — is not a jailbreak and carries no forbidden token; it is a human at the end of their patience. The worst possible response is the cheerful, context-free default: *"I'd be happy to help! Could you please rephrase your question?"* That's gasoline on a fire.

This gate doesn't defend the enterprise against harm; it defends the enterprise against losing a customer — a quality-of-service gate rather than a security one. So the frustration gate **detects, then routes, then acknowledges, then logs**: a sentiment classifier reads sustained capitalization, punctuation storms ("!!!???"), aggressive-but-non-toxic phrasing, and the same question re-asked three times (shaking hands with the duplicate detector above). On a high-frustration signal, escalate to a human queue; if none is available, acknowledge rather than paper over the state ("I can see this has been difficult; let me connect you with a specialist"); and log persistent frustration as a systemic UX signal for the product team, not a per-user quirk.

> A language model is trained to be helpful, not to read emotional state and adapt. Detecting the state is the cheap part; changing behavior in response to it is the guardrail.
