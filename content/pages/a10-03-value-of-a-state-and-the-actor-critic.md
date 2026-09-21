---
id: a10-03-value-of-a-state-and-the-actor-critic
title: "The Value of a State, and Why the Actor Needs a Critic"
week: 10
topic: "Act I: The Vocabulary of Reinforcement Learning"
order: 3
summary: The value of a state is the expected reward of every trajectory starting there, and separating a Critic that judges states from an Actor that picks actions is the architectural move that makes learning tractable.
course: ai_agents
---

Two people play the same fair, unregulated stock market — a true random walk, no rigging, no insider information. Player one starts with $100. Player two starts with $100,000. Ask which player is in the better position and the honest answer isn't "they're equal because the game is fair" — it's "the second player, by a huge margin," because a "fair game" is not the same as a "fair starting position." Player two can survive a streak of ten consecutive bad events that would bankrupt player one outright; the probability of the ten thousand consecutive bad events needed to actually bankrupt player two is practically zero. The game's rules never favored anyone — but the *state* each player started in already determined most of the outcome.

This is the intuition behind one of reinforcement learning's most load-bearing concepts: the value of a state. This page defines it formally, and introduces the actor-critic architecture that falls naturally out of taking it seriously.

## Core intuition

The **value of a state**, $V(s)$, is the expected (average) reward of all trajectories that start from that state, under the current policy: $V(s) = \mathbb{E}_\pi[R(\tau) \mid S_t = s]$. A state near the cheese has high value because most trajectories starting there end well; a state near the cat has low value because most trajectories starting there end badly — even before any specific action is chosen.

This gives rise to a natural two-role split. The **Actor** is the agent taking actions — the climber choosing a direction, the driver choosing a lane. The **Critic** is a separate function estimating the value of the state the actor's action just produced, providing a running assessment of "how good is where you just put yourself," independent of whether the final outcome (still pending) turns out well or badly.

## Why it matters

Separating actor and critic solves a real problem: without some notion of state value, an agent has no way to judge an action's quality *before* an episode fully terminates — it would have to wait for the final cheese-or-cat outcome to learn anything, discarding all the useful signal available at every intermediate step. With a critic estimating $V(s)$ at each step, the actor gets a dense, immediate learning signal — "that action moved you to a higher-value state" or "that action moved you to a lower-value state" — long before the episode concludes. This is what makes actor-critic methods far more sample-efficient than waiting for episode-end rewards alone.

The definition of value also has a subtlety worth sitting with: value is not simple distance to a goal. On a mountain, a state's altitude is a natural first guess at value, but a lower-altitude state $\gamma$ that happens to be *closer to the peak* might genuinely be more valuable than a higher-altitude state $\beta$ that dead-ends. Choosing how to define value — pure altitude versus something more like "eventual expected reward" — is itself a design decision, not a given.

## Instructor framing

Use the driving analogy to make the actor-critic split viscerally concrete before formalizing it: driving west from Fremont toward Pacifica along Highway 92, every step forward improves your state's value — you're more proximal to your destination, a genuinely good action. But at the T-junction near the cliff, continuing the *same* action (going straight, "west") drives you into the sea — a terminal state of catastrophically negative value. The lesson to draw explicitly: the quality of an action is entirely relative to the value of the state it produces, not some fixed property of the action itself ("go west" was excellent for nineteen steps and fatal on the twentieth). This reframing — judge actions by the states they lead to, not by the actions in isolation — is the conceptual seed of the advantage function developed in later weeks.

## Worked example

Consider two states in the mouse-cat-cheese maze: state $X$, very close to the cat, and state $Y$, very close to the cheese. Intuitively $V(X) < V(Y)$. To make this rigorous rather than just intuitive: enumerate all possible trajectories starting from $X$ — most of them, statistically, run into the cat, so their average reward is low. Enumerate all trajectories starting from $Y$ — most of them reach the cheese, so their average reward is high. Formally, $\mathbb{E}_\pi[R(\tau) \mid S_t = x] < \mathbb{E}_\pi[R(\tau) \mid S_t = y]$ — this expectation-over-trajectories *is* the formal definition of state value, not a metaphor for it.

