---
id: w3-01-first-projection-is-irreversible
title: "The First Projection Is Irreversible"
week: 3
topic: "Act I: The First Cut Is the Deepest"
order: 1
summary: Chunking is not preprocessing but the first lossy projection in the pipeline, and what the encoder never sees, the generator can never recover.
---

Twice now we have stood at the edge of a sphere. On Day 1, meaning became geometry — points on a high-dimensional manifold, nearness as kinship. On Day 2, we earned that geometry with attention and softmax, and ended on anisotropy, the huddling of embeddings into a narrow cone. This week takes the next, deceptively simple step: before a single vector can be computed, a document must be turned into the things we embed. That act has a name — **chunking** — and it is treated everywhere as settled plumbing: parse, slice, embed, retrieve.

It is not settled. It hides the first irreversible decision in the entire pipeline.

## Core intuition

Chunking is not a technical cleanup step. It is the first irreversible projection of information into the retrieval system.

Whatever you define as one chunk becomes the atomic unit that the model can later retrieve, score, and reason over. Once that boundary is chosen, the system can never reconstruct what was cut away.

## Why it matters

A bad chunk boundary creates a bad retrieval unit. It can destroy context, force two unrelated ideas into the same vector, or split a single argument across multiple fragments so that no fragment is faithful to the whole.

This is why chunking is one of the highest-leverage design choices in a RAG system.

## Instructor framing

This week is about the first major engineering decision after the geometry itself. The course is telling you that retrieval is not just “embed a document and hope.” It is “choose the right unit of meaning before any embedding happens.”

## Worked example


If a chunk contains two topics — “cow behavior” and “stock market volatility” — the embedding must compress them into one point. That point can no longer faithfully mean either one. The system has lost the ability to answer either question cleanly.

## Every embedding is a lossy projection

Recall the children's telephone game from Day 1 — the whisper that degrades with each relay. Embedding is the first relay. If that very first step introduces significant loss, no amount of downstream sophistication — no reranker, no clever prompt — can restore it. This is why chunking is not preprocessing. It is the first **ontological** decision in your retrieval pipeline: what you decide to embed as one unit fixes what the system can and cannot ever retrieve.

## The information bottleneck

The loss is structural, not incidental. Here is the plain-English version before the symbols: any time you compress something, you face a trade-off between throwing away as much as possible — to keep the result small and cheap — and keeping whatever part will actually matter later. The **information bottleneck** is that trade-off written as math. Given an input $X$ (the full text of a chunk) and a target $Y$ (whatever you will eventually ask of it — a topic, an answer to a query), we want a representation $Z$ — the embedding — that keeps as much information about $Y$ as possible while discarding as much of the rest of $X$ as possible:

$$\mathcal{L}_{IB} = I(X; Z) - \beta\, I(Z; Y)$$

Read it piece by piece. $I(\cdot;\cdot)$ is **mutual information** — a number answering "if I know one of these, how much less uncertain am I about the other?" $I(X;Z)$ measures how much of the raw chunk survived into the embedding — we want this *small*, since small means compact and cheap. $I(Z;Y)$ measures how much of what actually matters survived — we want this *large*. Because it is subtracted and weighted by $\beta$, a bigger $I(Z;Y)$ always shrinks the loss $\mathcal{L}_{IB}$ we are trying to minimize. So minimizing this loss means: compress hard, but not the part that matters.

**A tiny worked example.** Suppose a chunk is about one of two equally likely topics — cows or the stock market — so knowing $Y$ (the topic) is worth exactly 1 bit of information ($\log_2 2 = 1$, two equally likely options). Compare two ways of building $Z$:

| Representation $Z$ | $I(Z; Y)$ | What happened |
|---|---|---|
| $Z$ = which topic the chunk is about | 1 bit (perfect) | $Z$ is small *and* keeps everything that matters |
| $Z$ = the average of a cow-sentence and a stock-sentence embedding (the mixing principle, below) | ≈0 bits | $Z$ still costs bits to store, but a query can no longer tell which topic it came from |

The second row is the trap: mixing two thoughts does not just fail to save you anything — it can cost you *all* of $I(Z;Y)$, the one term in the loss that was supposed to pay for itself. When we embed a chunk, we pass it through exactly such a bottleneck. If the chunk holds two distinct thoughts — cows and the stock market — the bottleneck must crush both into one point. The result is faithful to neither. This is why chunk composition matters so profoundly.

```mermaid
flowchart LR
    D[/"raw document<br/>(many thoughts)"/] --> C["chunking decision<br/>(the first cut)"]
    C --> E["embedding<br/>(information bottleneck)"]
    E --> V[/"single vector<br/>(lossy, irreversible)"/]
    V --> R["retriever, reranker,<br/>generator downstream"]
    R -.->|"cannot recover<br/>what the cut destroyed"| V
```

> Every embedding is a lossy projection, and the first projection — from source to embedded unit — is the one no downstream cleverness can undo. What the encoder cannot see, the generator cannot recover.

The dominant narrative is parse → chunk → embed → retrieve, and almost every RAG pipeline opens with this unquestioned first step. This week questions it, beginning with the decision itself: what counts as one thought worth embedding as one unit?



## Math explained step by step

Unpack the information-bottleneck loss $\mathcal{L}_{IB} = I(X;Z) - \beta\,I(Z;Y)$ against the cow/stock table above, one term at a time.

**Step 1 — read $I(X;Z)$ as "how much of the raw chunk did the embedding keep?"** A 384-dimensional vector can hold only so much; this term is small by construction the moment you compress a paragraph into a point, and that's fine — compactness is the entire point of embedding.

**Step 2 — read $I(Z;Y)$ as "does the embedding still answer the question we'll eventually ask?"** In the table, $Z=$ "which topic" keeps all 1 bit that matters; $Z=$ "the averaged vector" keeps essentially none, even though it is exactly as expensive to store.

**Step 3 — see why the two terms fight over the same chunk.** If a chunk contains both the cow sentence and the stock sentence, a single fixed-size vector must represent both; whatever budget of "directions" gets spent describing the cow content is a budget not spent describing the stock content, and vice versa. The bottleneck is not a metaphor — it is $d$ real numbers with no more room to add.

**Step 4 — see the practical consequence in the cosine numbers.** The toy code shows the averaged vector scoring "mediocre" against *both* clusters, never strongly against either. That mediocrity is $I(Z;Y) \approx 0$ made visible: a query about cows and a query about stocks both get a lukewarm, unhelpful match, because the chunking decision destroyed the information needed to tell them apart *before* the embedding model ever ran.

## Practical pattern

Good chunking starts with the question: what is the smallest unit of meaning that should survive retrieval as a coherent object? The answer depends on the task, the domain, and the query distribution, but the principle is the same: preserve conceptual integrity before embedding.

## Common traps

- assuming 512 tokens is a principled standard;
- treating chunking as a preprocessing detail;
- mixing unrelated thoughts into one vector;
- expecting reranking or prompting to repair a broken chunk boundary.

## Takeaways

- Chunking is the first irreversible projection in retrieval.
- The chosen chunk defines the unit of semantic meaning.
- Loss happens at the boundary, before the model ever sees the text.
- Good retrieval starts with good chunking, not with better prompts.
