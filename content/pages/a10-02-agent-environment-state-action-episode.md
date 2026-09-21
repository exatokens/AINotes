---
id: a10-02-agent-environment-state-action-episode
title: "Agent, Environment, State, Action, Episode: The Core Vocabulary"
week: 10
topic: "Act I: The Vocabulary of Reinforcement Learning"
order: 2
summary: Every reinforcement learning system, from a Roomba to a language model, is described by the same five nouns — agent, environment, state, action, episode — and learning to see them everywhere is the actual skill this week teaches.
course: ai_agents
---

Once you've seen the mouse-cat-cheese story once, you start seeing it everywhere: a Roomba bumping through a room, a rabbit foraging at dawn, a chatbot choosing its next word. That's not a coincidence — it's because reinforcement learning is defined by a small, fixed vocabulary that applies unchanged across wildly different domains. This page is a deliberate act of vocabulary-building: five terms, precisely defined, illustrated across enough different examples that you stop needing the mouse to see the pattern.

The payoff for this vocabulary discipline arrives two pages from now, when the same five terms get mapped directly onto a large language model — the prompt becomes the state, the next token becomes the action, and the whole apparatus of RL becomes available for training agents that speak.

## Core intuition

**Agent**: the entity making decisions — a mouse, a Roomba, a rabbit, eventually a language model. **Environment**: everything the agent observes and acts within — a maze, a room, a forest, a conversation. **State** ($S_t$): the situation the agent finds itself in at time $t$ — where the mouse is in the maze at this moment. **Action** ($a_t$): what the agent does from a "buffet of possible actions" $\{a_0, a_1, \ldots, a_k\}$ available in that state — move forward, move left, stay put. **Episode**: the full sequence from an initial state to a terminal state, where a terminal state is one where no further actions are possible — the mouse gets the cheese, or the mouse becomes cheese.

The loop is continuous: the environment is in state $S_0$; the agent observes $S_0$ and picks action $a_1$; the environment transitions to $S_1$; the agent observes $S_1$, picks $a_2$, and so on, until a terminal state $S_n$ ends the episode.

## Why it matters

Precision here pays off because a subtle but common confusion — episode versus trajectory — trips up otherwise careful engineers. A **trajectory** ($\tau$) is *any* sequence of states and actions, which may be a full episode or only a fragment of one: $S_1 \xrightarrow{a_2} S_2 \xrightarrow{a_3} S_3$ is a valid trajectory but not a full episode unless $S_3$ happens to be terminal. In casual usage, people often use "episode" and "trajectory" interchangeably, and context has to disambiguate — but in the reward mathematics that later pages build (discounting, advantage functions, importance sampling), the distinction between a full episode's reward and a partial trajectory's reward matters for getting the algebra right.

## Instructor framing

Insist that students translate every new RL example they encounter, for the rest of this week and the weeks that follow, into these exact five nouns before doing anything else with it — a habit that pays for itself the moment the vocabulary gets mapped onto language models two pages from now. If a student cannot say, crisply, "here is the state, here is the action space, here is what a terminal state looks like" for a given scenario, no amount of downstream algorithm (policy gradients, PPO, GRPO) will make sense, because those algorithms are all just increasingly sophisticated ways of updating a policy over exactly this vocabulary.

## Worked example

A Roomba in a room: agent is the Roomba; environment is the room's geometry, furniture, and dirt distribution; state is the Roomba's current position and sensor readings; actions are a finite set — move forward, move backward, turn left, turn right, stay put; there is no natural terminal state unless you define one (room fully cleaned, or battery depleted).

A mouse in a maze, seeking cheese and avoiding a cat: agent is the mouse; environment is the maze; state is the mouse's current position; actions are the moves available from that position; the episode is the full path from the mouse's starting position to a terminal state, of which there are exactly two kinds — **cheese** (a positive terminal state) and **"be cheese"** (a negative terminal state, i.e., caught by the cat). Every episode ends in exactly one of these two ways, and the whole path — $S_0 \xrightarrow{a_1} S_1 \xrightarrow{a_2} \cdots \xrightarrow{a_n} S_n$ — is the episode, while any sub-sequence of it, like just the last three states, is merely a trajectory.