Now revisit the stock-market example through this lens: the "state" is a player's current wealth, and its value under a fair-game policy is the expected outcome of continuing to play from there. Because ruin is an absorbing (terminal, zero-value) state and a large wealth buffer makes reaching that absorbing state from many consecutive bad draws exponentially unlikely, the $100,000 state has dramatically higher value than the $100 state — not because the game favors the rich, but because value is a property of the *starting state*, propagated forward through the dynamics of the game, not a property of the rules alone. This is, incidentally, the mathematical core of the real debate between unregulated and regulated markets: the rules can be perfectly fair and the outcomes can still be wildly unequal, purely as a function of unequal starting-state values.

## Math explained step by step

Work through the value definition and its actor-critic implication precisely.

**Step 1 — the value function.** $V^\pi(s) = \mathbb{E}_{\tau \sim \pi}[R(\tau) \mid S_0 = s]$: the expected total reward of trajectories generated by policy $\pi$, starting from state $s$. This is an expectation over the *policy's own* behavior, so a better policy produces a higher $V^\pi(s)$ for the same underlying environment.

**Step 2 — why waiting for episode-end reward alone is inefficient.** Without $V$, the only training signal available is the final $R(\tau)$ once an episode terminates — every intermediate action must wait for that one distant number, diluted across every action taken during the episode (the credit assignment problem from the previous page, restated).

**Step 3 — the critic supplies a proxy signal at every step.** If the critic can estimate $\hat{V}(s)$ reasonably well, then the actor can be trained using the *change* in estimated value from one step to the next, $\hat{V}(S_{t+1}) - \hat{V}(S_t)$, as an immediate, dense learning signal — available at every single step, not just at episode end.

**Step 4 — this is exactly what "actor-critic" names.** The Actor is a policy $\pi_\theta(a \mid s)$ choosing actions; the Critic is a separate function $\hat{V}_\phi(s)$ (with its own parameters $\phi$, trained to predict actual observed returns) providing the per-step feedback the actor uses to improve. Two learning problems, two parameter sets, one shared loop — this is the architectural skeleton underneath every more advanced algorithm this course covers later (PPO, GRPO, and the rest all build on some version of this actor/critic or actor/reward split).

## Practical pattern

1. whenever an agentic system's only feedback is a final, episode-end outcome, treat "can I define a useful intermediate value estimate" as the first design question — a good critic turns a sparse, delayed signal into a dense, immediate one;
2. choose your value definition deliberately, the way the mountain example warns — a naive proxy (pure altitude, pure token count, pure distance-to-goal) can rank two states incorrectly if it ignores what actually determines eventual reward;
3. remember that value is policy-relative, not environment-absolute — $V^\pi(s)$ changes as $\pi$ improves, so a critic trained against an old, weaker policy's behavior will systematically misjudge states once the actor gets better, and needs to be retrained alongside it;
4. use the driving/cliff example as a debugging heuristic: if an agent seems to be doing "the same reasonable thing" right up until catastrophic failure, check whether your reward or value signal actually penalizes the terminal outcome sharply enough to outweigh many prior steps of locally-good-looking behavior.

## Common traps

- judging actions in isolation rather than by the value of the state they produce — an action that was good nineteen times can be catastrophic the twentieth time, and only value-of-resulting-state judges this correctly;
- choosing a convenient but wrong proxy for value (like pure distance or pure altitude) and then being confused when the learned policy behaves "greedily" in a way that misses better long-term outcomes;
- forgetting that value estimates are policy-relative and go stale as the policy improves, leading to a critic that lags behind and gives systematically miscalibrated feedback;
- assuming a dense reward signal isn't needed because "the final outcome is what matters" — this discards the entire efficiency gain that a well-trained critic provides over waiting for episode-end reward alone.

## Takeaways

- The value of a state, $V^\pi(s)$, is the expected reward of trajectories starting from that state under the current policy — not a fixed property of the environment, but a property of state *and* policy together.
- Two states can have very different value even under identical, perfectly fair dynamics, purely because of how many bad outcomes each can absorb before hitting a terminal (ruinous) state.
- The actor-critic split — one component choosing actions, a separate component estimating state value — converts a sparse, episode-end-only reward signal into a dense, per-step one, and underlies essentially every advanced RL algorithm covered later in the course.
- Value must be defined deliberately; naive proxies like raw distance or altitude can misrank states relative to what actually predicts eventual reward.
