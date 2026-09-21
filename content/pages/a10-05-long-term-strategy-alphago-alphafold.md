---
id: a10-05-long-term-strategy-alphago-alphafold
title: "Long-Term Strategy: What Move 37 and AlphaFold Actually Proved"
week: 10
topic: "Act I: The Vocabulary of Reinforcement Learning"
order: 5
summary: AlphaGo's Move 37 and AlphaFold's protein-folding breakthrough are the same proof, twice — that optimizing over whole trajectories rather than local steps lets reinforcement learning discover strategies no human ever demonstrated.
course: ai_agents
---

By move 36 of a game against world champion Lee Sedol, every human Go expert watching agreed the machine had lost. In their trained, expert judgment, the value of the state AlphaGo occupied was disastrously low. Then AlphaGo played move 37, and no human expert understood it — the collective reaction was a puzzled "interesting." That single move led to a new board state, and the true value of that state — the expected reward of every trajectory from there — turned out to be a win. The AI had found a genuinely superhuman strategy, one that human intuition, trained over a millennium of Go tradition, could not even recognize as promising while looking directly at it.

This page treats Move 37 and its stranger cousin, AlphaFold's protein-folding breakthrough, as data points in an argument this week has been building since the parenting-styles page: supervised learning optimizes locally against a fixed teacher, while reinforcement learning optimizes over entire trajectories against a goal, and that difference in *what is being optimized* is what allows RL to occasionally produce strategies nobody who trained it ever imagined.

## Core intuition

Supervised learning performs local optimization — it micro-optimizes a loss function computed example by example, move by move, token by token. Reinforcement learning performs optimization over entire *trajectories* — it evaluates the cumulative, discounted consequence of a whole sequence of decisions, which forces the learner to think strategically rather than merely tactically. A locally suboptimal move (sacrificing a piece, seeming to lose ground) can be part of a globally optimal trajectory (winning the game), and only trajectory-level optimization can discover and reward that combination.

## Why it matters

This distinction explains a cultural pattern the course draws out explicitly: cultures and institutions associated with long-termism (the traditions that produced and prize Go) versus those oriented around short-horizon metrics ("quarterly earnings," the tactical frame) map onto exactly the SL-versus-RL local-versus-trajectory distinction. It is not a coincidence that RL — the paradigm mathematically built to reward long-horizon outcomes over locally attractive but ultimately inferior moves — is the paradigm that produced Move 37. A learner optimized against local, per-step signals structurally cannot discover a strategy whose value only reveals itself many steps later.

## Instructor framing

Present AlphaFold immediately after AlphaGo, and make the parallel explicit rather than treating them as two unrelated anecdotes: the AlphaGo team, having built a system that mastered long-horizon strategic reasoning in Go, deliberately asked "what other problem is this hard?" and answered it with protein folding — repurposing the *same underlying RL techniques*, not a bespoke new algorithm, onto a completely different domain. This is a strong argument for treating RL's core machinery (policy, value, trajectory-level reward) as domain-general infrastructure, worth understanding on its own terms rather than as "the Go algorithm" or "the biology algorithm."

## Worked example

