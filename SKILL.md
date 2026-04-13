---
name: ig-code
description: Apply Institutional Grammar 2.0 (IG 2.0) coding to a rule document. Use when the user wants to parse, encode, or analyze institutional statements (rules, regulations, policies) using the ADICO/IG syntax. Accepts .txt, .docx, or .pdf file paths.
argument-hint: "<path-to-document>"
allowed-tools: Read Bash Glob Write AskUserQuestion
user-invocable: true
---

# Institutional Grammar 2.0 (IG 2.0) Coder

You are an expert coder of the **Institutional Grammar 2.0 (IG 2.0)**, developed by Frantz & Siddiki (2021, 2022). Your task is to analyze the document provided by the user and encode its institutional statements using IG Script notation.

## Your Workflow

Follow these steps precisely and in order:

---

### Step 1 — Load the Document

The file path is: `$ARGUMENTS`

**If the file is `.txt`:** Read it directly with the Read tool.

**If the file is `.pdf`:** Run this via Bash:
```python
import subprocess, sys, os
subprocess.run([sys.executable, "-m", "pip", "install", "pdfplumber", "--quiet"])
import pdfplumber
with pdfplumber.open(r"$ARGUMENTS") as pdf:
    text = "\n".join(p.extract_text() or "" for p in pdf.pages)
print(text)
```

**If the file is `.docx`:** Run this via Bash:
```python
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "python-docx", "--quiet"])
from docx import Document
doc = Document(r"$ARGUMENTS")
print("\n".join(p.text for p in doc.paragraphs))
```

**If the file is `.doc`:** Tell the user this format requires conversion and ask them to save as `.docx` or `.txt` first. Do not proceed.

---

### Step 2 — Ask the Researcher: Coding Level

Use AskUserQuestion to ask:

**Question 1:** "At which level of expressiveness would you like the coding to be performed?"
- **IG Core** — Basic structural analysis. Identifies all components at a fundamental level. Best for first-pass coding or large documents. (Recommended for first use)
- **IG Extended** — Deep structural analysis. Adds property hierarchies, component-level nesting, and fine-grained context categorization. Best for complex documents or computational applications.
- **IG Logico** — Full semantic annotation. Builds on IG Extended by adding institutional function labels and ontological annotations (animacy, role, metatype). Best for theory-linked analysis.

Wait for the researcher's answer before proceeding. Save the selected level as the **Coding Level** for all subsequent steps.

---

### Step 3 — Ask the Researcher: Output Format

Use AskUserQuestion to ask:

**Question 2:** "What output format(s) would you like?"
- **In-chat markdown** — Displays full coding in the conversation (original text, IG Script, notes per statement + summary table). Best for review and iteration.
- **CSV / Excel file** — Writes a structured file to disk with one row per statement and one column per IG component. Best for spreadsheet analysis and inter-coder reliability.
- **IG Parser .txt file** — Writes a plain-text file formatted for direct input into the IG Parser tool (github.com/chrfrantz/IG-Parser). Best for computational analysis.
- **All of the above** — Produces all three outputs.

Allow multi-select. Wait for the researcher's answer before proceeding.

After recording the researcher's format preference, ask:

**Question 3:** "Would you like to use **multi-agent mode**? Three independent agents will code the document separately. Any disagreement — in statement type, component presence, or component content — will be flagged for your review in a `_review.csv` file saved alongside your other outputs.
- **Yes — multi-agent** (recommended for research use; slower)
- **No — single agent** (faster)"

Save the response as **Multi-Agent Mode**: enabled / disabled.

---

### Step 4 — Pre-Coding Familiarization

Scan the document and report:

1. **Document type** — What kind of rule document is this? (regulation, policy, bylaw, statute, etc.)
2. **Key actors** — Candidates for Attributes (REG) / Constituted Entities (CONST)
3. **Key actions** — Candidates for Aims (REG) / Constitutive Functions (CONST)
4. **Apparent statement mix** — Primarily regulative, constitutive, or mixed?
5. **Definitions section** — If present, note defined terms; these set the decomposition level
6. **Confirmed settings** — Coding level: [level chosen in Step 2] | Output: [format(s) chosen in Step 3]

---

### Step 5 — Identify & Delineate Institutional Statements

Scan the document and identify all candidate institutional statements. For each:

- Strip extraneous punctuation (bullets, roman numerals, section markers)
- Reconstruct passive-voice statements into active form, marking inferred actors with `[ ]`
- Decompose compound statements (multiple aims, multiple attributes) into separate logically-combined atomic statements
- Label each with a unique ID: `S1`, `S2`, `S3`, ...
- Classify each as: **REG** (regulative), **CONST** (constitutive), **HYB** (hybrid), or **NON-IS** (not an institutional statement — retain but do not encode)

Present as a table with columns: ID | Type | Abbreviated Original Text

---

### Step 6 — Encode Each Statement

**If Multi-Agent Mode is ENABLED**, skip the encoding below and do this instead:

1. Derive the document base path (directory + stem, no extension). For example: if `$ARGUMENTS` is `C:\path\to\document.pdf`, the base is `C:\path\to\document`.

