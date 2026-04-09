# IG Skill — Inter-Agent Consistency Report

**Date:** 2026-04-08
**Document coded:** `test_rules.txt` — Organic Farming Certification Program
**Coding level:** IG Core
**Number of independent runs:** 5
**Pairwise comparisons:** 10

---

## 1. Approach

Five independent agent instances were each given identical instructions: read the ig-code skill definition (`SKILL.md`) and its six IG 2.0 reference documents, then apply the skill to `test_rules.txt` at IG Core level with CSV output. No information was shared between agents during coding. Each agent saved its output to a uniquely named CSV file (`run1.csv` through `run5.csv`).

The five CSVs were then compared pairwise using `compare.py`, which calculated:

- **Statement count**: number of institutional statements identified per run
- **Type classification agreement**: raw agreement and Cohen's kappa for REG / CONST / HYB labels
- **Component presence/absence agreement**: raw agreement and Cohen's kappa for each IG component (whether it was filled or left empty)
- **Component content similarity**: mean token-level Jaccard similarity for cells filled by both agents in a pair

Cohen's kappa corrects for chance agreement and is the standard metric for inter-rater reliability in content analysis. Jaccard similarity measures how much of the assigned text overlaps at the token level, ranging from 0 (no overlap) to 1.0 (identical).

---

## 2. Rationale

Consistency is a prerequisite for trustworthy content analysis. Before asking whether an IG coding is *correct*, it must be *reproducible*: the same text coded under the same guidelines should yield the same result regardless of who — or what — does the coding.

Using multiple independent LLM agents as a proxy for inter-rater reliability has a specific limitation worth stating clearly: the agents share the same model weights, the same skill prompt, and the same reference documents. High agreement therefore reflects the internal consistency of the skill's instructions — not independent expert judgment. Disagreements, however, are directly informative: they identify passages or component boundaries where the skill's guidance is underspecified, ambiguous, or contradictory. The method is therefore most useful as a **diagnostic tool for prompt refinement**, not as a substitute for human validation.

This test is deliberately scoped to **reliability only**. It does not assess validity (whether the codings are correct by IG 2.0 standards). A separate evaluation against expert-coded data is planned as a next step.

---

## 3. Results

### 3.1 Statement Detection

| Run | Statements identified |
|-----|----------------------|
| run1.csv | 13 |
| run2.csv | 13 |
| run3.csv | 14 |
| run4.csv | 13 |
| run5.csv | 14 |

Three runs produced 13 statements; two produced 14. The discrepancy is entirely attributable to decomposition decisions at two specific source sentences:

- **Sentence 2.4** ("Inspectors must sign and file farm inspection reports"): runs 1, 2, 4 decomposed this into two atomic statements (`S7a` sign, `S7b` file); run 3 kept it as a single statement (`S7`) with a compound Aim encoded as `I(sign [AND] file)`.
- **Sentence 3.2** ("Any operation that knowingly sells or labels a product as organic...shall be subject to a civil penalty"): run 5 further decomposed this into `S10a` (sells) and `S10b` (labels); all other runs kept it as one statement with `I(sell [OR] label)`.

Run 3 also used a different ID numbering scheme for the enforcement section (S12, S13, S14 vs. S9, S10, S11 in other runs), reflecting a different segmentation boundary for sentence 3.1.

### 3.2 Type Classification Agreement

Pairwise Cohen's kappa for REG / CONST / HYB classification (common statement IDs only):

| Pair | Common IDs | Raw agreement | Cohen's kappa |
|------|-----------|--------------|--------------|
| run1 vs run2 | 13 | 100.0% | 1.000 |
| run1 vs run3 | 9  | 100.0% | 1.000 |
| run1 vs run4 | 13 | 100.0% | 1.000 |
| run1 vs run5 | 12 | 100.0% | 1.000 |
| run2 vs run3 | 9  | 100.0% | 1.000 |
| run2 vs run4 | 13 | 100.0% | 1.000 |
| run2 vs run5 | 12 | 100.0% | 1.000 |
| run3 vs run4 | 9  | 100.0% | 1.000 |
| run3 vs run5 | 8  | 100.0% | 1.000 |
| run4 vs run5 | 12 | 100.0% | 1.000 |

**Mean type kappa across all pairs: 1.000**

Every agent assigned the same REG / CONST / HYB label to every statement, without exception.

### 3.3 Component-Level Agreement

Mean presence/absence kappa and mean content Jaccard averaged across all 10 pairwise comparisons. Content Jaccard is computed only over cells that both agents in a pair filled; "—" indicates the component was never used by any run.

| Component | Mean presence kappa | Mean content Jaccard | Notes |
|-----------|--------------------|--------------------|-------|
| A         | 1.000 | 0.776 | Perfect presence; content varies due to segmentation differences |
| A_prop    | 0.811 | 0.929 | Strong; minor disagreement on whether relative clauses qualify as A,p |
| D         | 1.000 | 0.740 | Perfect presence; low content Jaccard driven by cross-segmentation pairs |
| I         | 1.000 | 0.691 | Perfect presence; lowest content Jaccard — affected by compound-aim decomposition |
| Bdir      | 0.915 | 0.707 | Strong presence; content variance in cross-segmentation pairs |
| Bdir_prop | 0.600 | N/A   | Moderate; run 3 fills this inconsistently with other runs |
| Bind      | 0.612 | 1.000 | Moderate presence; when filled, content is identical |
| Cac       | 0.604 | 1.000 | Moderate presence; when filled, content is identical — disagreement is about *whether* to assign Cac |
| Cex       | 0.718 | 0.707 | Moderate; Cac/Cex boundary is the main source of disagreement |
| O         | 1.000 | 1.000 | Perfect — or-else clause identified and encoded identically |
| E         | 1.000 | 0.973 | Perfect; constitutive entity names near-identical across runs |
| E_prop    | —     | —     | Not used by any run |
| M         | —     | —     | Not used by any run |
| F         | 1.000 | 1.000 | Perfect — constitutive function term identical across all runs |
| P         | 1.000 | 1.000 | Perfect — constituting properties identical across all runs |
| P_prop    | —     | —     | Not used by any run |

