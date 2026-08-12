---
id: w6-15-verbalized-uncertainty-signal-sources
title: "Verbalized Uncertainty: The Linguistics of an Honest Hedge"
week: 6
topic: "Act III: Refusal and Humility"
order: 15
summary: A hedge is only honest if a real, measured signal sits underneath it — which rules out both a fake-precise confidence number and the model's own self-report of how sure it is.
---

Once you decide to mark epistemic status — grounded, inferred, unknown — you have to decide *how* to say it out loud, and the obvious answer turns out to be wrong on both ends.

## Why a confidence number fails

The naive approach — ask the model to append a score, "(confidence: 0.72)" — fails twice over. Users don't read numbers as calibrated probabilities; a "72%" reads as either suspiciously precise or meaninglessly vague, and in neither case does it change what the reader does next. And the model's self-reported number is itself uncalibrated: a language model asked how sure it is will cheerfully report high confidence on a fabrication, because fluency and certainty share a surface in the training data. This is the deep reason the uncertainty signal cannot be the model's self-report.

## Verbalized uncertainty — templated, not improvised

The better instrument is **verbalized uncertainty**: templated hedging language, tied to an underlying signal, that tells the reader what to do rather than what to compute:

- *"The sources directly state…"* — for grounded claims
- *"The documents suggest, but do not confirm…"* — for inferences
- *"I could not find support for…"* — for the silent regions

The point is that it's **templated and not improvised**. Improvised hedges drift — the same epistemic status comes out as "probably" one time and "it is likely that" the next, and the reader can't learn to read them. A fixed vocabulary, each mapped to a threshold on a real signal, becomes a language the user can learn: after a dozen answers they know "suggest" means the system found a plausible but uncited basis.

> The subtle danger is the **confidently-wrong hedge**. A hedge is only honest if the signal beneath it is real; a system that says "the documents suggest" when the documents are in fact silent has not been humble — it has laundered a fabrication through the grammar of humility, which is worse than a bare claim because it borrows the credibility of a caveat it did not earn.

## Where the uncertainty signal actually comes from

If not the model's self-report, then what? Four sources are available in production, and they stack — a small Swiss-cheese of uncertainty estimators, not one oracle.

| Signal | What it measures | Cost |
|---|---|---|
| **Retrieval thinness** | how much relevant evidence came back at all — a query whose top chunks sit below the relevance floor, or whose scores fall off a cliff after the first hit, is barely covered by the corpus | cheapest — check before the generator writes a token |
| **Groundedness residue** | the direct signal from Act II's faithfulness machinery: the fraction of decomposed claims that failed to ground, per-claim so humility can be graded | as cheap as Tier 2 of the escalation ladder |
| **Consistency across samples** | sample the answer several times and measure claim agreement — fabrications are unstable, varying across samples, while grounded claims stay stable (SelfCheckGPT needs no evidence set at all, only the model's own variance) | moderate — multiple generations |
| **Semantic entropy** | the sharpest sample-based signal; ordinary token-level entropy conflates uncertainty about *meaning* with mere uncertainty about *wording* — semantic entropy first clusters sampled answers by meaning (using NLI to decide when two samples say the same thing), then measures entropy over the clusters, invariant to paraphrase | 5-10× sampling cost; cheap probes trained to read it off hidden states push the cost toward zero |

```python
# toy retrieval-thinness + groundedness-residue based hedge selector
def choose_hedge(top_score: float, groundedness_residue: float) -> str:
    # top_score: relevance of the best retrieved chunk (0-1)
    # groundedness_residue: fraction of claims that failed to ground (0-1)
    if top_score < 0.3:
        return "I could not find support for this in the available documents."
    if groundedness_residue > 0.3:
        return "The documents suggest, but do not fully confirm, the following:"
    return "The sources directly state:"

print(choose_hedge(top_score=0.85, groundedness_residue=0.05))
print(choose_hedge(top_score=0.85, groundedness_residue=0.4))
print(choose_hedge(top_score=0.15, groundedness_residue=0.0))
```

None of these four signals is calibrated out of the box — a groundedness residue of "0.3 ungrounded" is not a probability of error; it's a raw score whose relationship to actual error rate is unknown and drifts with the domain, retriever, and model version. Turning a raw score into a decision you can put a guarantee on is the job of the next page — the most principled idea in the Act.