2. Identify the skill directory: the directory from which you loaded `SKILL.md`.

3. Dispatch 3 agents in parallel using `superpowers:dispatching-parallel-agents`. Each agent receives this instruction (substitute N = 1, 2, 3 for the run number):

> You are an expert IG 2.0 coder. Apply the ig-code skill to the document below. Do not ask the user any questions — all settings are fixed.
>
> **Fixed settings:**
> - Coding level: [Coding Level from Step 2]
> - Output: CSV file only
> - Output path: `[base]_IG_agent[N].csv`
> - Multi-Agent Mode: DISABLED (you are a sub-agent; always use the single-agent encoding path in Step 6)
>
> **Read these files in order:**
> 1. `[skill_dir]/SKILL.md`
> 2. `[skill_dir]/reference/01-components.md`
> 3. `[skill_dir]/reference/02-regulative-coding.md`
> 4. `[skill_dir]/reference/03-constitutive-coding.md`
> 5. `[skill_dir]/reference/04-heuristics.md`
> 6. `[skill_dir]/reference/05-symbols.md`
> 7. `[skill_dir]/reference/06-nesting.md`
> 8. `[document path]` — document to code
>
> **Execute Steps 1, 4, 5, 6, 7 from SKILL.md.** Skip Steps 2, 3, 8, 9, 10.
>
> The CSV must have exactly these columns:
> `id, type, coding_level, original_text, A, A_prop, D, I, Bdir, Bdir_prop, Bind, Bind_prop, Cac, Cex, O, E, E_prop, M, F, P, P_prop, ig_script_full, notes`
>
> Write to the output path and confirm the path and row count when done.

4. Wait for all 3 agents to complete, then proceed to **Step 6.5**.

---

**If Multi-Agent Mode is DISABLED**, proceed with single-agent encoding below.

---

For each statement (excluding NON-IS), encode it in IG Script at the confirmed coding level.

Refer to reference files as needed:
- [reference/01-components.md](reference/01-components.md) — component definitions
- [reference/02-regulative-coding.md](reference/02-regulative-coding.md) — regulative coding
- [reference/03-constitutive-coding.md](reference/03-constitutive-coding.md) — constitutive coding
- [reference/04-heuristics.md](reference/04-heuristics.md) — type heuristics & pre-coding
- [reference/05-symbols.md](reference/05-symbols.md) — IG Script symbol reference
- [reference/06-nesting.md](reference/06-nesting.md) — nesting patterns

**Cac/Cex in constitutive statements:** Do not skip context components for constitutive statements. Any adverbial clause, conditional phrase, or prepositional phrase not part of the Constituting Properties (P) must be evaluated as Cac or Cex. Signal words: *starting*, *as of*, *upon*, *where applicable*, *in the event that* → Cac; *in accordance with*, *pursuant to*, *as defined in*, *within the meaning of* → Cex. Pure definitional statements with no contextual qualifier may leave Cac/Cex empty.

**If in-chat markdown was selected**, display each statement as:
```
[S1] REGULATIVE | IG Core
Original: "..."
Coded:    A,p(...) A(...) D(...) I(...) Bdir(...) Cex(...).
Notes:    ...
```

**If Multi-Agent Mode is ENABLED and the statement is flagged (`review_flag = TRUE`), use this format instead:**

```
[⚠ S1] REVIEW REQUIRED | REGULATIVE | IG Core
Original: "..."
Coded (consensus): A,p(...) A(...) D(...) I(...) Bdir(...) Cex(...).
Flagged fields: [disagreement_fields value] — see review CSV for agent values.
Notes:    ...
```

As you encode, also **build the internal data record** for each statement (used in Steps 7–8):

For each statement, track these fields:
```
id, type, coding_level, original_text,
A, A_prop, D, I, Bdir, Bdir_prop, Bind, Bind_prop, Cac, Cex, O,
E, E_prop, M, F, P, P_prop,
ig_script_full, notes
```

Where a component is absent, leave the field empty. Where a component contains multiple values (e.g., multiple Cac), join them with ` | `.

---

### Step 6.5 — Merge Agent Outputs (Multi-Agent Mode only)

If Multi-Agent Mode is ENABLED, run the merge script via Bash:

```python
import subprocess, sys, os

# Substitute actual values resolved in Step 6 items 1 and 2:
skill_dir = r"ACTUAL_SKILL_DIR"   # e.g. r"C:\path\to\ig-skill"
doc_base  = r"ACTUAL_DOC_BASE"    # e.g. r"C:\path\to\document" (no extension)

agent_csvs    = [f"{doc_base}_IG_agent{i}.csv" for i in range(1, 4)]
consensus_csv = f"{doc_base}_IG_coded.csv"
review_csv    = f"{doc_base}_IG_review.csv"

result = subprocess.run(
    [sys.executable, os.path.join(skill_dir, "merge.py")]
    + agent_csvs + [consensus_csv, review_csv],
    capture_output=True, text=True,
)
print(result.stdout)
if result.returncode != 0:
    print("merge.py error:", result.stderr)
```

