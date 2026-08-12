---
id: w3-11-contextual-and-late-chunking
title: "Re-Contextualization: Contextual and Late Chunking"
week: 3
topic: "Act III: Two Roads — Better Chunking, or No Chunking?"
order: 11
summary: Rather than inflate chunks, restore context dynamically — contextual chunking repairs in text space with an LLM-written preface, while late chunking repairs in latent space by chunking after encoding.
---

Rather than inflate chunks to preserve context, restore context dynamically. Two techniques attack the same target — endophora — from opposite directions.

## Contextual chunking: repair in text space

Chunk small, then for each chunk $C_i$ use an LLM to read the whole document and prepend the minimal context that completes it, embedding $C_i' = \text{CTX}_i \parallel C_i$. The chunk "It has a population of 3.6 million" becomes "Berlin is the most populous city of Germany. It has a population of 3.6 million." Described in Anthropic's widely cited note on contextual retrieval and studied by Das et al., it elegantly addresses endophora — at the cost of one LLM call per chunk, tamed in practice by a local model and prompt caching.

```python
# contextual chunking -- an LLM reads the whole doc and prepends a repair
def contextual_chunk(chunk, full_document, llm):
    prompt = (
        f"Document:\n{full_document}\n\n"
        f"Chunk:\n{chunk}\n\n"
        "Write 1-2 sentences of context that make this chunk self-contained. "
        "Do not alter the chunk's original text."
    )
    preface = llm.generate(prompt)
    return f"{preface} {chunk}"

# "It has a population of 3.6 million." -->
# "Berlin is the most populous city of Germany. It has a population of 3.6 million."
```

## Late chunking: repair in latent space

The more elegant idea. In the villages of North India, grandmothers cut old saris into patches and stitch them into a *razai* — a quilt holding every memory in one warm whole. Late chunking runs that in reverse: let the encoder stitch the whole document together — every token absorbing every other through attention — and only then cut.

If the encoder produces contextualized latents $h_i = \text{encode}(t_i \mid t_1, \ldots, t_n)$, each $h_i$ depending on all tokens, then

$$v_{\text{chunk}} = \text{MeanPool}(h_{i_1}, h_{i_1+1}, \ldots, h_{i_2})$$

Read this piece by piece. $h_i = \text{encode}(t_i \mid t_1, \ldots, t_n)$ says the vector for token $t_i$ is computed *while looking at every other token in the document* — that is what self-attention buys you for free, before any cutting happens. $\text{MeanPool}(h_{i_1}, \ldots, h_{i_2})$ is nothing more exotic than adding up the vectors between the two boundary tokens $i_1, i_2$ and dividing by how many there are. Compare traditional chunking, which first extracts text and embeds it without its surroundings: $v_{\text{chunk}}' = \text{embed}(t_{i_1:i_2})$ — those tokens never got to look outside their own chunk. The difference is the difference between a word that knows its neighbors and a word that has been orphaned.

**A tiny worked example**, reusing the cow sentence from the endophora page: "The cow jumped over the moon. It was rather pleased with itself." Give "cow" the toy direction $[1, 0]$ (as in earlier pages), and suppose a context-free "it" starts out meaning almost nothing on its own, closer to $[0, 1]$.

*Traditional chunking* embeds "It was rather pleased with itself" as its own chunk. "It" never sees "cow," so mean-pooling that sentence's tokens gives something like $v_{\text{chunk}}' \approx [0.1, 0.9]$ — nearly orthogonal to "cow." *Late chunking* encodes both sentences together first: self-attention lets "it" attend back to "cow" before any boundary is drawn, shifting its contextualized vector toward $[0.7, 0.3]$; mean-pooling the same sentence's tokens now gives $v_{\text{chunk}} \approx [0.7, 0.3]$.

```python
import numpy as np

cow = np.array([1.0, 0.0])
v_traditional = np.array([0.1, 0.9])   # "it" never saw "cow"
v_late        = np.array([0.7, 0.3])   # "it" absorbed "cow" via self-attention

cos = lambda a, b: a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
print("traditional chunk vs. 'cow':", round(cos(v_traditional, cow), 2))  # 0.11
print("late chunk vs. 'cow':       ", round(cos(v_late, cow), 2))         # 0.92
```

Query "what did the cow do?" now matches the late-chunked vector (cosine ≈ 0.92) far better than the traditionally-chunked one (cosine ≈ 0.11) — same words, same boundary, the only difference is *when* the cut happened relative to attention. A chunk whose text reads only "it jumped over the moon" can still be retrieved by "what did the cow do?" — because when "it" was encoded, it soaked up "cow" from prior context. It feels like magic; it is geometry.

```python
# late chunking -- embed the WHOLE document first, then pool boundaries after
def late_chunk(document_tokens, boundaries, encoder):
    # every token is encoded once, attending to the entire document
    hidden_states = encoder.encode_all(document_tokens)   # h_1 ... h_n

    chunk_vectors = []
    start = 0
    for end in boundaries:
        bucket = hidden_states[start:end]      # already-contextualized vectors
        chunk_vectors.append(bucket.mean(axis=0))  # mean pool inside the bucket
        start = end
    return chunk_vectors
# each resulting vector "knows" about the whole document, even if its
# own text span never mentions the subject explicitly
```

## Choosing between them

Both methods attack endophora, but differently: contextual chunking is more interpretable — you can read the prepended context and check it. Late chunking is more elegant and efficient — chunking and embedding merge into one pass over a local encoder. For mission-critical corpora, do both: contextualize the text, then late-chunk the result.

> A good leader holds both an earthworm's view — local, granular, every grain of soil — and an eagle's view — global, panoramic, the whole landscape. Small contextualized chunks give you the earthworm; hierarchical and late chunking give you the eagle. A well-designed pipeline gives you both.
