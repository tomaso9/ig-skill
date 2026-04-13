# IG Skill — Institutional Grammar 2.0 Coder

A Claude Code skill that applies **Institutional Grammar 2.0 (IG 2.0)** coding to rule documents — regulations, statutes, policies, bylaws, and other institutional texts.

Based on: *Frantz & Siddiki, IG 2.0 Codebook v1.4 (October 2024)*

---

## What It Does

Given a rule document, the skill:

1. **Identifies** all institutional statements and classifies each as regulative (REG), constitutive (CONST), hybrid (HYB), or non-institutional (NON-IS)
2. **Encodes** each statement in IG Script notation at your chosen level of expressiveness
3. **Produces** structured outputs ready for analysis — in-chat review, spreadsheet, or IG Parser input

You choose the coding level and output format interactively. Optionally, you can enable **multi-agent mode**, where three independent agents code the document in parallel and any disagreements are automatically flagged for your review.

---

## Installation

```
/plugin install ig-skill@github:tomaso9/ig-skill
```

Or copy the `ig-skill/` folder to your project's `.claude/skills/` directory:

```
.claude/skills/ig-skill/SKILL.md
```

---

## Usage

```
/ig-code <path-to-document>
/ig-code regulations.txt
/ig-code policy.pdf
/ig-code statute.docx
```

The skill asks three questions before coding begins:

### Question 1 — Coding Level

| Level | Description | Best for |
|-------|-------------|----------|
| **IG Core** | Basic structural analysis. Human-readable. Moderate syntactic detail. | First-pass coding, large documents |
| **IG Extended** | Fine-grained decomposition: property hierarchies, component nesting, rich context categorization. | Complex documents, computational use |
| **IG Logico** | Full semantic annotation: institutional function labels, animacy, role, metatype. | Theory-linked analysis |

### Question 2 — Output Format

Select one or more:

- **In-chat markdown** — coding displayed directly in the conversation
- **CSV / Excel file** — one row per statement, one column per IG component
- **IG Parser .txt** — formatted for the [IG Parser](https://github.com/chrfrantz/IG-Parser) tool
- **All of the above**

### Question 3 — Multi-Agent Mode

Choose whether to run in single-agent or multi-agent mode (see below).

---

## Multi-Agent Mode

When enabled, three independent Claude agents code the document separately. Any disagreement between agents — in statement type, component presence, or component content — is flagged for your review.

### How it works

1. **Pre-dispatch:** The orchestrating agent runs its own statement identification (Steps 4–5) and presents the statement list to you for confirmation before dispatching.
2. **Dispatch:** Three agents code the document independently in parallel, each producing a CSV.
3. **Merge:** Disagreements are detected field by field. Consensus values are determined by majority vote (2-of-3); if all three differ, the first agent's value is used as a starting point.
4. **Cross-check:** The consensus statement list is compared against the orchestrator's reference. Any statement missed by all three agents is flagged explicitly.
5. **Output:** Your chosen format(s) are produced from the consensus values. Flagged statements are marked `⚠` throughout.

### Multi-agent outputs

In addition to your chosen output format(s), multi-agent mode always writes:

**`<document>_IG_coded.csv`** — consensus coding with two extra columns:

| Column | Values | Meaning |
|--------|--------|---------|
| `review_flag` | TRUE / FALSE | Whether any field disagreed across agents |
| `disagreement_fields` | e.g. `Cac, Cex` | Which fields need human review |

**`<document>_IG_review.csv`** — one row per disagreement, for adjudication:

| Column | Description |
|--------|-------------|
| `id` | Statement ID |
| `field` | Which IG component disagreed |
| `run1_value` | Agent 1's value |
| `run2_value` | Agent 2's value |
| `run3_value` | Agent 3's value |
| `consensus_used` | Value written to the consensus CSV |

In the IG Parser `.txt` output, flagged statements carry a `[REVIEW REQUIRED]` marker and a `Review:` line listing the disagreeing fields.

### When to use multi-agent mode

Multi-agent mode is recommended when coding quality matters more than speed — inter-rater reliability studies, systematic policy analysis, or any use where you want to know which coding decisions were unambiguous and which require expert judgment.

Single-agent mode is faster and appropriate for exploratory work or documents where you plan to review the output yourself.

---

## Output Format Details

### CSV / Excel

Written as `<document_name>_IG_coded.csv` (or `.xlsx`) in the same directory as the input file.

| Column | Description |
|--------|-------------|
| `id` | Statement ID (S1, S2, …) |
| `type` | REG / CONST / HYB |
| `coding_level` | IG Core / Extended / Logico |
| `original_text` | Source sentence |
| `A` | Attributes |
| `A_prop` | Attribute properties |
| `D` | Deontic |
| `I` | Aim |
| `Bdir` | Direct Object |
| `Bdir_prop` | Direct Object properties |
| `Bind` | Indirect Object |
| `Bind_prop` | Indirect Object properties |
| `Cac` | Activation Condition |
| `Cex` | Execution Constraint |
| `O` | Or else |
| `E` | Constituted Entity |
| `E_prop` | Entity properties |
| `M` | Modal |
| `F` | Constitutive Function |
| `P` | Constituting Properties |
| `P_prop` | Constituting Properties properties |
| `ig_script_full` | Full IG Script encoded statement |
| `notes` | Coder notes and ambiguity flags |

### IG Parser .txt

Written as `<document_name>_IG_parser.txt`. One block per statement:

```
ID: S1
Type: REGULATIVE
Level: IG Core
Original: "Certified farmers must submit an organic system plan annually."
Statement: A,p(Certified) A(farmers) D(must) I(submit) Bdir(organic system plan) Cex(annually).
```

### In-chat Markdown

Displays each statement inline:

```
[S1] REGULATIVE | IG Core
Original: "..."
Coded:    A,p(...) A(...) D(...) I(...) Bdir(...) Cex(...).
Notes:    ...
```

Flagged statements in multi-agent mode:

```
[⚠ S1] REVIEW REQUIRED | REGULATIVE | IG Core
Original: "..."
Coded (consensus): A,p(...) A(...) D(...) I(...) Bdir(...) Cex(...).
Flagged fields: Cac, Cex — see review CSV for agent values.
Notes:    ...
```

---

## IG Script Quick Reference

**Regulative:** `A` (Attributes) · `D` (Deontic) · `I` (Aim) · `Bdir` (Direct Obj) · `Bind` (Indirect Obj) · `Cac` (Activation Condition) · `Cex` (Execution Constraint) · `O` (Or else)

**Constitutive:** `E` (Constituted Entity) · `M` (Modal) · `F` (Constitutive Function) · `P` (Constituting Properties) · `Cac` · `Cex` · `O`

**Properties:** `,p` suffix · **Implied components:** `[ ]` · **Logical operators:** `[AND]` `[OR]` `[XOR]` `[NOT]` · **Nesting:** `{ }`

---

## Reference

- Frantz, C.K. & Siddiki, S.N. (2021, 2022). *Institutional Grammar 2.0.*
- Codebook: https://arxiv.org/abs/2008.08937
- IG Parser: https://github.com/chrfrantz/IG-Parser
- This skill: https://github.com/tomaso9/ig-skill

---

## License

MIT
