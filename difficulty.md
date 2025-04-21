# FFR Difficulty Axioms

This document defines formal behavioral expectations for difficulty models based on transitions and note timing in FlashFlashRevolution (FFR).

---

## Introduction

An FFR level, or **chart**, is essentially a collection of timed inputs that the player must hit with a certain degree of timing precision in order to maximize their score.

FFR's rhythm game genre is called "4-key", where the inputs are limited to 4 different key bindings on the keyboard. The most common way of playing 4-key, when looking to maximize score, is called **spread**, where the 4 key bindings are played by a separate finger and each hand uses 2 fingers. The key bindings are generally setup in a row-like arrangement, such as "ASKL" or "WEOP".

This document will assume that style of play as it has stood the test of time in being the only style that allows getting anywhere near the best of scores, and is generally the most ergonomic approach to the game. There are _some_ exceptions to that, but the other styles tend to only have better ergonomy in very particular edge cases that would rarely ever be considered _easier_ on entire charts than spread.

## Definitions

### Chart and hits

Lets define some core concepts in order to formalize the meaning of "difficulty" in FFR.

Let the following be a chart made of $n$ **hits**:

$$
C=[x_1, x_2, \dots, x_n]
$$

$$
x=(m, h, r)
$$

A hit $x$ is represented by a 3-tuple of the following values:

- $m \in [0, \infin]$ is the millisecond timing of the hit relative to the start of the song.

- $h \in \{1, 2\}$ denotes the hand used to perform the input for the hit where:
  - $1$: left hand hit;
  - $2$: right hand hit.

- $r \in \{1, 2, 3\}$ denotes the finger(s) representation of a hit where:
  - $1$: **single** on left finger only;
  - $2$: **single** on right finger only;
  - $3$: **jump** (i.e., both fingers pressed simultaneously).

Let the following be selectors for the different values of a hit:

$$
\pi_m(x_i) = m_i,\quad \pi_h(x_i) = h_i,\quad \pi_r(x_i) = r_i
$$

We will make the trivial assumption, for simplicity, that the hits are ordered by time:

$$
\forall i\in[0, n-1],\ \pi_m(x_i) \leq \pi_m(x_{i+1})
$$

This definition of a chart is not the only one; there are other representations that allow different mathematical manipulations. One particularly helpful result of this definition is that it allows for easier representation of **same-hand** elements, which can be isolated from **both-hands** elements. This is especially practical for evaluating spread-specific ergonomy, as each hand has a certain degree of independence while the 2 fingers on a given hand are much less independent mechanically. A hit being represented as $(m, h, r)$ is therefore a natural consequence of the assumption of spread style, as it basically encodes an atomic mechanical movement made by the player.

---

### Same-hand elements

We can now define some of those same-hand elements in order to facilitate the formalizing of features that pertain to only the sequence of hits on a given hand.

Let the following be the subset of all hits in a chart that are on the hand $h$:

$$
C_h = [x \in C \mid \pi_h(x) = h]
$$

$$
n_h = |C_h|
$$

Also, since some elements are based on the relationship between two consecutive hits, lets denote the set of "all hits in a chart except the last hit" as follows for simplicity:

$$
C^*=[x_1, x_2, \dots, x_{n-1}]
$$

#### Gap value

Let the following be the "gap" value $g$, representing the millisecond difference between two consecutive hits on a given hand:

$$
\forall x \in C_h^*,\ g_i = \pi_{g, h}(x_i) = \pi_m(C_h[i]) - \pi_m(C_h[i-1])
$$

$$
g_{n_h} = \pi_{g, h}(x_{n_h}) = \infin
$$

Note that the gap value of the last hit on a given hand is set to $\infin$ as it has no subsequent hit.

This element is very important because the time between two hits on a given hand is an intuitive and logical major contributor to perceived difficulty. Generally, although not _always_, a sequence of hits is perceived as more difficult as the $g$ values are smaller.

#### Hit transition

Next, lets define the "type" of transition between two consecutive same-hand hits as the following:

