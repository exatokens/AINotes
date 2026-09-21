---
id: a13-03-non-stationarity-and-ctde
title: "Non-Stationarity and CTDE: Why Multi-Agent Worlds Move While You Reason"
week: 13
topic: "Act I: Coordinating Many Minds"
order: 3
summary: A multi-agent environment changes for reasons unrelated to your own actions, invalidating the single-agent assumption that made earlier RL math tractable — Centralized Training, Decentralized Execution is the industry's answer, trained like a master chef overseeing many independent cooks.
course: ai_agents
---

Ten Roomba robots share a single room, and each independently spots the same pile of dirt at the same moment. Each, reasoning entirely on its own, concludes that rushing toward the dirt is the optimal action — and by the time they arrive, they collide, creating a pileup and wasting far more effort than if any single one of them had simply gone alone. No individual Roomba reasoned incorrectly. Each one's private observation, taken in isolation, genuinely justified its action. What broke was an assumption none of them knew they were making: that the room would still look the way they last observed it by the time their action executed. This is the defining technical challenge of multi-agent reinforcement learning, and this page names it precisely and works through the architecture — Centralized Training, Decentralized Execution — the field has converged on to address it.

## Core intuition

Every single-agent RL formulation covered earlier in this course quietly assumed a **stationary environment**: a state that changes only in response to *the agent's own actions*, formalized as a Markov Decision Process where $S_{t+1}$ depends only on $S_t$ and the agent's own action $a_t$. In a multi-agent setting, this assumption breaks: the environment is **non-stationary**, because it changes as a result of *every* agent's actions simultaneously, not just your own — from any single agent's perspective, the state transition probabilities are not fixed, because they depend on what other independently-acting agents are doing at the same time.

The industry's answer is **CTDE — Centralized Training, Decentralized Execution**: during training, a central component observes the *global* state across all agents and can see the full consequences of their joint actions, allowing genuine coordination to be learned; during actual deployment (execution), each agent acts autonomously and locally, using only what it learned during centralized training, without needing that global view moment to moment.

## Why it matters

Non-stationarity is not a minor technical caveat — it is the reason naive single-agent training, applied independently to each agent in a team, systematically fails to produce coordination. If each agent is trained purely against its own local observations, as if the rest of the environment were stationary, it will learn a policy that is locally sensible but globally uncoordinated — exactly the Roomba pileup, or the "key in the room" problem: an agent observes a key on a table and reasons "I'll pick it up later," but if a second agent moves the key in the meantime, the first agent's reasoning was correct when made and is simply obsolete by the time it acts. CTDE resolves this by giving the *training* process the global information individual agents cannot have at execution time, without requiring that same global information to be available (with its associated communication and latency cost) once the system is actually deployed.

## Instructor framing

Use the kitchen metaphor as the throughline for this entire page, because it makes the training/execution split viscerally concrete: picture a Master Chef (the centralized Critic) overseeing a kitchen full of cooks, each independently cutting carrots, boiling water, preparing dessert. During training, the Chef sees everything — if the carrot cake as a whole fails, an individual cook stirring their own pot has no way to know why, but the Chef, watching the global outcome, can trace the failure and correct it. Sometimes this correction is drastic: a real anecdote in the course describes a wedding carrot cake where too much milk had been added and wasn't evaporating — the "Chef," using centralized authority, scooped out the excess milk, poured it into cups, and had everyone drink it to save the cake on schedule, a correction no individual cook stirring their own portion could have made or even perceived the need for. Once training is complete, the Chef leaves — during the actual dinner rush (execution), each cook has internalized an "embedded policy" and acts autonomously, the carrot cook instinctively cutting to the right size without further central instruction, yet the overall result remains coordinated because that coordination was baked in during training.

## Worked example

Not every coordinated multi-agent behavior requires explicit MARL training at all — a useful and sometimes cheaper alternative is **implicit coordination**, which shows up naturally in two very different settings. In nature, a flock of geese exhibits a clear structure (a leader, followers, young protected at the tail) and reacts to a predator with an optimal fanning strategy, all without any explicit verbal negotiation, because "evolutionary reinforcement learning" — a brutally effective training process where the penalty for a bad policy is literally death — has embedded an optimal coordination policy into the species over countless generations. In AI systems, research into generative agent "simulacra" found that LLM agents could convincingly simulate a town of interacting humans *without* any centralized critic or explicit MARL training at all, because the underlying models were already so thoroughly trained on human sociological dynamics from their pre-training data that they could "roleplay" coordinated social interaction correctly by drawing on patterns they had already internalized. Both examples are a genuine caveat to CTDE's necessity: when the needed coordination pattern is already implicitly present in a system's prior training or evolutionary history, explicit centralized-training infrastructure may be unnecessary overhead.

## Math explained step by step

Formalize the stationary-versus-non-stationary distinction, and show precisely why it breaks single-agent RL's convergence guarantees.

