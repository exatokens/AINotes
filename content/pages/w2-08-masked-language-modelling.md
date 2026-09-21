---
id: w2-08-masked-language-modelling
title: "Masked Language Modelling: Guess the Missing Word"
week: 2
topic: "Act II: The Lookup That Learns"
order: 8
summary: BERT's training objective is the card game of guessing a blanked-out word, scored by exactly the negative log-likelihood built this morning — and a model that consistently wins that game across billions of novel sentences must have learned something real about language.
---

We now have a machine that makes beliefs (softmax), a judge that scores them (negative log-likelihood), and a mechanism that lets a word read its context (self-attention). Assemble them and you have the training objective that built the first great encoder, BERT: **Guess the Missing Word**.

## The game

You're dealt cards, each a sentence with one word blanked out, and a small vocabulary of candidate words. Your task: spread ten chips across the candidates according to your belief about the missing word — chips are probability, ten chips is certainty, and a softmax in your skull does the spreading. Then the true word is revealed, and you score yourself by $-\log_2 p$, the surprise of the chips you placed on the truth. Lowest total surprise wins.

The score sheet is a negative-log-likelihood calculation; the chip-spreading is a softmax. This is no longer a game — it is a training loop with you as the model.

Two moments repay the whole exercise:

- **The zero-chip trap.** Place no chips on a candidate, and if it's the answer, your surprise is $-\log 0 = \infty$ — you lose instantly. This is why real models never assign exactly zero probability to anything: the softmax's strictly positive exponentials cannot produce a zero, and log-loss punishes confident wrongness without mercy.
- **The bidirectional round.** First see only the left half of the sentence and bet; then see the right half too and bet again. The collapse in your surprise when the right context arrives is, in bits, exactly what reading both directions at once is worth — the entire architectural argument of BERT over a left-to-right model, made physical.

The decks are typically dealt in a deliberate order — an unfamiliar language first, then a partially-familiar one, then a fluent one — tracing a **perplexity curve**: near the clueless baseline of $\log_2 V$ bits for the unfamiliar language, rescued partway by cognates for the partially-familiar one, and near zero surprise for the fluent one. Your own scores, falling deck by deck, trace the same curve a model walks down during pretraining.

## Core intuition

Masked language modelling turns language into a prediction game. A model that can infer the missing token from context is not merely memorizing strings; it is learning the surrounding structure that makes one word more likely than another.

## Why it matters

This is the training objective that gave us the encoder family behind modern retrieval. The model's ability to recover missing words is the first point at which contextual meaning becomes a learned, reusable representation.

## Instructor framing

This chapter is the payoff of the whole week. Softmax gave us a way to turn scores into beliefs; negative log-likelihood gave us a way to score those beliefs against reality; self-attention gave a word a way to read its context. Masked language modelling is not a fourth new idea — it is those three, wired into a single training loop and run billions of times. The point for students is to see that BERT's "understanding" is not a separate mystical capacity; it is the residue of relentlessly playing, and gradually winning, this one card game.

## Worked example

Take a single dealt card: "The keys were locked inside the ___." A poor player spreads chips evenly across every noun in the vocabulary — "car," "house," "cabinet," "safe" — and pays a heavy, undifferentiated surprise no matter which one is revealed. A better player has learned, from millions of similar sentences, that "locked inside the ___" after "keys" overwhelmingly precedes small, keyable containers, and stacks eight of ten chips on "car" and "house." When the answer is revealed as "car," that player's surprise is small; the even-spreading player's is large. Run this exact scoring, deck after deck, and the chip-placement strategy that survives is not a list of memorized sentences — it is a working model of which words keep company with which, which is precisely the contextual representation later reused for semantic search.

This is the moment the model stops being a language pattern and starts becoming an internal representation of context. The score is not a trick — it is the embryo of the representation used later for semantic search.

## Why winning the game means something

