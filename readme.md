# FFR Difficulty Axioms

This document defines formal behavioral expectations for difficulty models based on transitions and note timing.

---

## Definitions

- Let $D(\dots)$ denote an unknown function that outputs a single real number $d$ that represents difficulty.
- Let $D_t(g)$ denote the difficulty of a chart consisting of a sequence of same-hand hits with transitions of type $t$ with fixed gap $g$ and fixed length $n$.
- Let $g\in[1, \infin]$ be gap values, from one hit to the next, in milliseconds.
- Let $t\in\{0, 1, 2, 3, 4\}$ denote same-hand transition types to the next hit:
  - $0$: single → single (different finger)
  - $1$: single → single (same finger)
  - $2$: jump → single
  - $3$: single → jump
  - $4$: jump → jump
- Let $h$ denote the hand to consider such that:
  - $1$: left hand
  - $2$: right hand

---

## Axiom 1: Monotonicity of Jack-like Transitions

For any chart consisting of a sequence of notes all on the same hand, with identical gap $g$ and a fixed set of jack-like transitions, the difficulty must strictly decrease as the gap increases.

That is, shorter gaps are always more difficult for constant jack-like motion patterns.

### Formally

Let $D_T(g)$ be the difficulty of a chart with transition set $T$ and gap $g$. Then:

$$
T = \{T_i \in \{1, 2, 3, 4\} \mid 1 \leq i \leq n\}
$$
$$
\forall g_1, g_2\in[1, \infin]\ ,g_1<g_2 \Rightarrow D_T(g_1) > D_T(g_2)
$$

## Axiom 2: Monotonicity of Alternating Singles with Gap > 100ms

For any chart consisting of a sequence of alternating singles, so constant transition type $t=0$, all on the same hand, with a fixed gap $g > 100$ ms, the difficulty must strictly decrease as the gap increases.

That is, as alternating notes approach the manipulation threshold of 100ms, the difficulty increases. As they move further apart, the difficulty decreases.

### Formally

Let $D_t(g)$ be the difficulty of a chart with alternating singles at gap $g$. Then:

$$
\forall g_1,g_2\in[100, \infin]\ ,g_1<g_2\Rightarrow D_t(g_1)>D_t(g_2)
$$

## Axiom 3: Monotonicity of Repetition

For any chart consisting of a sequence of a single transition type (or a consistent alternating motion such as $T = [2, 3, 2, 3, ...]$) with fixed gap $g$, the difficulty must strictly increase as the number of repeated transitions increases.

That is, longer repetitive motions (e.g., 20-note jacks) are always more difficult than shorter ones (e.g., 10-note jacks), assuming the motion type and gap are the same.

### Formally

Let $D_t(g, n)$ be the difficulty of a chart with fixed transition type $t$, fixed gap $g$, and $n$ repeated such transitions. Then:

$$
\forall t\in\{0, 1, 2, 3, 4\},\ \forall g\in [1, \infty],\ \forall n_1<n_2,\quad D_t(g, n_1)<D_t(g, n_2)
$$

Note that the increase in difficulty may saturate:

$$
\frac{\partial D_t(g, n)}{\partial n} \ge 0,\quad
\frac{\partial^2 D_t(g, n)}{\partial n^2} \le 0
$$

This captures the idea that while difficulty increases with repetition, the rate of increase may diminish over time.
