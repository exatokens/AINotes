---
id: w1-04-language-models-seq2seq
title: "Language Models & the Seq2Seq Scaffold"
week: 1
topic: "Act II: How the Machine Sees"
order: 4
summary: A language model factorises sequence probability into next-token predictions; seq2seq splits understanding (encoder) from speaking (decoder) — and RAG systems use two different models for the two jobs.
---

Strip away the marketing and a language model is a **sequence model**: a function that, given a sequence of tokens, assigns probabilities to what comes next. Formally, it factorises the probability of a whole sequence into a product of next-token probabilities:

$$p(y_1, y_2, \ldots, y_T) = \prod_{t=1}^{T} p\left(y_t \mid y_1, \ldots, y_{t-1}\right)$$

Read the $\prod$ (product) as "multiply the per-step probabilities together." Concretely: suppose that after reading "The capital of France is", the model assigns $p(\text{Paris}) = 0.62$ to the next token; then, having appended "Paris", it assigns $p(\text{"."} \mid \ldots \text{Paris}) = 0.90$ to the token after that. The probability of producing the two-token continuation "Paris." is just the product of those two steps: $0.62 \times 0.90 \approx 0.56$. Nothing more exotic is happening in the formula above — it is that same multiplication, carried out for every token in the sequence.

The pedagogical point is simple but important: the model does not consult a static memory of facts; it updates a probability distribution one token at a time, guided by the text seen so far.

Generation is **autoregressive**: predict $y_t$, append it, condition on it, predict $y_{t+1}$. Each factor is a distribution over the entire vocabulary, and "writing" is repeatedly sampling from it.

> This factorisation is why a language model can be *steered by context*: everything to the left — including the documents RAG inserts — conditions every probability that follows. Retrieval works precisely because the model attends to the evidence we place in $y_1, \ldots, y_{t-1}$.

## Core intuition

A language model is not a magical database. It is a probability machine over sequences. It predicts the next token, one step at a time, in a context-dependent way.

That matters for RAG because the context we add to the model is what decides which tokens are plausible. The retrieved evidence is not only information; it is a conditioning signal working directly on the probability distribution of the answer.

## Why it matters

If you do not understand the autoregressive pattern, it is easy to think of LLMs as “writing from memory” in a vague way. In reality, they are repeatedly using the visible context to choose what should come next.

This is why RAG works at all: the system injects the right chunk before the answer begins, shifting the probability distribution toward evidence-grounded responses.

## Instructor framing

This chapter is the conceptual bridge between representation and generation. The embedder places meaning in a space; the generator consumes context and writes the answer. They are different jobs, different models, and different failure modes.

## Worked example

Suppose the model sees: "The capital of France is".

It does not do a dictionary lookup. It conditionally assigns probability to each possible next token. The highest-probability next token is likely "Paris". Once that token is appended, the process continues. The model is not “knowing” a fact in a static sense; it is rolling forward through a sequence of conditional choices.

## Math explained step by step

The formula is a product of conditional probabilities:

$$p(y_1, y_2, \ldots, y_T) = \prod_{t=1}^{T} p\left(y_t \mid y_1, \ldots, y_{t-1}\right)$$

Each factor says: given the tokens seen so far, what is the probability of the next token? The product multiplies all these step-wise probabilities. That is exactly how the model assigns a likelihood to a whole sentence.

## Practical pattern

In a RAG system, the practical pattern is:

1. retrieve the relevant chunks;
2. place them before the user question in the prompt;
3. let the decoder generate from this modified context;
4. finally, verify or cite the evidence used.

Context is not just “more text”; it is the model's conditioning signal.

## Common traps

- imagining the LLM is a search engine rather than a conditional generator;
- forgetting that retrieval changes the model's probability distribution;
- conflating embedding models with generation models;
- treating prompt length as a substitute for evidence quality.

## Takeaways

- A language model is a sequence probability machine.
- RAG works by placing evidence in context before generation.
- The embedder and the generator serve different roles.
- The same model family can do both jobs, but they are not the same abstraction.

```python
# autoregressive generation, spelled out — the loop IS the idea
def next_token_probs(tokens):
    """Stand-in for a trained model: returns {token: probability}."""
    ...

tokens = ["The", "capital", "of", "France", "is"]
for step in range(3):
    probs = next_token_probs(tokens)
    best = max(probs, key=probs.get)   # greedy: take the most likely
    tokens.append(best)                # append, condition, repeat
print(" ".join(tokens))
```

## The seq2seq scaffold

The pedagogically useful scaffold for relating an input to an output is **sequence-to-sequence** (Sutskever et al.): an *encoder* reads the input and compresses it into an internal representation — a latent $z$ — and a *decoder* expands that latent into an output sequence:

$$\text{input} \xrightarrow{\;\text{encoder}\;} z \xrightarrow{\;\text{decoder}\;} \text{output}$$

Read it as a pipeline of meaning: the encoder's job is to **understand** (map text into a latent that captures its content); the decoder's job is to **speak** (turn a latent back into fluent text). Early machine translation used exactly this shape — read the French, form a thought, write the English.

```mermaid
flowchart LR
    IN[/"input sequence<br/>(e.g. French sentence)"/] --> ENC["Encoder<br/>(understands)"]
    ENC -- "latent z<br/>(fixed-size vector)" --> DEC["Decoder<br/>(speaks)"]
    DEC --> OUT[/"output sequence<br/>(e.g. English sentence)"/]
```

> **The bottleneck:** all the meaning of a long input must squeeze through a single fixed-size latent $z$. For a short sentence, fine; for a paragraph, the latent forgets its own beginning by the time it reaches the end. This bottleneck is exactly what *attention* was invented to relieve — next page.

## Encoder vs decoder: the Week-1 misconception that costs weeks

A distinction worth fixing now. In almost every production RAG system:

| | The **embedder** (encoder) | The **generator** (decoder LLM) |
|---|---|---|
| Job | Place texts as points in a space | Write the answer |
| Character | Silent, cheap | Eloquent, expensive |
| When it runs | Already ran over **every chunk** in the corpus | Once per answer |
| Examples | Sentence-BERT descendants, MiniLM | GPT-style models |

The model that generates your answer is **not** the same model that embeds your documents for retrieval. Conflating them is the single most common Week-1 misconception, and it quietly corrupts one's reasoning about cost, latency, and failure modes for weeks. When the course says "the embedding model", it means the encoder; "the LLM" or "the generator" means the decoder.
