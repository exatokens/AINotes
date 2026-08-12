---
id: w3-08-bridging-inference-genre-blindness
title: "Bridging Inference and Genre Blindness"
week: 3
topic: "Act II: A Field Guide to What Chunking Destroys"
order: 8
summary: Some connections have nothing explicit to sever, and a uniform chunk size ignores that a contract, a novel, and a paper carry information at wildly different densities.
---

There is a connection subtler than endophora or lexical cohesion — one with nothing explicit to detect. "John walked into the room. The chandelier was magnificent." No pronoun, no connective — yet every reader knows the chandelier is in the room. The definite article signals that the chandelier belongs to the frame that "room" activated. This is **bridging inference**, and Schank's theory of scripts explains its reach: "the restaurant" activates waiter, menu, bill, tip, so "she left a generous tip" is coherent only while the restaurant script is live. Chunk it away and the embedding captures the act of tipping but not its situation.

In technical text the danger sharpens: "the potential" (gravitational? electric?), "the spread" (bid–ask? credit? yield?) — the surrounding text is the only disambiguator, and chunking severs it invisibly.

## Genre blindness

A structural failure precedes all of these: **genre blindness** — treating a legal contract, a novel, and a scientific paper as if they shared one information structure.

| Genre | Information density |
|---|---|
| Legal contract | Dense — every clause carries force |
| Novel | Sparse — pages of atmosphere around one pivotal line |
| Scientific paper | Rigid implicit structure (abstract, methods, results, each presupposing the others) |

Your chunker gives all three 512 tokens. Density varies *within* a document too: an abstract is extraordinarily dense, an introduction discursive. Optimal chunking would adapt its granularity to this variation — yet almost no production system does, because measuring density in real time requires the very understanding the system is trying to achieve.

Tone is the final casualty: Swift's "A Modest Proposal" is satire only in the contrast between earnest setup and monstrous punchline; chunk them apart and one reads as policy, the other as lunacy, and neither is the truth.

## Query–chunk asymmetry

> Queries are short and sharp; chunks are long and diffuse. A focused query point matched against a blurred chunk centroid underestimates true relevance, so the system is biased toward homogeneous chunks and against heterogeneous ones — regardless of which holds the answer. It is retrieving the most internally coherent chunks, not the most relevant ones. Those are not the same thing.

Bridging inference and genre blindness both point to the same conclusion: there is no universally optimal decomposition. Document structure, modality, and task jointly determine what "one thought" even means.
