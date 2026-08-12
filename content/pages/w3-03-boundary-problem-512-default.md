---
id: w3-03-boundary-problem-512-default
title: "The Boundary Problem and the 512-Token Default"
week: 3
topic: "Act I: The First Cut Is the Deepest"
order: 3
summary: A document is a continuous stream of meaning with no ground-truth boundary, and the industry's default of 512 tokens is a baseline for expedience, not a considered choice.
---

The first pathology is deceptively simple: where do we draw the line? A document is a continuous stream of meaning, and the question of where one chunk ends has no ground truth. Too small, and we lose context; too large, and we conflate distinct thoughts. There is no universal right answer — optimal granularity depends on query distribution, domain density, and downstream task.

## Reckoning the 512-token default

Fixed-size chunking is the worst offender, and 512 tokens is the most common default. Let's reckon with what that actually means:

| Unit | Rough size |
|---|---|
| One line | 8–10 words ≈ 10–13 tokens |
| One page | 30–40 lines ≈ 300–400 tokens |
| 512-token chunk | ≈ one page |

So a 512-token chunk is about one printed page. What is the probability that an arbitrary page contains **exactly one** coherent thought? For a dense newspaper article, very low. For a discursive academic text — the kind where a friend can step out for coffee, return an hour later, and find the lecture still on the same point — also very low.

```python
# a naive fixed-size chunker -- the "worst offender" the source warns about
def fixed_size_chunk(tokens, size=512):
    return [tokens[i:i + size] for i in range(0, len(tokens), size)]

# it has no idea where a sentence, paragraph, or thought ends --
# it just counts to 512 and drops the knife
tokens = list(range(1300))  # stand-in for a tokenized document
chunks = fixed_size_chunk(tokens)
print([len(c) for c in chunks])  # [512, 512, 276] -- boundaries fall wherever they fall
```

> The 512-token default is not a considered choice; it is a baseline for expedience. Yet adopted unreflectively it cascades through the entire pipeline, silently fixing what the system can ever retrieve.

An engineer who spends weeks tuning rerankers and prompts while leaving chunking at the default 512-token setting is polishing the upper floors of a building whose foundation is cracked. The greatest leverage in most RAG systems is not the generator — it is the quality of the input to the retriever, and chunking determines that quality.

This is the first lesson of chunking: question the orthodoxy. Do not be indoctrinated into the unthinking sequence every tutorial prescribes — think from first principles about what you gain and lose at each cut. Act II catalogues exactly what gets lost.
