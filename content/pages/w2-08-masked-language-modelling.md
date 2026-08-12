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

## Why winning the game means something

If a machine could play this game well — if, across billions of novel sentences, it consistently placed most of its chips on the right missing word — what would you conclude about its grasp of language? You couldn't dismiss it as memorisation; the sentences are novel. You couldn't call it luck; the consistency forbids it. You'd have to admit it had learned something real about how words constrain one another — grammar, selectional preference, world knowledge — because there's no other way to keep the score low.

This is the audacious bet of **masked language modelling** (in the older language of psychology, the *cloze task*), and it paid off: a model trained only to be unsurprised by missing words turned out to have built, as a side effect, contextual representations rich enough to become the foundation of modern retrieval.

> The encoder you load to embed your documents was forged in exactly this fire — a softmax over a vocabulary, scored by negative log-likelihood, played billions of times. Its sense of which sentences "mean the same thing" is a fossil of how unsurprised it learned to be. Understand the game, and you can finally reason about why retrieval succeeds or fails.