**Step 1 — the single-agent (stationary) MDP.** A standard MDP is defined by $(S, A, P, R, \gamma)$, where the transition function $P(S_{t+1} \mid S_t, a_t)$ depends only on the current state and the *single* agent's own action — this fixed, agent-independent transition structure is exactly what makes single-agent policy-gradient convergence proofs (and the REINFORCE derivation from Week 11) valid.

**Step 2 — the multi-agent case introduces other agents' parameters into the transition.** With $n$ agents, the true transition is $P(S_{t+1} \mid S_t, a_t^{(1)}, \ldots, a_t^{(n)})$ — dependent on the *joint* action of all agents. From agent $i$'s local perspective, holding only its own action fixed, the effective transition it experiences is $P(S_{t+1} \mid S_t, a_t^{(i)}) = \sum_{a^{(-i)}} P(S_{t+1}\mid S_t, a_t^{(i)}, a^{(-i)}) \cdot \pi^{(-i)}(a^{(-i)} \mid S_t)$ — a transition that depends explicitly on the *other* agents' policies $\pi^{(-i)}$.

**Step 3 — see why this breaks stationarity as training proceeds.** Because every other agent's policy $\pi^{(-i)}$ is *also being updated* during training, the effective transition function agent $i$ experiences keeps changing underneath it, purely as a side effect of other agents' learning — even if agent $i$'s own policy and the "true" environment mechanics never change. This is precisely what "non-stationary from any single agent's perspective" means formally: the single-agent convergence guarantees that assumed a fixed $P$ simply do not apply when $P$'s effective form is itself shifting as training proceeds.

**Step 4 — CTDE's mathematical fix.** During centralized training, a critic conditions its value estimate on the *joint* state and joint actions of all agents, $V(S_t, a_t^{(1)}, \ldots, a_t^{(n)})$, restoring a well-defined, non-shifting quantity to train against, since the joint-action space, unlike any single agent's local view, fully determines the next state. Each agent's policy is then trained using gradients derived from this joint-aware critic, while remaining, architecturally, a function of only its own local observation — so at execution time, with the joint-aware critic discarded, each agent can still act using only what it can locally observe, having had its policy shaped during training by information it will not have access to afterward.

## Practical pattern

1. before training multiple agents to act as a team, explicitly check whether their combined action space genuinely creates non-stationarity from any single agent's perspective — some multi-agent-looking problems (each agent independently pursuing unrelated goals with no shared consequences) do not actually require CTDE machinery at all;
2. when non-stationarity is real, invest in a centralized critic during training that observes the full joint state and joint actions, even if each individual agent's deployed policy remains strictly local — this is the CTDE pattern, not an optional refinement of it;
3. consider whether implicit coordination (already-present in a strong pre-trained model, or achievable via evolutionary/imitation shortcuts) might be sufficient before building explicit centralized-training infrastructure — it is a real, cheaper option in some settings, not just a theoretical curiosity;
4. design for the training/execution asymmetry deliberately: your centralized critic's information requirements at training time should not become a hidden runtime dependency at deployment time, or you have not actually built a decentralized-execution system.

## Common traps

- training multiple agents independently, each against its own local observations as if the environment were stationary, and being surprised when the resulting team behavior is locally sensible but globally uncoordinated (the Roomba pileup, the "three people making soup" kitchen chaos);
- assuming a single-agent RL algorithm's convergence guarantees transfer unchanged to a multi-agent setting, without accounting for the fact that other agents' concurrently-updating policies make the effective environment non-stationary from each agent's perspective;
- building full CTDE infrastructure for a multi-agent problem that doesn't actually require it — some tasks are non-stationary in name only, and the added engineering cost of centralized training is unjustified;
- accidentally smuggling centralized, global information into a deployed "decentralized" agent's runtime inputs, defeating the entire purpose of the CTDE split and reintroducing a hidden coordination dependency that won't scale or generalize the way genuine local execution would.

## Takeaways

- Multi-agent environments are non-stationary from any single agent's perspective, because the effective transition dynamics depend on other agents' concurrently-changing policies, not just the environment's fixed mechanics — this breaks the assumptions underlying single-agent RL convergence guarantees.
- Centralized Training, Decentralized Execution (CTDE) resolves this by training a critic that sees the full joint state and joint actions of all agents, while keeping each deployed agent's policy a function of only its own local observations.
- Implicit coordination — geese flocking, LLM agents roleplaying social dynamics from pre-training — is a real, sometimes sufficient alternative to explicit CTDE machinery, worth checking for before building the more expensive centralized-training infrastructure.
- The kitchen metaphor (a Master Chef training cooks, then stepping back during the dinner rush) captures CTDE's core asymmetry precisely: global information is available and used during training, and deliberately withheld — because it's genuinely unavailable — during execution.