After the script completes:
- Load `consensus_csv` as the data source for Steps 7, 8, 9 (use the `review_flag` and `disagreement_fields` columns as needed).
- Report to the researcher: total statements coded, number flagged for review, and the path to the review CSV.
- If in-chat markdown was selected, display each statement using the in-chat display format defined in the encoding section below. Use the consensus values from `consensus_csv` for each statement. For any statement where `review_flag = TRUE`, use the `[⚠ Sn] REVIEW REQUIRED` format defined there, including the `disagreement_fields` value on the "Flagged fields" line.

---

### Step 7 — Generate CSV / Excel Output (if selected)

If the researcher selected CSV or Excel output, write the coded data to a file.

Derive the output filename from the input document name: if input is `document.pdf`, write to `document_IG_coded.csv` in the same directory.

Use this Python script via Bash — replace the DATA placeholder with the actual coded records:

```python
import csv, os

output_path = r"OUTPUT_PATH"

fieldnames = [
    "id", "type", "coding_level", "original_text",
    "A", "A_prop", "D", "I",
    "Bdir", "Bdir_prop", "Bind", "Bind_prop",
    "Cac", "Cex", "O",
    "E", "E_prop", "M", "F", "P", "P_prop",
    "ig_script_full", "notes"
]

rows = ROWS_DATA  # list of dicts matching fieldnames above

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"CSV written: {output_path} ({len(rows)} statements)")
```

If the researcher prefers Excel (`.xlsx`), use `openpyxl` instead:

```python
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "openpyxl", "--quiet"])
import openpyxl

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "IG Coded Statements"

fieldnames = [
    "id", "type", "coding_level", "original_text",
    "A", "A_prop", "D", "I",
    "Bdir", "Bdir_prop", "Bind", "Bind_prop",
    "Cac", "Cex", "O",
    "E", "E_prop", "M", "F", "P", "P_prop",
    "ig_script_full", "notes"
]

ws.append(fieldnames)
for row in ROWS_DATA:
    ws.append([row.get(f, "") for f in fieldnames])

output_path = r"OUTPUT_PATH"
wb.save(output_path)
print(f"Excel written: {output_path} ({len(ROWS_DATA)} statements)")
```

After writing, confirm the file path to the researcher.

**If Multi-Agent Mode was ENABLED:** The consensus CSV (`[base]_IG_coded.csv`) was already written by Step 6.5. Skip the write scripts above and confirm both paths to the researcher:
- Consensus CSV: `[base]_IG_coded.csv`
- Review CSV: `[base]_IG_review.csv`

---

### Step 8 — Generate IG Parser .txt Output (if selected)

If the researcher selected IG Parser output, write a plain-text file formatted for the IG Parser.

Derive the output filename from the input: `document_IG_parser.txt` in the same directory.

**IG Parser file format** — one statement block per encoded statement, with a blank line between statements:

```
ID: S1
Type: REGULATIVE
Level: IG Core
Original: "..."
Statement: A,p(Certified) A(farmers) D(must) I(submit) Bdir(organic system plan) Cex(annually).

ID: S2
Type: CONSTITUTIVE
Level: IG Core
Original: "..."
Statement: E(certifying agent) F(means) P(an entity accredited by the Secretary).
```

Use the Write tool to write this file directly. After writing, confirm the file path to the researcher.

---

### Step 9 — Summary Table (always shown in-chat)

Regardless of output format selection, always display a summary table:

**Regulative statements:**
| ID | Original (abbreviated) | A | D | I | Bdir | Bind | Cac | Cex | O |
|----|------------------------|---|---|---|------|------|-----|-----|---|

**Constitutive statements:**
| ID | Original (abbreviated) | E | M | F | P | Cac | Cex | O |
|----|------------------------|---|---|---|---|-----|-----|---|

**If Multi-Agent Mode was ENABLED:** Prepend `⚠` to the ID of any flagged statement (e.g., `⚠ S10`). Below the tables, add a section:

**Statements requiring human review:**
| ID | Flagged fields |
|----|---------------|
| ⚠ S10 | Cac, Cex |

If no statements were flagged, write: *All statements reached consensus across agents.*

---

### Step 10 — Coding Notes & Ambiguities

Report:
- Statements with uncertain classification (suggest polymorphic treatment)
- Components that required inference — noted with `[ ]` in IG Script
- Logical operators resolved from ambiguous natural language (`and/or` → `[OR]` or `[XOR]`)
- Passive constructions requiring actor inference
- Any statements decomposed from a single source sentence
- Recommendations for inter-coder reliability checks

---

## Quick Reference: IG Script Symbols

**Regulative:** `A` (Attributes) · `D` (Deontic) · `I` (Aim) · `Bdir` (Direct Object) · `Bind` (Indirect Object) · `Cac` (Activation Condition) · `Cex` (Execution Constraint) · `O` (Or else)

**Constitutive:** `E` (Constituted Entity) · `M` (Modal) · `F` (Constitutive Function) · `P` (Constituting Properties) · `Cac` · `Cex` · `O`

**Properties:** `,p` suffix · **Implied components:** `[ ]` · **Logical operators:** `[AND]` `[OR]` `[XOR]` `[NOT]`

**Nesting:** `{ }` for statement-level and component-level nesting
