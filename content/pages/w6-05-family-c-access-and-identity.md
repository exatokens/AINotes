---
id: w6-05-family-c-access-and-identity
title: "Family C — Access and Identity"
week: 6
topic: "Act I: The Gatehouse — Keeping Bad Questions Out"
order: 5
summary: A query can be polite, on-topic, and injection-free and still be one this particular person must never have answered, because the failure is authorization, not content.
---

The first two families asked *what the query says*. This one asks *who is asking, and what they're allowed to see* — and no content filter in the world catches a failure here, because it isn't a content problem at all.

## Core intuition

Access control is not an application-layer afterthought. In retrieval systems, it must be enforced at the search boundary because the model will happily consume unauthorized content once it gets inside the context window.

## Why it matters

This family is about secret correctness: the system must not permit a user to see or reuse data they are not allowed to access. If authorization is delayed until after retrieval, the system has already leaked information by the way it behaves.

## Instructor framing

The pre-retrieval-versus-post-retrieval distinction is worth drilling until it's automatic — it is a common real-world production bug, not a theoretical concern, and the table's framing ("information leakage wearing the costume of access control") is precise enough to quote directly when reviewing a teammate's design. The confused-deputy section is the hardest material on this page; make sure students can explain in their own words why neither party (the low-privilege attacker, the high-privilege retrieval service) is individually malicious, yet the outcome is a breach.

## Worked example



Consider an HR knowledge base shared between all employees and HR staff. An intern asks the assistant, "what is the standard severance package structure?" — a question the company policy allows any employee to have answered from the general HR handbook. But suppose the vector index also contains a specific document titled "Severance negotiation for [named senior executive], confidential" that happens to score highly similar to the intern's query, because it discusses the same topic in detail. With post-retrieval filtering, the system retrieves both documents, notices the second is restricted, and either silently drops it (fine) or the intern notices the response feels oddly incomplete, or worse, a differently-phrased query causes the filter to miss it. With pre-retrieval filtering, the confidential document is excluded from the candidate set entirely by a metadata constraint (`access_level <= intern_clearance`) applied before the vector search runs — the intern's query never sees it exist, cannot detect its presence through absence, and no downstream prompt or generation step ever has the chance to leak from it, because it was never in context to leak from.

This is the first time the security story stops being textual and becomes architectural. Authorization is a retrieval constraint, not a UI decoration.

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






## Math explained step by step

Formalize why post-retrieval filtering leaks information, using an information-theoretic framing.

**Step 1 — model what an observer can infer from search behavior.** Even if a post-retrieval filter perfectly hides a restricted document's *content*, the *existence* of filtering is itself observable: a result count that drops from "5 documents found" to "2 documents shown," a response that hedges suspiciously, or a latency difference between a filtered and unfiltered path. Each of these is a bit of information leaking from a channel that was supposed to be closed.

**Step 2 — quantify the leak as a side channel.** If an attacker can distinguish "your search matched N documents, M of which you can view" from "your search matched M documents" (M < N), they have learned that $N - M$ restricted documents exist and are relevant to their query — a real fact about the corpus's content, obtained without ever seeing the restricted text itself. Repeated queries can narrow this further (does adding "salary" to the query increase the hidden count? now you know the hidden documents mention salary), turning a binary existence leak into a slow-motion content leak via repeated probing.

**Step 3 — see why the pre-retrieval design has zero information in this channel.** If the ACL constraint is applied *before* ranking (as a filter on the candidate set, `access_level <= user_clearance`), the search that runs is, from the system's internal perspective, over a corpus that *never contained* the restricted documents in the first place — there were never "N documents" to begin with, only "M," so there is no gap between a hidden count and a shown count for an attacker to observe. The information simply isn't computed, let alone leaked.

**Step 4 — see why the confused-deputy fix requires the same principle applied to credentials, not just documents.** In the confused-deputy pattern, the retrieval service's own broad access is the analog of "the corpus contains N documents" — if the service applies its own clearance to a query it's serving on someone else's behalf, it's running the equivalent of pre-retrieval filtering with the wrong clearance level. The fix — propagate the originating user's clearance into the filter, not the deputy service's own — is exactly "make sure the constraint applied before the search reflects the actual permission boundary that matters," the same pre-retrieval discipline, just tracking whose permission is authoritative.

## Practical pattern

Implementing access control correctly in a retrieval pipeline:

1. implement every ACL check as a metadata filter applied to the vector search query itself (a `WHERE`-clause-equivalent on the index), never as a post-processing step on returned results — check your vector database's documentation for native pre-filtering support (most modern ones, including Qdrant, support this) rather than filtering in application code after retrieval;
2. propagate the originating user's identity and clearance through every layer of a multi-service pipeline explicitly — a retrieval service acting "on behalf of" a user must apply that user's permissions, not its own service-level credentials, at the point of search;
3. treat tenant isolation with the same pre-retrieval discipline as clearance levels — a multi-tenant index should make it structurally impossible (a hard partition or a mandatory tenant-ID filter) for one tenant's query to touch another's vectors, not merely unlikely;
4. add a detect-and-redact pass for PII at the query boundary as a standing pipeline stage, not an incident-response afterthought — treat every query as a potential PII-carrying event, log only the detected type never the value, and decide in advance whether a redacted query should proceed or be declined.

## Common traps

- implementing access control as a post-retrieval display filter ("hide the sensitive results from the response"), which leaks existence and often partial content through result counts, response hedging, or latency differences even when the actual restricted text is never shown;
- building a retrieval microservice with broad, service-level credentials and forgetting to propagate the originating user's specific clearance into every query it executes on that user's behalf — the textbook setup for a confused-deputy exploit;
- treating PII arriving in a user's query as an edge case to handle manually, rather than a standing, automated detect-and-redact pipeline stage that runs on every query regardless of whether an incident is suspected;
- assuming tenant isolation is achieved by application-level checks alone, without a hard structural partition at the retrieval layer that makes cross-tenant access impossible rather than merely checked-for.

## Takeaways

- Authorization in a RAG system must be enforced as a pre-retrieval filter on the search itself, not a post-retrieval display filter — filtering after the fact leaks the existence of restricted content through result counts and behavioral side channels, even when the content itself stays hidden.
- The confused-deputy pattern shows that a high-privilege retrieval service must carry the originating user's clearance into its own search, not its own service-level credentials, or an injected instruction can borrow the service's reach to exceed the attacker's actual permissions.
- Concretely: verify today whether your production retrieval pipeline applies ACL constraints before or after the vector search runs — if after, treat it as an active information-leakage vulnerability, not a performance optimization opportunity.
