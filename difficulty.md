# FFR Difficulty Axioms

This document defines formal behavioral expectations for difficulty models based on transitions and note timing in FlashFlashRevolution (FFR).

---

## Introduction

An FFR level, or **chart**, is essentially a collection of timed inputs that the player must hit with a certain degree of timing precision in order to maximize their score.

FFR's rhythm game genre is called "4-key", where the inputs are limited to 4 different key bindings on the keyboard. The most common way of playing 4-key, when looking to maximize score, is called **spread**, where the 4 key bindings are played by a separate finger and each hand uses 2 fingers. The key bindings are generally setup in a row-like arrangement, such as "ASKL" or "WEOP".

This document will assume that style of play as it has stood the test of time in being the only style that allows getting anywhere near the best of scores, and is generally the most ergonomic approach to the game. There are _some_ exceptions to that, but the other styles tend to only have better ergonomy in very particular edge cases that would rarely ever be considered _easier_ on entire charts than spread.

## Definitions

Let's define some core concepts in order to be able to formalize the meaning of "difficulty" in FFR.

### Chart

#### Hit-based

Let the following be a chart made of $n$ **hits**:

$$
C=[x_0, x_1, x_2, \dots, x_{n-1}]
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

For robustness sake, let's constrain that definition to not contain any set of hits that share the same $m$ and $h$ value:

$$
\forall i, j \in [0, n-1],\ i \ne j \Rightarrow (\pi_m(x_i), \pi_h(x_i)) \ne (\pi_m(x_j), \pi_h(x_j))
$$

This will ensure that the charts are valid and don't have anomalous features, even though such invalid charts are _technically_ possible to create for the game; there's no benefit to considering them in this document.

We will also make the trivial assumption, for simplicity, that the hits are ordered by time:

$$
\forall i\in[0, n-2],\ \pi_m(x_i) \leq \pi_m(x_{i+1})
$$

Now since some elements defined below are based on the relationship between two consecutive hits, let's denote the set of "all hits in a chart except the last hit" as follows for simplicity:

$$
C^*=[x_0, x_1, x_2, \dots, x_{n-2}]
$$

This hit-based definition of a chart is not the only one; there are other representations that allow different mathematical manipulations. One particularly helpful result of this definition is that it allows for easier representation of **same-hand** elements, which can be isolated from **both-hands** elements. This is especially practical for evaluating spread-specific ergonomy, as each hand has a certain degree of independence while the 2 fingers on a given hand are much less independent mechanically. A hit being represented as $(m, h, r)$ is therefore a natural consequence of the assumption of spread style, as it basically encodes an atomic mechanical movement made by the player.

#### Note-based

Another chart representation that will also be useful is the following:

$$
\Phi = [\nu_0, \nu_1, \nu_2, \cdots, \nu_{\eta-1}]
$$

$$
\nu = (m, l)
$$

This representation denotes a chart $\Phi$ as a sequence of $\eta$ **notes**. Each note $\nu$ is a simple tuple of the following values:

- $m \in [0, \infin]$ is the millisecond timing of the note relative to the start of the song. This is identical to the $m$ value of a hit.

- $l \in \{1, 2, 3, 4\}$ denotes the **lane** of the note. More visually, each value represents a finger in a spread playstyle setup from left to right. As an example, with key bindings "ASKL", $1$ would be "A", $2$ would be "S", $3$ would be "K" and $4$ would be "L".

Again, let's define selectors for these values:

$$
\pi_m(\nu_i) = m_i,\quad \pi_l(\nu_i) = l_i
$$

The chart validity constraint of this form is more straightforward:

$$
\forall i, j \in [0, \eta-1],\ i \ne j \Rightarrow \nu_i \ne \nu_j
$$

While the hit-based representation is particularly helpful for formalizing concepts that are more centered around ergonomy of play, this note-based one will be helpful for concepts that are more related to the game's specific mechanics.

#### Equivalency of representations

To ensure that all definitions derived from either representation is applicable to the other, there needs to be a formal mapping between the two.

Let's first define special selectors of a note that return elements of a hit:

$$
\Pi_m(\nu) = \pi_m(\nu)
$$

$$
\Pi_h(\nu) =
\begin{cases}
1 & \text{if}\quad \pi_l(\nu) \in \{1, 2\} \\
2 & \text{if}\quad \pi_l(\nu) \in \{3, 4\} \\
\end{cases}
$$

$$
\Pi_r(\nu) =
\begin{cases}
1 & \text{if}\quad \pi_l(\nu) \in \{1, 3\} \\
2 & \text{if}\quad \pi_l(\nu) \in \{2, 4\} \\
\end{cases}
$$

Then, the selectors of a hit that return elements of a note:

$$
\Pi_m(x) = \pi_m(x)
$$

