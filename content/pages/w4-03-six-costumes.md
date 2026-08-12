---
id: w4-03-six-costumes
title: "Every Text Wears a Costume"
week: 4
topic: "Act I: The Purpose Problem"
order: 3
summary: The same underlying fact is dressed differently for peer reviewers, adversaries, shareholders, and everyone else, and a user's naked query matches none of the costumes well.
---

Text is never neutral. It is dressed for an audience and a purpose, and the costume changes everything about how it can be found.

Consider the same underlying finding — a drug reduced thirty-day mortality by four percent — as it would be written in six different rooms:

| Genre | Written for | How it dresses the fact |
|---|---|---|
| The paper (IMRaD) | a skeptical peer reviewer | the number lives in Results, its meaning lives in Discussion, and the Abstract softens both into "may suggest a modest benefit" |
| The legal brief | an adversary | anticipates objections, buries the operative clause in "notwithstanding the foregoing" |
| The earnings call | shareholders and lawyers at once | responsibility distributed, every claim "wears a helmet" |
| The press release | the public | sells |
| The textbook | a learner | teaches |
| The tweet | an audience of scrollers | provokes |

**IMRaD** is Introduction, Methods, Results, and Discussion — the standard structure of a research paper, and it is worth naming because it is the clearest case of a genre that scatters one claim across several sections on purpose.

## Six costumes, one truth

Here is the thing that should unsettle you: a user's query — "does the drug reduce deaths?" — matches none of the six well. The query is naked. The text is in costume.

> Retrieval is the awkward party where the naked query must recognize a friend through six disguises.

## Search is an audience nobody wrote for

This is the week's quiet scandal. **Search-native text** — text shaped so that a blunt query lands on it — is almost never the raw text. The raw text was written for Meera, for the reviewer, for the shareholder, for the adversary. The searcher is an audience who arrived after the writing was done, speaking a different dialect: short, declarative, impatient, phrased as a question.

The raw text and the ideal search artifact can share almost no words. "Can the licensor end the contract early?" shares nothing lexically with "notwithstanding the provisions of Section 12(b), the Licensor retains the irrevocable right to terminate." Same meaning; disjoint vocabulary.

An embedding model can bridge some of that gap — that is what it is for — but Act II runs a live bake-off to see exactly how much gap is left when we lean on the embedder alone.
