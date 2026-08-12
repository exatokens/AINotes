---
id: w4-02-meera-and-ravi
title: "Meera and Ravi: Two Ways to Prepare for an Exam"
week: 4
topic: "Act I: The Purpose Problem"
order: 2
summary: A story about two exam-takers shows that representation follows purpose, and that a textbook built for understanding is the wrong shape for a system that must instantly match a query to an answer.
---

Two students are preparing for the IIT entrance examination — the gateway exam that, in India, decides futures. Call them Meera and Ravi.

**Meera** reads physics to understand it. She lingers on Newton's third law until she can feel the symmetry of forces in her bones; she derives, she doubts, she rebuilds. **Ravi** does something different. Ravi has a coach, and the coach has a stack of ten thousand past questions. Ravi drills until, the instant he sees "two blocks, one pulley, coefficient of friction µ," his hand is already moving. He is not understanding the problem. He is matching it.

## Who is right?

It is a trick question — they have different purposes, and **purpose dictates representation**. Meera is building a model of the world. Ravi is building an index from question-shapes to answer-procedures. Test them on deep conceptual transfer, and Meera wins. Test them on "answer two hundred questions in three hours," and Ravi wins, and it is not close.

> This is not a parable against Ravi. Under a three-hour exam with two hundred questions, his representation is the correct one for his purpose. The error would be to confuse his purpose with Meera's.

## The punchline for RAG

A textbook is written for Meera. It builds understanding cumulatively, page after page, each idea resting on the last. Retrieval-augmented generation, at query time, is Ravi: it needs to look at a short question and instantly reach the passage that answers it.

When you index a Meera-text for a Ravi-task, you get a mismatch — and that mismatch is the silent cause of half the bad RAG demos you have ever seen.

The fix is **not** to read the textbook better. The fix is to manufacture Ravi's flashcards from it, and index those.

| | Meera | Ravi |
|---|---|---|
| Optimizes for | deep conceptual understanding | instant question-to-answer matching |
| Representation | cumulative, sequential prose | question-shaped procedures |
| Wins when | transfer, novel reasoning | fixed-format, time-boxed exam |
| Analogue in RAG | the original document | the derivative artifact we search against |

The resolution is not to pick one over the other — it is to keep both, each doing the job it is suited for. Ravi's flashcards index the understanding; Meera's text still *is* the understanding. We will make this precise in Act II as **the core pattern**: retrieve against the derivative, generate from the source.