$$
\Pi_l(x) =
\begin{cases}
\{1\} & \text{if}\quad \pi_h(x) = 1\quad \text{and}\quad \pi_r(x) = 1 \\
\{2\} & \text{if}\quad \pi_h(x) = 1\quad \text{and}\quad \pi_r(x) = 2 \\
\{3\} & \text{if}\quad \pi_h(x) = 2\quad \text{and}\quad \pi_r(x) = 1 \\
\{4\} & \text{if}\quad \pi_h(x) = 2\quad \text{and}\quad \pi_r(x) = 2 \\
\{1, 2\} & \text{if}\quad \pi_h(x) = 1\quad \text{and}\quad \pi_r(x) = 3 \\
\{3, 4\} & \text{if}\quad \pi_h(x) = 2\quad \text{and}\quad \pi_r(x) = 3 \\
\end{cases}
$$

Using all these selectors, let's now define mappings of hits to notes and vice versa.

##### Hits to notes

The mapping from hits to notes can result in either one or two notes depending on if the finger type of the hit is a single ($1$ or $2$) or a jump ($3$). Let's define the function $\phi$ as the transformer of a hit-based chart to a note-based chart.

$$
\phi : C \to \Phi,\quad \Phi = \phi(C)
$$

$$
\phi(C) = \bigcup_{x \in C} \{ ( \Pi_m(x),\ l ) \mid l \in \Pi_l(x) \}
$$

##### Notes to hits

The opposite mapping however (from notes to hits) is slightly less straightforward due to the possibility of having to merge pairs of notes that would result in a singular jump hit.

Let the following set $\Phi_t$ be the set of all notes in chart $\Phi$ that have a millisecond timing $t$, where $t$ is taken from the set $T$ of all unique timings of the chart's notes:

$$
T = \{\pi_m(\nu) \mid \nu \in \Phi\}
$$

$$
\forall t \in T,\quad \Phi_t = \{ \nu \in \Phi \mid \pi_m(\nu) = t \}
$$

This grouping of notes completely partitions the chart, so whatever action is taken over all such partitions of a given chart is guaranteed to cover all notes too. More formally:

$$
\Phi = \bigsqcup_{t \in T} \Phi_t
$$

Then, there needs to be a way to transform a single partition of notes into one or more hits. The mapping below does that:

$$
L_h = \{\nu \in \Phi_t \mid \Pi_h(\nu) = h \}
$$

$$
x(\Phi_t) =
\bigcup_{h \in \{1, 2\}}
\begin{cases}
\emptyset & \text{if}\quad |L_h| = 0 \\
\{ (t, h, \Pi_r(\nu)) \} & \text{if}\quad |L_h| = 1 \\
\{ (t, h, 3) \} & \text{if}\quad |L_h| = 2 \\
\end{cases}
$$

With all of that, it becomes possible to map all partitions to hits, merging notes where needed. Let's define the function $\chi$ as the transformer of a note-based chart to a hit-based chart:

$$
\chi : \Phi \to C,\quad C = \chi(\Phi)
$$

$$
\chi(\Phi) = \bigcup_{t \in T} x(\Phi_t)
$$

##### Final equivalency of chart representations

With the transformer functions defined above, there is a complete bidirectional mapping. This mapping can be written as such:

$$
\chi : \Phi \rightarrow C,\quad \phi : C \rightarrow \Phi
$$

$$
\chi(\phi(C)) = C,\quad \phi(\chi(\Phi)) = \Phi
$$

The step-by-step proof of this mapping relies on the defined chart constraints and would be somewhat lengthy, so it is left out to keep things more concise.

---

### Same-hand elements

We can now define some important same-hand elements in order to facilitate the formalizing of features that pertain to only the sequence of hits on a given hand.

Let the following be the subset of all hits in a chart that are on the hand $h$:

$$
C_h = [x \in C \mid \pi_h(x) = h]
$$

$$
n_h = |C_h|
$$

#### Gap value

Let the following be the **gap** value $g$, representing the millisecond difference between two consecutive hits on a given hand:

$$
\forall x \in C_h^*,\ g_i = \pi_{g, h}(x_i) = \pi_m(C_h[i]) - \pi_m(C_h[i-1])
$$

$$
g_{n_h} = \pi_{g, h}(x_{n_h}) = \infin
$$

Note that the gap value of the last hit on a given hand is set to $\infin$ as it has no subsequent hit.

This element is very important because the time between two hits on a given hand is an intuitive and logical major contributor to perceived difficulty. Generally, although not _always_, a sequence of hits is perceived as more difficult as the $g$ values are smaller.

#### Hit transition

Next, let's define the "type" of transition between two consecutive same-hand hits as the following:

$$
r_{h,i} = \pi_r(C_h^*[i])
$$

$$
t_i = \begin{cases}
0 & \text{if}\quad r_{h,i} \in \{1, 2\},\ r_{h,i+1} \in \{1, 2\},\ r_{h,i} \ne r_{h,i+1} \\
1 & \text{if}\quad r_{h,i} \in \{1, 2\},\ r_{h,i+1} \in \{1, 2\},\ r_{h,i} = r_{h,i+1} \\
2 & \text{if}\quad r_{h,i} = 1,\ r_{h,i+1} = 3 \\
3 & \text{if}\quad r_{h,i} = 2,\ r_{h,i+1} = 3 \\
4 & \text{if}\quad r_{h,i} = 3,\ r_{h,i+1} = 1 \\
5 & \text{if}\quad r_{h,i} = 3,\ r_{h,i+1} = 2 \\
6 & \text{if}\quad r_{h,i} = 3,\ r_{h,i+1} = 3
\end{cases}
$$