$$
r_{h,i} = \pi_r(C_h^*[i])
$$

$$
t_i = \begin{cases}
0 & \text{if}\ \  r_{h,i} \in \{1, 2\},\ r_{h,i+1} \in \{1, 2\},\ r_{h,i} \ne r_{h,i+1} \\
1 & \text{if}\ \  r_{h,i} \in \{1, 2\},\ r_{h,i+1} \in \{1, 2\},\ r_{h,i} = r_{h,i+1} \\
2 & \text{if}\ \  r_{h,i} = 3,\ r_{h,i+1} = 1 \\
3 & \text{if}\ \  r_{h,i} = 3,\ r_{h,i+1} = 2 \\
4 & \text{if}\ \  r_{h,i} = 1,\ r_{h,i+1} = 3 \\
5 & \text{if}\ \  r_{h,i} = 2,\ r_{h,i+1} = 3 \\
6 & \text{if}\ \ r_{h,i} = 3,\ r_{h,i+1} = 3
\end{cases}
$$

$$
t_{n_h} = -1
$$

Again, note that the transition value for the last hit is set at $-1$ as an arbitrary value, since there is no subsequent hit to transition to.

This element allows to factor in the different ways a hand can move when transitioning from one hit to the next. It is a widely accepted fact that each type of transition has different implications regarding perceived difficulty, although the exact shape and values for these implications are unknown and not necessarily unanimously agree upon.

Here's what each transition value means in words:

- $0$: single → single _(different finger)_
  - This is commonly refered to as a **trill** motion.*
- $1$: single → single _(same finger)_
  - This is commonly refered to as a **jack** motion.**
- $2$: jump → left single
- $3$: jump → right single
  - These can be categorized as a **jack-like** motions (which $t=1$ also is), and are generally considered to be the least ergonomic motion in spread style.
- $4$: left single → jump
- $5$: right single → jump
  - These can be also categorized as a jack-like motions, and are generally considered to be just slightly more ergonomic than their opposite counterparts $2$ and $3$.
- $6$: jump → jump
  - This is commonly refered to as a **jumpjack** motion, which is another jack-like motion.

Note that:  

\* The word "trill" is slightly overloaded there, as it is generally known to mean _multiple_ such transitions in a row. For now, lets just allow a single such transition to also be labeled that way. More specific contextual terminology will be introduced later if necessary.

\*\* Similarly, "jack" is generally known to mean _multiple_ such transitions. Lets accept a singular one to also be labeled that way.

---

### Difficulty

There are a lot of high level concepts that people naturally refer to when discussing the difficulty of a chart or a section of a chart, or when comparing multiple of those together. The goal here is simply to define basic aspects relating to difficulty, which will be useful when exploring those high level concepts later on.

Let the following denote an unknown function that outputs a single positive real number $d$ that represents difficulty:

$$
D : C \to \reals^+,\quad d = D(C)
$$

The shape of this difficulty function is likely very complicated and probably contains a fair amount of hyperparameters that would attempt to reflect the intricacies of the various human biomechanical aspects of the spread playstyle. Such hyperparameters aren't the focus of this document, however it's good to keep in mind that they're somewhat at the root of a lot of debates over how different aspects of difficulty interact together mathematically and intuitively.

## Axioms

Over the years, there have been many lengthy discussions and debates over how to approach the automatic computation of a chart's difficulty.

### Axiom 1: Monotonicity of Jack-like Transitions

For any chart consisting of a sequence of notes all on the same hand, with identical gap $g$ and a fixed set of jack-like transitions, the difficulty must strictly decrease as the gap increases.

That is, shorter gaps are always more difficult for constant jack-like motion patterns.

#### Formally

Let $D_T(g)$ be the difficulty of a chart with transition set $T$ and gap $g$. Then:

$$
T = \{T_i \in \{1, 2, 3, 4\} \mid 1 \le i \le n,\forall i \in [1, n - 2],\ (T_i, T_{i+1}, T_{i+2}) \notin \{(1, 3, 2), (2, 3, 1)\} \}
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