If a machine could play this game well — if, across billions of novel sentences, it consistently placed most of its chips on the right missing word — what would you conclude about its grasp of language? You couldn't dismiss it as memorisation; the sentences are novel. You couldn't call it luck; the consistency forbids it. You'd have to admit it had learned something real about how words constrain one another — grammar, selectional preference, world knowledge — because there's no other way to keep the score low.

This is the audacious bet of **masked language modelling** (in the older language of psychology, the *cloze task*), and it paid off: a model trained only to be unsurprised by missing words turned out to have built, as a side effect, contextual representations rich enough to become the foundation of modern retrieval.

> The encoder you load to embed your documents was forged in exactly this fire — a softmax over a vocabulary, scored by negative log-likelihood, played billions of times. Its sense of which sentences "mean the same thing" is a fossil of how unsurprised it learned to be. Understand the game, and you can finally reason about why retrieval succeeds or fails.






## Math explained step by step

Walk the card game back into the three formulas built earlier this week.

**Step 1 — the model produces logits over the vocabulary.** For the blanked position, the model computes one raw score per candidate word — its "enthusiasm," exactly as in the cow/duck/sofa example — using the contextual vector that self-attention has already built for that blank from every other word in the sentence.

**Step 2 — softmax turns logits into your chip allocation.** $\text{softmax}(z)_i = e^{z_i} / \sum_j e^{z_j}$ spreads exactly ten chips' worth of probability across the vocabulary, honoring the model's relative confidences.

**Step 3 — negative log-likelihood scores the bet against the revealed word.** Once the true word is revealed, the loss is $-\log p(\text{true word})$ — the same surprise formula from two pages ago. A confident, correct bet costs almost nothing; a confident, wrong bet costs enormously, which is exactly the "zero-chip trap" above stated as a formula.

**Step 4 — training is minimizing average surprise across billions of blanks.** Backpropagating this loss adjusts every weight, including the attention projections, so that next time a similar context appears, the chips shift toward the word that actually filled it. Averaged over enough sentences, the only way to keep lowering this number is to have genuinely learned which words belong where — which is why a low loss on held-out text is trustworthy evidence of real linguistic competence, not overfitting to one example.

## Practical pattern

For a RAG engineer, the practical upshot is this: when you pick an embedding model, you are inheriting whatever the masked-language-modelling (or similar) pretraining taught it about context. Concretely:

1. prefer encoders whose pretraining corpus resembles your domain — a model that never saw clinical or legal text during MLM pretraining will have weaker contextual judgments there, however well it scores on general benchmarks;
2. treat published perplexity or loss curves as a rough proxy for "how unsurprised is this model by text like mine," not an absolute quality score;
3. remember that MLM pretraining alone gives you *contextual* representations, not yet *retrieval-shaped* ones — the next page's contrastive fine-tuning is still required before cosine similarity becomes a meaningful ranking signal.

## Common traps

- assuming a model that scores well on masked-word prediction is automatically good at retrieval — MLM builds contextual understanding, but (as the next page shows) it does nothing to spread embeddings apart in space;
- picking an off-the-shelf encoder without checking what domain its pretraining corpus covered, then being surprised when it misjudges jargon-heavy sentences;
- treating perplexity as a single absolute quality number rather than a comparison that only makes sense against a specific corpus;
- forgetting that the "zero-chip trap" is a live production bug, not just a toy rule: a model that assigns near-zero probability to a correct-but-rare answer produces a wildly disproportionate loss spike, which is why real vocabularies always keep some probability mass on every token via smoothing or subword coverage.

## Takeaways

- Masked language modelling trains an encoder by scoring its softmax guesses about hidden words with negative log-likelihood.
- Winning this game consistently, on novel sentences, requires learning real structure about language — not memorization.
- Contextual competence from MLM is necessary but not sufficient for retrieval; check whether an embedding model was *further* contrastively tuned before trusting its cosine scores for search.
- When choosing an embedding model, ask what corpus its masked-word pretraining ran on — a mismatch there predicts weak retrieval on your domain before you run a single query.

