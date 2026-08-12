---
id: w6-02-family-a-malformed-evasive-input
title: "Family A — Malformed and Evasive Input"
week: 6
topic: "Act I: The Gatehouse — Keeping Bad Questions Out"
order: 2
summary: The model reads far more than your filters do, so an attacker who wants past a toxicity classifier simply encodes the message the more capable reader downstream will decode and obey.
---

Imagine a bouncer who only speaks English standing in front of a translator who speaks fifty languages. If you want to sneak something past the bouncer, you don't argue with him — you just say it in a language he doesn't understand, and let the translator quietly pass it along. That's the whole logic of Family A.

## The asymmetry: the model is more capable than your filters

Your toxicity classifier reads English; the model reads base64, Cyrillic, and Zulu. An adversary who knows this doesn't type the slur — they encode it, and let the more capable reader downstream decode and obey what the less capable filter waved through. The governing principle of this entire family is **deobfuscate, then inspect**: before any content-level detector runs, render the input into the canonical form the model will effectively read.

The deobfuscation layer does four things, each costing microseconds:

- **NFKC normalization** folds homoglyphs and compatibility characters, so a token like `admin` written with a Cyrillic look-alike "а" (U+0430, visually identical to Latin U+0061) collapses to plain Latin `admin` before any string match runs.
- **Zero-width character stripping** removes characters (U+200B, U+200C, U+200D, U+FEFF) that are invisible in rendered text but present in the byte stream, where an attacker sows them between the letters of a banned phrase to shatter the string a matcher is looking for — and it logs their presence, since a query carrying zero-width joiners is almost never innocent.
- **Base64 / hex / URL decoding** feeds the decoded payload back through the entire pipeline, since the decoded form is the form the model will actually act on.
- **Script-consistency checks** flag queries mixing Latin and Cyrillic without linguistic reason (a Japanese query mixing kana and Latin is normal; a Latin phrase salted with Cyrillic homoglyphs is an attack signature).

> Inspection before canonicalization is inspection of the costume, not the person.

**Entropy is a cheap tell.** Base64 draws from a near-uniform 64-symbol alphabet and clusters near $\log_2 64 \approx 5.9$ bits per character; natural English runs closer to 1–1.5 bits, because letters are predictable from their neighbors. One entropy check — per-character Shannon entropy, thresholded — flags encoded payloads almost for free.

## The gibberish ladder: an escalation ladder in miniature

Gibberish is the cleanest worked example of the cheapest-first discipline in the whole course. Walk it rung by rung — the shape recurs everywhere.

| Rung | Technique | Cost | Catches |
|---|---|---|---|
| 1 | Hash-set membership test | near-free (µs) | keyboard smashes: `asdf`, `qwerty`, `jkljkl`, home-row runs, `aaaaaa` |
| 2 | Regex + character statistics | µs | consonant-run/no-vowel patterns; English sits near a 1.5:1 consonant-to-vowel ratio, a smash may exceed 4:1 |
| 3 | Entropy + out-of-vocabulary rate | fraction of a ms | a query 90% out-of-dictionary tokens is almost certainly not a question |
| 4 | Small distilled classifier | low ms, rarely invoked | the rare word-like-but-meaningless residue |

The ladder spends compute in inverse proportion to how often each rung fires — the expensive classifier runs almost never, because the cheap rungs already cleared the field.

> **From the field.** One client audit found that as much as **thirty percent** of all queries were gibberish — pure keyboard-smashes. Not malice, barely even carelessness: a new visitor probing an interface they were never taught to read. Thirty cents of every compute dollar was being spent embedding, retrieving, and generating answers to `asdfgh`. Rung 1 alone — a hash set — returned nearly all of it. The cheapest gate, deployed at the very front, often pays for the entire gatehouse by itself.

```python
# a toy gibberish detector: rungs 1-3 of the ladder, no model required
import re
import math
from collections import Counter

KEYBOARD_SMASHES = {"asdf", "qwerty", "jkljkl", "asdfgh", "aaaaaa"}
VOWELS = set("aeiou")

def char_entropy(s):
    counts = Counter(s.lower())
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())

def consonant_vowel_ratio(s):
    letters = [c for c in s.lower() if c.isalpha()]
    vowels = sum(1 for c in letters if c in VOWELS)
    consonants = len(letters) - vowels
    return consonants / max(vowels, 1)

def is_gibberish(query):
    q = query.strip().lower()
    if q in KEYBOARD_SMASHES:                       # rung 1
        return True, "rung1: keyboard smash"
    if consonant_vowel_ratio(q) > 4.0:               # rung 2
        return True, "rung2: impossible cv ratio"
    if char_entropy(q) > 4.5 and " " not in q:       # rung 3 (crude entropy stand-in)
        return True, "rung3: high entropy, no word boundary"
    return False, "passed"

for query in ["asdfgh", "xkcqbz vwpqrz", "what is our refund policy?"]:
    print(query, "->", is_gibberish(query))
```

## The translation jailbreak

Family A's subtlest wing: take a request your English classifier would refuse, translate it into a low-resource language — Zulu, Scots Gaelic, Hmong — and the multilingual model understands and complies while the monolingual guardrail, which has never seen toxicity in that language, assigns a low score and waves it through. The attack exploits a coverage asymmetry: the LLM was pretrained on a broad multilingual corpus; the safety filter was trained overwhelmingly on English.

The defense is to make the guardrail as multilingual as the model it protects. Detect the language first — fastText handles 170+ languages in microseconds — then enforce an explicit language policy: define the served languages; for anything outside it, either translate the query into a served language and re-run the *entire* pipeline on the translation, or decline the unserved language with a clear message. The one thing you must not do is let an unrecognized language skip the content checks.

> If your guardrails only speak English, your system is only safe in English.