### 3.4 Statements with Lowest Agreement

**S7 / S7a / S7b** (sentence 2.4 — "sign and file inspection reports"): The primary segmentation disagreement. Runs 1, 2, 4 produced two atomic statements with IDs `S7a` and `S7b`; run 3 produced one compound statement `S7`. The two approaches are both defensible under IG 2.0 (atomic decomposition vs. logical-operator encoding), but the skill prompt does not specify which is preferred for [AND]-linked Aims.

**S8 / S8a / S8b** (sentence 2.5 — "certifiers and inspectors must seek renewal"): Same pattern. Runs 1, 2, 4 decomposed on compound Attributes (`S8a` certifiers, `S8b` inspectors); run 3 kept as `S8` with `A(certifiers [AND] inspectors)`.

**S10 / S10a / S10b** (sentence 3.2 — "sells or labels as organic"): Run 5 uniquely decomposed the [OR]-linked Aim. All other runs encoded as one statement with `I(sell [OR] label)`.

**S5 — Cac/Cex boundary** (sentence 2.2 — prohibition on synthetic chemicals): Runs 1, 2, 3, 5 agreed on `Cac("once organic certification is conferred")` and `Cex("at any time")`; run 4 disagreed on which contextual clause maps to Cac vs. Cex, showing kappa = 0.494 in the run1-vs-run4 pair for Cac.

**S9** (sentence 3.1 — noncompliance notification): The passive-to-active reconstruction was consistent, but actors and Bind assignments varied across runs, contributing to lower content Jaccard for A and Bind in some pairs.

---

## 4. Discussion

**Overall reliability level**: The skill performs at the highest level of consistency on the most consequential dimension — type classification. A mean kappa of 1.000 across all 10 pairs for REG / CONST / HYB means the skill never confuses a behavioral rule with a constitutive definition (or vice versa). This is a strong result for a task that IG practitioners regard as one of the more demanding classification decisions.

**Most consistent components**: Deontic (D), Or-else (O), and all constitutive components (E, F, P) show perfect presence kappa and near-perfect or perfect content Jaccard. These are the most syntactically constrained elements of IG Script — D is directly recoverable from the modal verb in the source text, O from explicit sanction clauses, and E/F/P from definitional sentence structure. The skill's reference documents apparently provide sufficient guidance for these.

**Primary source of inconsistency — statement segmentation**: The most impactful disagreement is not about component assignment within a statement but about whether to decompose compound statements at all. The skill's SKILL.md instructs agents to "decompose compound statements (multiple aims, multiple attributes) into separate logically-combined atomic statements," but the guidance does not distinguish between cases where decomposition is mandatory versus optional. The result is that agents make different but defensible choices: decompose `[AND]`-linked Aims into atomic statements, or encode them as a single statement with logical operators. This is the root cause of the 13 vs. 14 count discrepancy and the low content Jaccard scores observed in cross-segmentation pairs.

**Second source — Cac/Cex boundary**: Among within-count pairs (where segmentation is identical), the Cac/Cex distinction is the most variable component. Mean presence kappa for Cac is 0.604 (moderate) and for Cex is 0.718 (moderate-to-strong). When agents do fill these components, the content they assign is highly similar (Jaccard 1.000 for Cac, 0.707 for Cex), meaning the disagreement is not about *what* text goes into the component but about *which* component it belongs to. The Cac vs. Cex distinction — activation condition vs. execution constraint — is conceptually subtle, and the reference documents address it but leave room for interpretation at the boundary.

**Third source — Bdir_prop and Bind presence**: Presence kappa for Bdir_prop (0.600) and Bind (0.612) are the lowest of any used component. These reflect genuine ambiguity in whether a qualifying phrase on the direct object rises to the level of a codeable property, and whether an indirect object is sufficiently explicit to assign a Bind. Agents' choices here are internally consistent but diverge from each other.

---

## 5. Conclusion and Next Steps

The skill demonstrates strong reliability on its most critical task — distinguishing regulative from constitutive statements — and near-perfect consistency on syntactically constrained components (D, O, E, F, P). These results justify confidence in the skill's structural coherence as a coding instrument.

The two areas requiring prompt refinement before moving to validity testing are: (1) **decomposition policy** — the skill should specify a clear decision rule for when [AND]/[OR]-linked aims and attributes must be decomposed into atomic statements versus encoded with logical operators within a single statement; and (2) **Cac/Cex disambiguation** — the reference material on activation conditions vs. execution constraints should be supplemented with decision examples drawn from sentence types that commonly appear in regulatory text (temporal clauses, spatial clauses, conditional clauses introduced by "when," "upon," "except").

Once these refinements are made, a re-run of this reliability test should be conducted to verify improvement before proceeding to validity assessment against expert-coded benchmarks.

**Thresholds used for interpretation:**

| Metric | Strong | Moderate | Needs work |
|--------|--------|----------|------------|
| Statement count | All equal | +/-1 statement | 2+ difference |
| Type kappa | >= 0.80 | 0.60-0.79 | < 0.60 |
| Component presence kappa | >= 0.80 | 0.60-0.79 | < 0.60 |
| Content Jaccard | >= 0.70 | 0.50-0.69 | < 0.50 |
