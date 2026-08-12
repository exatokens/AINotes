---
id: w6-05-family-c-access-and-identity
title: "Family C — Access and Identity"
week: 6
topic: "Act I: The Gatehouse — Keeping Bad Questions Out"
order: 5
summary: A query can be polite, on-topic, and injection-free and still be one this particular person must never have answered, because the failure is authorization, not content.
---

The first two families asked *what the query says*. This one asks *who is asking, and what they're allowed to see* — and no content filter in the world catches a failure here, because it isn't a content problem at all.

## RBAC is a retrieval concern, not a UI concern

Role-based access control is old — enterprise software has enforced it since the 1990s. Its application to unstructured retrieval is new and treacherous. In a relational database, RBAC guards tables, rows, and columns with a clean schema. In a RAG system, RBAC must guard **chunks**, which have no schema — the only thing that gives a chunk a clearance level is the metadata you tagged it with at ingestion time. Get that tagging wrong and there is nothing downstream to catch it.

The governing rule is one sentence, and it is the most violated rule in production RAG:

> RBAC is a retrieval concern, not a UI concern. If you hand a sensitive document to the model, the model will generate from it — it has no notion of clearance, no way to know a passage was meant for the executive and not the intern.

So authorization must be a **pre-filter on the vector search**: the user's permissions become a metadata constraint (`access_level <= user_clearance`), applied *before* ranking, so unauthorized documents never enter the candidate set at all.

## Pre-retrieval versus post-retrieval filtering

Contrast this with **post-retrieval filtering** — retrieve first, then hide what the user may not see. This leaks. The number of results returned, or a conspicuous absence where a result should be, betrays the very existence of classified material: "your search matched three documents you are not cleared to view" *is itself a disclosure*.

| | Pre-retrieval filtering | Post-retrieval filtering |
|---|---|---|
| When the ACL applies | before ranking, as a search constraint | after retrieval, as a display filter |
| What it is | access control | information leakage wearing the costume of access control |
| Failure mode | none — unauthorized docs never enter candidate set | result counts and conspicuous absences leak existence |

The same discipline underwrites **tenant isolation** in a multi-customer system: tenant A's query must be structurally incapable of retrieving tenant B's chunks, enforced as a hard partition at the retrieval layer — a correctness property, not a feature.

## The confused deputy

When Family B meets Family C, you get the **confused deputy**, a classic security pattern that RAG reinvents vividly. A retrieval service runs with broad access — it must, to serve every authorized user from one index. An attacker who cannot reach a document directly instead plants an instruction (indirect injection) that the high-privilege service will read and act upon, borrowing the deputy's reach to do what the attacker's own low privilege forbids. Neither the service nor the user is malicious — the privilege of one is turned against the boundary of the other. The defense composes everything above: **the deputy must carry the originator's clearance into the retrieval filter, not its own**, so an injected instruction cannot fetch what the originating user could not.

## PII in the query — not an attack, but your incident

One member of this family is not adversarial at all, and it belongs here on purpose: PII arriving in the query. Users paste an SSN, an API key, a medical record, a credit-card number — sometimes on purpose, far more often an errant Ctrl+V into the wrong window. It is not an attack. But it becomes your compliance incident the instant the pipeline touches it, and the blast radius grows at every hop: the query is logged (now the secret is in your audit trail), embedded (now it is a vector in your index, potentially retrievable by a future query), and forwarded to a third-party model (now it has left your infrastructure entirely). Under GDPR, HIPAA, or PCI-DSS, each hop can be a violation on its own.

The defense is a detect-and-redact pass at the boundary: regexes for structured secrets (Luhn-valid card numbers, `AKIA` AWS keys, `ghp_` GitHub tokens, SSNs), plus a light NER pass — Presidio is the reference implementation — for names and addresses that have no fixed syntactic shape. Redact the span, replace it with a typed placeholder, and log the *type* of PII detected but never the value. Proceed with the redacted query if it still means something; decline if redaction emptied it.

```python
# toy PII detect-and-redact pass — regex only, no NER model
import re

PATTERNS = {
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "AWS_KEY": r"\bAKIA[0-9A-Z]{16}\b",
    "GITHUB_TOKEN": r"\bghp_[A-Za-z0-9]{36}\b",
    "CARD_NUMBER": r"\b(?:\d[ -]*?){13,16}\b",
}

def redact(query: str):
    found = []
    redacted = query
    for label, pattern in PATTERNS.items():
        if re.search(pattern, redacted):
            found.append(label)
            redacted = re.sub(pattern, f"[REDACTED_{label}]", redacted)
    return redacted, found

q = "My SSN is 123-45-6789, what is the leave policy for a contractor?"
redacted_q, types = redact(q)
print(redacted_q)
print("logged PII types (never the value):", types)
```

> **From the field.** For months, a regular at a company's weekly meetup ate dinner, then worked furiously on his laptop. It turned out the public-WiFi routing table had left a path open to one of the company's GPU servers, and he had quietly been running his own jobs on it for the price of a free dinner. No content filter in the world would have caught it — the abuse never touched the content path at all. Your guardrails are only as wide as the surface you remember to guard, and the surface is always larger than the diagram you drew.
