# IG Skill — Institutional Grammar 2.0 Coder

A Claude Code skill that applies **Institutional Grammar 2.0 (IG 2.0)** coding to rule documents.

Based on: *Frantz & Siddiki, IG 2.0 Codebook v1.4 (October 2024)*

---

## What It Does

This skill teaches Claude to:
1. Parse rule documents (`.txt`, `.docx`, `.pdf`)
2. Identify and classify institutional statements as **regulative**, **constitutive**, **hybrid**, or **non-IS**
3. Encode each statement using **IG Script notation** at your chosen level of expressiveness (IG Core, IG Extended, or IG Logico)
4. Apply pre-coding steps, nesting principles, and type heuristics from the official IG 2.0 codebook
5. Produce a structured output table and coding notes

---

## Installation

### From GitHub (once published)
```
/plugin install ig-skill@github:tomaso9/ig-skill
```

### Local installation
Copy the `ig-skill/` folder to your project's `.claude/skills/` directory:
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

The skill will interactively ask two questions before coding begins:
1. **Coding level** — IG Core, IG Extended, or IG Logico
2. **Output format(s)** — in-chat markdown, CSV/Excel file, IG Parser .txt, or all

---

## Output Formats

### In-chat Markdown
Displays coding inline in the conversation — original text, IG Script, notes per statement, plus summary tables and ambiguity notes. Best for review and iteration.

### CSV / Excel File
Written to disk as `<document_name>_IG_coded.csv` (or `.xlsx`) in the same directory as the input file. One row per encoded statement, one column per IG component:

| Column | Description |
|--------|-------------|
| `id` | Statement ID (S1, S2, ...) |
| `type` | REG / CONST / HYB |
| `coding_level` | Core / Extended / Logico |
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

### IG Parser .txt File
Written to disk as `<document_name>_IG_parser.txt`. One block per statement, formatted for direct input into the [IG Parser](https://github.com/chrfrantz/IG-Parser):

```
ID: S1
Type: REGULATIVE
Level: IG Core
Original: "Certified farmers must submit an organic system plan annually."
Statement: A,p(Certified) A(farmers) D(must) I(submit) Bdir(organic system plan) Cex(annually).
```

---

## IG 2.0 Levels of Expressiveness

| Level | Description |
|-------|-------------|
| **IG Core** | Basic structural analysis. Human readable. Moderate syntactic detail. |
| **IG Extended** | Fine-grained decomposition: property hierarchies, component-level nesting, rich context categorization. |
| **IG Logico** | Full semantic annotation using institutional taxonomies (animacy, role, regulative/constitutive functions). |

---

## IG Script Quick Reference

**Regulative:** `A` (Attributes) · `D` (Deontic) · `I` (Aim) · `Bdir` (Direct Obj) · `Bind` (Indirect Obj) · `Cac` (Activation Condition) · `Cex` (Execution Constraint) · `O` (Or else)

**Constitutive:** `E` (Constituted Entity) · `M` (Modal) · `F` (Constitutive Function) · `P` (Constituting Properties) · `Cac` · `Cex` · `O`

**Properties:** `,p` suffix · **Implied:** `[ ]` · **Logical operators:** `[AND]` `[OR]` `[XOR]` `[NOT]`

---

## Reference

- Frantz, C.K. & Siddiki, S.N. (2021, 2022). *Institutional Grammar 2.0.*
- GitHub: https://github.com/tomaso9/ig-skill
- Codebook: https://arxiv.org/abs/2008.08937
- IG-Parser: https://github.com/chrfrantz/IG-Parser

---

## License

MIT
