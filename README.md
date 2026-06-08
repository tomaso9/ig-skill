# IG Skill — Institutional Grammar 2.0 Coder

A Claude Code skill that applies **Institutional Grammar 2.0 (IG 2.0)** coding to rule documents — regulations, statutes, policies, bylaws, and other institutional texts.

Based on: *Frantz & Siddiki, IG 2.0 Codebook v1.4 (October 2024)*

---

## What It Does

Given a rule document (or a pre-identified statement list), the skill:

1. **Identifies** all institutional statements and classifies each as regulative (REG), constitutive (CONST), or non-institutional (NON-IS)
2. **Encodes** each statement in IG Script notation at your chosen level of expressiveness
3. **Produces** structured outputs ready for analysis — in-chat review, spreadsheet, or IG Parser input

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
/ig-code statements.xlsx
/ig-code prior_session_statement_list.csv
```

**For `.xlsx` input:** Each row must be a pre-identified institutional statement. The file must include at least two columns — one for the statement text and one for a unique statement ID (e.g., S1, S2…).

**For `.csv` input:** A statement list saved from a previous coding session (`<doc>_statement_list.csv`). The skill loads it directly and skips statement identification.

---

## Workflow Decision Tree

The diagram below shows every decision point in a complete coding session.

```
START: /ig-code <file>
│
├─ Input type?
│   │
│   ├─ .txt / .pdf / .docx
│   │   Step 1:  Load document text
│   │   Step 4:  Familiarize — document type, zones, key actors
│   │   Step 5:  Identify & classify all statements → researcher confirms
│   │            Save confirmed list to <doc>_statement_list.csv
│   │
│   ├─ .xlsx
│   │   Step 1:   Load workbook (headers + all rows)
│   │   Step 1.5: Choose ID column + text column
│   │             Classify each row as REG / CONST / NON-IS
│   │             Researcher confirms → confirmed list
│   │             (Skips Steps 4 and 5)
│   │
│   └─ .csv  (pre-classified list from a prior session)
│       Step 1: Load rows, researcher confirms
│               (Skips Steps 1.5, 4, and 5)
│
│   ── confirmed statement list available ──
│
├─ Step 2: Choose coding level
│   ├─ IG Core      — basic structural analysis
│   ├─ IG Extended  — property hierarchies, nesting, context types
│   └─ IG Logico    — full semantic + ontological annotation
│
├─ Step 3: Choose output format(s), multi-agent mode, and metrics
│
├─ Encoding
│   │
│   ├─ Multi-agent mode = YES
│   │   │
│   │   ├─ Statement count ≤ 50?
│   │   │   ├─ YES ── 1 batch, 3 agents
│   │   │   └─ NO  ── N batches of up to 50 statements each
│   │   │             (if total agent calls > 9: large-doc warning shown)
│   │   │
│   │   ├─ Step 6:   Orchestrator reads reference files, pre-assigns types,
│   │   │            dispatches 3 agents in parallel per batch
│   │   │            Each agent encodes using inline reference → AGENT_DATA
│   │   │
│   │   └─ Step 6.5: Merge three outputs
│   │                Field-by-field comparison → majority vote (2-of-3)
│   │                All three differ → UNDETERMINED (flagged for review)
│   │                Writes: <doc>_IG_coded.csv + <doc>_IG_review.csv
│   │
│   └─ Multi-agent mode = NO
│       └─ Step 6: Single agent encodes all statements sequentially
│
├─ Step 7:  Write CSV / Excel output       (if selected)
├─ Step 8:  Write IG Parser .txt output    (if selected)
├─ Step 9:  Display summary table          (always shown)
├─ Step 10: Report coding notes & ambiguities
│
└─ Metrics enabled AND level ≥ IG Extended?
    ├─ YES → Step 11: Run complexity.py → <doc>_IG_metrics.csv
    └─ NO  → Done
```

---

## Setup Questions

The skill asks up to four questions before coding begins.

### Question 1 — Coding Level

| Level | Description | Best for |
|-------|-------------|----------|
| **IG Core** | Basic structural analysis. Identifies all components at a fundamental level. | First-pass coding, large documents |
| **IG Extended** | Deep structural analysis. Adds property hierarchies, nesting, and fine-grained context categorization. | Complex documents, computational use |
| **IG Logico** | Full semantic annotation. Builds on Extended with institutional function labels and ontological annotations. | Theory-linked analysis |

### Question 2 — Output Format

Select one or more:

- **In-chat markdown** — coding displayed directly in the conversation
- **CSV / Excel file** — one row per statement, one column per IG component
- **IG Parser .txt** — formatted for the [IG Parser](https://github.com/chrfrantz/IG-Parser) tool
- **All of the above**

### Question 3 — Multi-Agent Mode

Choose whether to run with one agent or three. See [Multi-Agent Mode](#multi-agent-mode).

### Question 4 — Complexity Metrics *(IG Extended / IG Logico only)*

Whether to compute institutional complexity metrics (ISC, ISR, Tree Depth) after coding. If yes, you select which metrics.

---

## Multi-Agent Mode

When enabled, three independent Claude agents code the document in parallel. Any disagreement between agents — in component content, presence, or value — is flagged for your review.

### How it works

1. **Pre-dispatch:** The orchestrator assigns statement types (REG/CONST/NON-IS) and reads all required IG 2.0 reference materials. Agents receive the reference content inline in their task prompt — they do not read any files themselves.
2. **Dispatch:** Three agents code the statements in parallel, each producing a structured data block.
3. **Merge:** Disagreements are detected field by field. Consensus values are determined by majority vote (2-of-3). If all three agents produce different values for a field, that field is set to **`UNDETERMINED`** and flagged for human adjudication.
4. **Cross-check:** The consensus statement list is compared against the orchestrator's reference list. Any statement missed by all three agents is flagged explicitly.
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
| `consensus_used` | Value written to consensus CSV (`UNDETERMINED` if all three differ) |

In the IG Parser `.txt` output, flagged statements carry a `[REVIEW REQUIRED]` marker and a `Review:` line listing the disagreeing fields.

### When to use multi-agent mode

Use multi-agent mode when coding quality matters more than speed — inter-rater reliability studies, systematic policy analysis, or any use where you want to know which decisions were unambiguous and which require expert judgment.

Single-agent mode is faster and appropriate for exploratory work or documents where you plan to review the output yourself.

---

## Session State

After each step, the skill writes a `<document>_IG_session.json` file alongside your outputs. This file records all confirmed session settings: input path and type, coding level, output formats, multi-agent mode, metrics selection, statement list path, current step, and batch configuration.

If a session is interrupted or the context window is compressed mid-session, the skill reads this file at the start of each step to recover its state rather than relying on in-context memory.

---

## Output Format Details

### CSV / Excel

Written as `<document_name>_IG_coded.csv` (or `.xlsx`) in the same directory as the input file.

| Column | Description |
|--------|-------------|
| `id` | Statement ID (S1, S2, …) |
| `type` | REG / CONST |
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