## Math explained step by step

Quantify how the size of the action space and the length of an episode compound to define the real difficulty of a problem.

**Step 1 — count the raw trajectory space.** If the action space has $k$ actions available at each step, and an episode runs for $n$ steps before hitting a terminal state, the number of *possible* distinct trajectories is on the order of $k^n$ — this grows exponentially in episode length even for a modest action set.

**Step 2 — see why this matters for exploration.** A mouse maze with $k = 4$ moves per step and an episode length of $n = 20$ has up to $4^{20} \approx 1.1 \times 10^{12}$ possible trajectories — an astronomically large space for trial-and-error to search blindly, which is exactly why raw random exploration is an impractical learning strategy on its own, and why later pages introduce a *policy* (a learned, non-uniform distribution over actions) to concentrate search where reward is more likely.

**Step 3 — relate episode length to credit-assignment difficulty.** The longer $n$ is before a terminal state (and its associated reward) arrives, the more individual actions $a_1, \ldots, a_n$ must share credit or blame for that single eventual outcome — this is the seed of the credit assignment problem developed formally two pages ahead, and it scales directly with $n$: doubling episode length roughly doubles the number of actions competing for credit from one reward signal.

**Step 4 — the practical takeaway from the arithmetic.** Environments with short episodes and small action spaces are comparatively easy for RL to learn from; environments with long episodes and large action spaces (language generation, with a vocabulary-sized action space and episodes hundreds of tokens long) are precisely where the more sophisticated machinery — policy gradients, discounting, advantage functions — earns its keep, because brute-force trajectory enumeration is hopeless at that scale.

## Practical pattern

1. for any new agentic problem, write down the five nouns explicitly before writing any code: what exactly is the agent, what exactly is the environment, what is a state, what is the action space, what counts as a terminal state;
2. check whether the state definition is *sufficient* — does it contain everything the agent needs to decide its next action, or is relevant history missing? An insufficient state definition (the Markov property violated) silently degrades every downstream algorithm;
3. estimate the rough size of the trajectory space ($k^n$) for your problem before choosing a training approach — this ballparks whether blind exploration is remotely feasible or whether you need strong priors (a good starting policy, dense reward shaping) to make learning tractable at all;
4. explicitly distinguish, in your own notes and in any team communication, "episode" (full run to a terminal state) from "trajectory" (any sub-sequence) — sloppy use of these terms is a common source of bugs when computing rewards and advantages later.

## Common traps

- defining a state that omits information the agent actually needs to act well, then being surprised the learned policy behaves inconsistently — this is a state-design bug, not a learning-algorithm bug;
- confusing "episode" and "trajectory" when writing or reading reward equations, leading to off-by-one or scope errors in what a given reward term is actually summed over;
- underestimating how explosively $k^n$ grows for long-horizon, large-action-space problems, and being surprised when naive exploration fails to find good behavior in any reasonable amount of training time;
- assuming every environment has a natural terminal state — many real agentic tasks (a customer-support conversation, an ongoing monitoring agent) don't terminate cleanly, and the episode boundary itself has to be a deliberate design choice.

## Takeaways

- Every RL system is described by five nouns: agent, environment, state, action, and episode — and translating a new problem into these terms explicitly is a prerequisite for applying any RL algorithm to it correctly.
- An episode is the full run from an initial state to a terminal state; a trajectory is any sub-sequence of states and actions, which may or may not be a complete episode — the distinction matters once reward mathematics enters.
- The size of the trajectory space grows exponentially in both action-space size and episode length, which is the structural reason long-horizon, large-action-space problems (like language generation) need more sophisticated machinery than blind trial and error.
- This same vocabulary maps directly onto large language models two pages ahead — the mapping is not an analogy, it is a literal substitution of terms.
