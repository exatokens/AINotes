---
id: w3-11-contextual-and-late-chunking
title: "Re-Contextualization: Contextual and Late Chunking"
week: 3
topic: "Act III: Two Roads — Better Chunking, or No Chunking?"
order: 11
summary: Rather than inflate chunks, restore context dynamically — contextual chunking repairs in text space with an LLM-written preface, while late chunking repairs in latent space by chunking after encoding.
---

Rather than inflate chunks to preserve context, restore context dynamically. Two techniques attack the same target — endophora — from opposite directions.

## Core intuition

A chunk is not only a slice of text; it is a fragment that may depend on nearby context for its meaning. The solution is to restore that context either before or during encoding, rather than hoping the chunk is self-sufficient.

## Why it matters

This is the first practical repair strategy for the exact failure mode chunking creates: a sentence whose meaning is trapped in the surrounding document. These methods recover that dropped meaning without simply enlarging the chunk blindly.

## Instructor framing

The pedagogical hinge of this page is "text space vs. latent space" — students should leave able to say, precisely, where each technique intervenes. Contextual chunking intervenes *before* embedding, by rewriting the text itself (an LLM call, an extra artifact you can literally read). Late chunking intervenes *during* embedding, by reordering the pipeline so attention happens before the cut, not after (no new text, nothing to read — the fix lives entirely in when pooling occurs). Both repair the same endophora wound; they are not competing theories, they are different surgical approaches.

## Worked example

Take the Wikipedia-style paragraph: "Berlin is the capital and largest city of Germany. It has a population of 3.6 million, making it the European Union's most populous city." A naive chunker splitting on sentence length might place the second sentence in its own chunk for retrieval, where "it" has no textual referent at all. Contextual chunking asks an LLM to read the whole document and hand back a short repair — "Berlin is the most populous city of Germany." — prepended to the orphaned sentence, so the chunk that reaches the encoder now reads as a complete, self-contained fact. Late chunking does something less visible but equally effective: it never separates the sentences before running the encoder, so by the time "it" is turned into a vector, self-attention has already let it look back at "Berlin" and absorb that meaning — the chunk's *text* still says only "It has a population of 3.6 million," but its *vector* already knows it's about Berlin.

We are no longer asking whether chunking is possible. We are asking when context should be restored, and whether that restoration should happen in text space or latent space.

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






## Math explained step by step

Recap the cow/late-chunking worked example above as the four-step argument for why *order of operations* is the entire mechanism.

**Step 1 — name the two orderings being compared.** Traditional chunking: cut the text first, encode each piece second — so "It was rather pleased with itself" is encoded with no access to "cow" at all. Late chunking: encode the whole document first (every token attends to every other token, including across the sentence boundary), cut second, then mean-pool each already-contextualized span.

**Step 2 — see numerically what each ordering produces.** Traditional gives "it" a token vector near $[0.1, 0.9]$ — nearly orthogonal to "cow" $=[1,0]$, cosine $\approx 0.11$. Late chunking gives "it" a vector near $[0.7, 0.3]$ — because self-attention let it read "cow" before any cut happened — cosine $\approx 0.92$ against "cow."

**Step 3 — connect the vector difference to a ranking outcome.** A query "what did the cow do?" embeds close to the "cow" direction. Retrieval scores it against both chunk vectors: the late-chunked vector (cosine $0.92$) wins decisively over the traditionally-chunked one (cosine $0.11$), even though the underlying *text* of the chunk — "it jumped over the moon" — is identical in both cases. The only variable that changed was *when*, relative to attention, the boundary was drawn.

**Step 4 — see why this generalizes beyond one pronoun.** The same argument applies to any information that self-attention could have propagated across a would-be chunk boundary — a definition established paragraphs earlier, an antecedent several sentences back, a qualifying clause. Late chunking doesn't fix any one pathology by name; it fixes the entire class of pathologies caused by cutting *before* the encoder had a chance to read the whole context, which is why it pairs so well with contextual chunking's more surgical, human-readable repairs.

## Practical pattern

Choose (or combine) the two repairs based on what you can afford to inspect and what your encoder supports:

1. use **contextual chunking** when you need an auditable trail — the prepended context is literal text a reviewer or compliance process can read and verify, which matters for regulated domains;
2. use **late chunking** when your embedding model's context window can hold the whole source document (or a large section of it) — it is cheaper per chunk (no extra LLM call) and requires no prompt engineering, only a change in *when* pooling happens in your embedding pipeline;
3. for mission-critical corpora, do both in sequence — contextualize the text first (repairing references an encoder's attention window might not reach anyway, e.g. across a multi-document context), then late-chunk the contextualized result to capture everything attention can still reach directly;
4. check your embedding library's API before assuming late chunking is available — it requires access to per-token hidden states before pooling, which many hosted embedding APIs do not expose; you may need a local encoder to implement it.

## Common traps

- assuming late chunking works with any embedding model, when it actually requires access to per-token hidden states before pooling — most hosted, black-box embedding APIs only return the final pooled vector and cannot support it;
- letting contextual chunking's LLM-written preface drift from the source text — if the model summarizes or slightly distorts the context sentence, you have introduced a new, subtler faithfulness problem while fixing the endophora one;
- applying late chunking to documents longer than the encoder's context window — attention cannot connect tokens the model never sees together in the same forward pass, so late chunking silently degrades back toward traditional chunking's blindness once the document exceeds the window;
- treating either technique as a complete fix for Act II's whole catalogue — both target endophora and cross-reference specifically; discourse severing (Toulmin units) and negation scope still need their own handling (keeping the relevant sentences in one chunk) regardless of which re-contextualization method you use.

## Takeaways

- Contextual chunking repairs in text space (an LLM-written preface you can read and audit); late chunking repairs in latent space (attention runs before the cut, no new text produced).
- The order of operations — encode-then-cut versus cut-then-encode — is the entire mechanism behind late chunking's improvement; the underlying chunk text never changes.
- Late chunking requires per-token hidden-state access and a context window large enough to hold the source document — verify both before adopting it.
- Concretely: for regulated or high-stakes corpora, contextualize the text first and late-chunk the result — the combination is more expensive than either alone but repairs the widest range of severed references.