$$
t_{n_h} = -1
$$

Again, note that the transition value for the last hit is set at $-1$ as an arbitrary value, since there is no subsequent hit to transition to.

This element allows to factor in the different ways a hand can move when transitioning from one hit to the next. It is a widely accepted fact that each type of transition has different implications regarding perceived difficulty, although the exact shape and values for these implications are unknown and not necessarily unanimously agreed upon.

Here's what each transition value means in words:

- $0$: single → single _(different finger)_
  - This is commonly refered to as a **trill** motion.*
- $1$: single → single _(same finger)_
  - This is commonly refered to as a **jack** motion.**
- $2$: left single → jump
- $3$: right single → jump
  - These can be categorized as a **jack-like** motions (which $t=1$ also is), and are generally considered to be the least ergonomic motion in spread style.
- $4$: jump → left single
- $5$: jump → right single
  - These can be also categorized as a jack-like motions, and are generally considered to be just slightly more ergonomic than their opposite counterparts $2$ and $3$.
- $6$: jump → jump
  - This is commonly refered to as a **jumpjack** motion, which is another jack-like motion.

Note that:  

\* The word "trill" is slightly overloaded there, as it is generally known to mean _multiple_ such transitions in a row. For now, let's just allow a single such transition to also be labeled that way. More specific contextual terminology will be introduced later if necessary.

\*\* Similarly, "jack" is generally known to mean _multiple_ such transitions. Let's accept a singular one to also be labeled that way.

---

### Scoring

It is essential to formally define FFR's scoring system so that we can relate the difficulty concepts to the players' goal during gameplay. Nowadays, and for many years now, that scoring system has been an accuracy based one where the players attempt to get a "AAA" or as close to it as they can.

The "

---

### Difficulty

There are a lot of high level concepts that people naturally refer to when discussing the difficulty of a chart or a section of a chart, or when comparing multiple of those together. The goal here is simply to define basic aspects relating to difficulty, which will be useful when exploring those high level concepts later on.

Let the following denote an unknown function that outputs a single positive real number $d$ that represents difficulty:

$$
D : C \to \reals^+,\quad d = D(C)
$$

The shape of this difficulty function is likely very complicated and probably contains a fair amount of hyperparameters that would attempt to reflect the intricacies of the various human biomechanical aspects of the spread playstyle. Such hyperparameters aren't the focus of this document, however it's good to keep in mind that they're somewhat at the root of a lot of debates over how different aspects of difficulty interact together mathematically and intuitively.

## Axioms

Over the years, there have been many lengthy discussions and debates over how to approach the automatic computation of a chart's difficulty. Due to the lack of extensive tooling and proper formalization of the problem, most of these debates would end in a dead end; the intricacies are simply too complex to discuss just in a casual conversation without eventually having inconsistent statements.

In order to build a foundation for those debates in a more formal setting, this section introduces some axioms that should _always_ hold regardless of the approach taken to implement a difficulty calculator. These axioms are based on concepts that are considered as universally true and agreed upon by essentially any knowledgeable player.

### Axiom 1: Monotonicity of Jack-like Transitions

For any chart consisting of a sequence of hits all on the same hand, with identical gap $g$ and a fixed set of jack-like transitions, the difficulty must strictly decrease as the gap increases.

That is, shorter gaps are always more difficult for constant jack-like motion patterns.

#### Formally

Let $D_T(g)$ be the difficulty of a chart with transition set $T$ and gap $g$. Then:

$$
T = \{T_i \in \{1, 2, 3, 4\} \mid 1 \le i \le n,\forall i \in [1, n - 2],\ (T_i, T_{i+1}, T_{i+2}) \notin \{(1, 3, 2), (2, 3, 1)\} \}
$$
$$
\forall g_1, g_2\in[1, \infin]\ ,g_1<g_2 \Rightarrow D_T(g_1) > D_T(g_2)
$$

### Axiom 2: Monotonicity of Alternating Singles with Gap > 100ms

For any chart consisting of a sequence of alternating singles, so constant transition type $t=0$, all on the same hand, with a fixed gap $g > 100$ ms, the difficulty must strictly decrease as the gap increases.

That is, as alternating notes approach the manipulation threshold of 100ms, the difficulty increases. As they move further apart, the difficulty decreases.

#### Formally

Let $D_t(g)$ be the difficulty of a chart with alternating singles at gap $g$. Then:

$$
\forall g_1,g_2\in[100, \infin]\ ,g_1<g_2\Rightarrow D_t(g_1)>D_t(g_2)
$$

### Axiom 3: Monotonicity of Repetition

For any chart consisting of a sequence of a single transition type (or a consistent alternating motion such as $T = [2, 3, 2, 3, ...]$) with fixed gap $g$, the difficulty must strictly increase as the number of repeated transitions increases.

That is, longer repetitive motions (e.g., 20-note jacks) are always more difficult than shorter ones (e.g., 10-note jacks), assuming the motion type and gap are the same.

#### Formally

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