Protein folding was, for decades, biology's "holy grail" problem — understanding a protein's 3D structure from its amino-acid sequence is central to understanding disease mechanisms and discovering drugs, and finding the structure of even a single protein had historically been a multi-year, Nobel-Prize-worthy undertaking. AlphaFold could not simply memorize its way to a solution, because the problem cannot be solved by pattern-matching against a lookup table of known structures — it had to build an internal "theory" (a policy, in this course's vocabulary) of the actual physics: the forces of attraction and repulsion between atoms that determine how a folded chain settles into its final geometry. Trained on roughly a thousand known protein structures with a purely episodic reward (+1 for a correct structure, 0 otherwise — deliberately sparse, exactly the kind of weak signal this week has been arguing RL can nonetheless learn from), AlphaFold 2 went on to determine the structure of essentially every protein known on Earth, more accurately than human scientists — earning its creators the Nobel Prize. It became, in the course's own framing, a "generalization engine": a system that had internalized the *rules* governing protein structure deeply enough to apply them to proteins it had never seen, rather than one that had memorized the specific answers to a thousand training examples.

## Math explained step by step

Formalize why local optimization can miss what trajectory-level optimization finds.

**Step 1 — local (per-move) optimization objective.** A supervised or greedy local approach effectively optimizes $\arg\max_{a} q(s, a)$ at each state $s$ independently, where $q$ is some locally-computable estimate of move quality (material advantage in chess, immediate plausibility in protein folding).

**Step 2 — trajectory-level (RL) optimization objective.** RL instead optimizes $\max_\theta \mathbb{E}_{\tau \sim \pi_\theta}[R(\tau)]$ — the expected reward of the *entire* trajectory the policy generates, which may require choosing an action with low or even negative local $q(s,a)$ at some step, provided that action leads toward states with much higher long-run expected value.

**Step 3 — see why the two can disagree.** If the true value function $V^*(s')$ of the state reached by a "sacrifice" move $a'$ is higher than the value reached by the locally-safer move $a$, then $a'$ is the correct choice even though $q(s, a') < q(s, a)$ under any naive local scoring. A policy trained only to match locally-approved moves (SFT against expert-labeled "best local moves") cannot discover $a'$, because no expert dataset would ever have labeled it as locally correct in the first place — this is precisely the mechanism behind Move 37 being invisible to human experts until its consequences played out.

**Step 4 — generalize the argument beyond games.** The same logic explains why AlphaFold could not have been built as a supervised lookup over known structures: the reward that matters (a chemically and geometrically correct final fold) is a trajectory-level (whole-structure) property, not decomposable into locally-correct per-residue placements that a supervised loss could directly target. The RL formulation — reward the entire folded outcome, let the policy discover the physics-consistent intermediate steps on its own — is what made a genuine generalization engine possible, rather than a rote memorizer of a thousand training examples.

## Practical pattern

1. before assuming a problem can be solved with a locally-scored, supervised approach, ask whether "locally correct" and "eventually correct" can actually diverge in your domain — if a good local heuristic doesn't reliably compose into a good global outcome, this is a signal that trajectory-level RL, not step-level supervision, is the right tool;
2. when a domain expert's per-step judgment is your only available training signal, recognize its structural ceiling explicitly — a policy trained to imitate expert-approved local moves inherits the blind spots of local, human-scale evaluation, and cannot discover a Move-37-style strategy invisible to that same local judgment;
3. treat the AlphaGo-to-AlphaFold transfer as a template for your own work — if you've built RL infrastructure (a policy, a value estimator, a trajectory-level reward) for one problem, actively look for a structurally similar but domain-different problem where the same machinery, not a bespoke rebuild, might transfer;
4. for genuinely sparse-reward problems (a single +1/0 at the very end of a long process, as in AlphaFold), do not assume RL is infeasible just because the signal looks too weak — the course's own examples (the village kiosk, AlphaGo, AlphaFold) are all cases where a sparse but well-defined episodic reward was sufficient to drive extraordinary learning, given enough rollouts.

## Common traps

- assuming a strong local heuristic (material count in chess, plausibility scoring in protein folding) is a safe substitute for genuine trajectory-level optimization, when the two can actively disagree at exactly the moves or steps that matter most;
- treating human expert judgment as a reliable ceiling for training data, when the entire point of trajectory-level RL is its capacity to discover strategies invisible to that same expert judgment;
- dismissing a problem as unlearnable because its reward signal looks too sparse or too delayed, without first checking whether the AlphaGo/AlphaFold pattern (rollout-heavy training against a well-defined, if sparse, episodic reward) genuinely applies;
- treating AlphaGo and AlphaFold as two unrelated success stories rather than one transferable insight — the specific domain-general lesson is that the *same* trajectory-level RL machinery, not two different algorithms, produced both breakthroughs.

## Takeaways

- Supervised, local optimization can be structurally blind to strategies that require a temporarily "worse" local move in service of a much better long-run outcome — Move 37 is the canonical illustration.
- Reinforcement learning's optimization over whole trajectories, not individual steps, is precisely what allows it to discover strategies no human demonstrator ever showed it or could recognize as promising in the moment.
- AlphaFold's breakthrough was not a new algorithm invented from scratch for biology — it was the same RL machinery from AlphaGo, deliberately repurposed onto a domain where trajectory-level reward (a correctly folded structure) similarly could not be decomposed into locally-supervisable steps.
- Sparse, purely episodic rewards (a single +1/0 at the end of a long process) are not disqualifying for RL — both flagship successes covered here used exactly that reward shape, given sufficient rollouts.
