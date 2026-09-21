---
id: w4-03-six-costumes
title: "Every Text Wears a Costume"
week: 4
topic: "Act I: The Purpose Problem"
order: 3
summary: The same underlying fact is dressed differently for peer reviewers, adversaries, shareholders, and everyone else, and a user's naked query matches none of the costumes well.
---

Text is never neutral. It is dressed for an audience and a purpose, and the costume changes everything about how it can be found.

## Core intuition

The same fact can wear many different textual costumes. A document is not just content; it is a performance for a specific audience, genre, and purpose.

This matters because users search in a different dialect from the document's authorial voice. Retrieval is then not just a matter of matching words; it is often a matter of recognizing the same fact through a different textual disguise.

## Why it matters

If the retriever only searches raw text written for a human audience, it may miss the form the query is actually asking for. The mismatch between genre and intent is one of the central reasons search-native text exists.

## Instructor framing

Use the six-costume table as a diagnostic checklist students can apply to their own capstone corpus: before building any retrieval system, ask "what genre is this text, and who was it actually written for?" A student who cannot answer that question for their own documents does not yet understand their retrieval problem well enough to start building.

## Worked example



This chapter is a direct restatement of the purpose problem: the searcher is an audience nobody wrote for, and the text's costume matters because the query arrives in a bare, direct form.

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



## Math explained step by step

Quantify "the query is naked, the text is in costume" using the drug-mortality example across genres.

**Step 1 — treat each genre as a different transformation of the same underlying fact.** Let $F$ = "the drug reduced 30-day mortality by 4%." Each genre applies its own transformation: the paper hedges it ("may suggest a modest benefit"), the press release amplifies it, the legal brief buries it in qualifying clauses. Six genres, six surface forms, one $F$.

**Step 2 — a query is generated from $F$ directly, not from any one genre's transformation.** "Does the drug reduce deaths?" is close, lexically and semantically, to $F$ itself — a plain statement of the fact — but each genre's surface form has moved *away* from that plain statement by design (that's what a costume is: a deliberate transformation for an audience).

**Step 3 — see why this predicts a specific, measurable ranking problem.** Because the query resembles $F$ more than it resembles any costume, cosine similarity between the query and each costumed passage is *systematically depressed* relative to what it would be if the passage stated $F$ plainly — and depressed by different amounts for different genres, since the press release's amplification and the legal brief's burial are different distances from plain statement.

**Step 4 — see why a search-native rewrite specifically targets this gap.** A derived sentence that states $F$ plainly — "The drug reduced 30-day mortality by 4%" — sits, by construction, exactly where the query already expects a match to be. This is why Act II's bake-off (next pages) measures real, often dramatic, similarity gains from adding such artifacts: the rewrite doesn't make the embedding model smarter, it removes the genre-specific distance the model had to overcome unaided.

## Practical pattern

The right solution is not to force users to speak the author’s language. It is to create text that speaks the user’s language while still linking back to the original source of truth.

## Common traps

- assuming all text is equally retrievable; 
- forcing the searcher to match the document's genre; 
- treating a raw passage as the only valid retrieval object.

## Takeaways

- Text is authored for a purpose and audience.
- The query dialect is often very different from the document dialect.
- Search-native artifacts are a response to this structural mismatch.
