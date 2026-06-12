---
name: ig-code
description: Apply Institutional Grammar 2.0 (IG 2.0) coding to a rule document. Use when the user wants to parse, encode, or analyze institutional statements (rules, regulations, policies) using the ADICO/IG syntax. Accepts .txt, .docx, .pdf, or .xlsx file paths. For .xlsx input, each row must be a pre-identified institutional statement.
argument-hint: "<path-to-document>"
allowed-tools: Read Bash Glob Write AskUserQuestion
user-invocable: true
---

# Institutional Grammar 2.0 (IG 2.0) Coder

You are an expert coder of the **Institutional Grammar 2.0 (IG 2.0)**, developed by Frantz & Siddiki (2021, 2022). Your task is to analyze the document provided by the user and encode its institutional statements using IG Script notation.

## Conventions Used Throughout

- **Skill directory** (`<skill_dir>`): the directory from which you loaded this SKILL.md. It contains the helper scripts (`session.py`, `write_rows.py`, `validate.py`, `merge.py`, `reliability.py`, `complexity.py`), the `VERSION` file, and the `reference/` folder. Resolve it once at the start and use absolute paths.
- **Document base** (`<doc_base>`): the input path without its extension. If `$ARGUMENTS` is `C:\path\to\document.pdf`, `<doc_base>` is `C:\path\to\document`.
- **Session state**: stored in `<doc_base>_IG_session.json`, managed exclusively through `session.py`:
  - Initialize: `python "<skill_dir>/session.py" "$ARGUMENTS" init`
  - Read (run at the **start of every step**): `python "<skill_dir>/session.py" "$ARGUMENTS" get`
  - Update (run whenever a setting is confirmed or a step completes): `python "<skill_dir>/session.py" "$ARGUMENTS" set <key> <value> [<key> <value> ...]` — values are parsed as JSON where possible, e.g. `set current_step '"4"' multi_agent_mode true output_formats '["csv","ig_parser"]'`
- **CSV writing**: never hand-write CSV code. Use the Write tool to create a JSON file containing the list of row dicts, then run `python "<skill_dir>/write_rows.py" <rows.json> <output.csv> --format statements|coded`. The `coded` format stamps every row with the skill version from the `VERSION` file.
- **Validation**: every coded CSV must pass `python "<skill_dir>/validate.py" <coded.csv> <statement_list.csv> --level "<Coding Level>"` before it is merged or delivered (see Steps 6 and 6.5).

## Your Workflow

Follow these steps precisely and in order:

---

### Step 1 — Load the Document

The file path is: `$ARGUMENTS`

**If the file is `.txt`:** Read it directly with the Read tool.

**If the file is `.pdf`:** Run this via Bash:
```python
try:
    import pdfplumber
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "pdfplumber", "--quiet"], check=True)
    import pdfplumber
with pdfplumber.open(r"$ARGUMENTS") as pdf:
    text = "\n".join(p.extract_text() or "" for p in pdf.pages)
print(text)
```

**If the file is `.docx`:** Run this via Bash:
```python
try:
    import docx
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "python-docx", "--quiet"], check=True)
    import docx
doc = docx.Document(r"$ARGUMENTS")
print("\n".join(p.text for p in doc.paragraphs))
```

**If the file is `.xlsx`:**

First, display this message to the user:

> **Note:** For Excel input, your file must include at least two columns: one containing the statement text, and one containing a unique ID for each statement (e.g., S1, S2…). If your file doesn't have these yet, please add them before proceeding.

Then run via Bash:
```python
try:
    import openpyxl
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "openpyxl", "--quiet"], check=True)
    import openpyxl
wb = openpyxl.load_workbook(r"$ARGUMENTS")
ws = wb.active
all_rows = list(ws.iter_rows(values_only=True))
headers = list(all_rows[0])
data_rows = all_rows[1:]
print("Columns:", headers)
print(f"\nFirst 3 rows (of {len(data_rows)} total):")
for row in data_rows[:3]:
    print(row)
wb.close()
```

Save `headers` and `data_rows` as **Excel input state** — `headers` is the list of column names, `data_rows` is the full list of data rows. Proceed to **Step 1.5** to select columns and classify statements.

**If the file is `.csv`:** Run this via Bash:

```python
import csv
with open(r"$ARGUMENTS", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    headers = list(reader.fieldnames or [])
print("Columns:", headers)
print(f"Total rows: {len(rows)}")
for row in rows[:3]:
    print(dict(row))
```

Check whether the file contains `id`, `type`, and `original_text` columns:

- **If all three columns are present:** This is a pre-classified statement list from a previous coding session. Load all rows as `{"id": ..., "type": ..., "original_text": ...}` dicts and save as the **statement data**. Present the list to the researcher for confirmation (use the presentation rule from Step 5: full table if ≤ 50 statements, file-review summary if more):

  | ID | Type | Abbreviated Original Text |
  |----|------|--------------------------|

  Then ask: *"This is the statement list saved from a previous coding session. Does everything look correct? If any statements should be reclassified or removed, let me know now. Otherwise reply 'yes' to proceed."*

  Wait for the researcher's confirmation. Apply any requested changes. Save the confirmed list as the **authoritative statement list**. Skip Steps 4 and 5.

  Continue to Step 2.

- **If the required columns are not present:** Tell the researcher the file does not appear to be a pre-classified statement list (expected columns: `id`, `type`, `original_text`) and ask them to check the file or provide input in a supported format (`.txt`, `.pdf`, `.docx`, `.xlsx`). Do not proceed.

**If the file is `.doc`:** Tell the user this format requires conversion and ask them to save as `.docx` or `.txt` first. Do not proceed.

After successfully loading the document (for `.txt`, `.pdf`, `.docx`, `.xlsx`, or a pre-classified `.csv`), initialize the session state via Bash:

```
python "<skill_dir>/session.py" "$ARGUMENTS" init
```

---

### Step 1.5 — Excel Column Selection & Statement Classification *(xlsx input only — skip for all other input types)*

At the start of this step, read the session state: `python "<skill_dir>/session.py" "$ARGUMENTS" get`

1. Use AskUserQuestion to ask:

   *"Which column contains the statement text?"*

   List the column names from `headers` (saved in Step 1) as a bulleted list of options.

2. Use AskUserQuestion to ask:

   *"Which column contains the statement IDs?"*

   List the column names from `headers` as a bulleted list of options.

3. Run this via Bash to extract all rows using the column names the researcher selected in sub-steps 1 and 2 (substitute the researcher's exact column names for `TEXT_COLUMN` and `ID_COLUMN`):

```python
import openpyxl
wb = openpyxl.load_workbook(r"$ARGUMENTS")
ws = wb.active
all_rows = list(ws.iter_rows(values_only=True))
headers = list(all_rows[0])
text_idx = headers.index("TEXT_COLUMN")
id_idx = headers.index("ID_COLUMN")
statements = [{"id": str(row[id_idx]), "text": str(row[text_idx])} for row in all_rows[1:] if row[id_idx] is not None]
for s in statements:
    print(f"  {s['id']}: {s['text'][:80]}")
print(f"\nTotal: {len(statements)} statements")
wb.close()
```

Save the resulting list of `{"id": ..., "text": ...}` dicts as the **statement data**. Each entry is a pre-delineated atomic statement — do not decompose or split rows.

4. Classify each statement as **REG**, **CONST**, or **NON-IS** using the normative-force and syntactic heuristics from `reference/04-heuristics.md`. Note: the document zone prior (Step 4 item 2) cannot be applied here because Steps 4 and 5 are skipped for xlsx input — rely on the statement text alone.

5. Present the classification to the researcher using the presentation rule from Step 5 (full table if ≤ 50 statements; otherwise write the statement-list CSV first and show a summary + 10-row sample, asking the researcher to review the file):

   | ID | Type | Abbreviated Original Text |
   |----|------|--------------------------|

   Then ask:

   *"Does this classification look correct? If any statements should be reclassified, let me know now. Otherwise reply 'yes' to proceed."*

6. Wait for the researcher's confirmation. Apply any requested reclassifications. Save the confirmed list as the **authoritative statement list** — this replaces the output of Step 5 for all downstream steps.

Update the session state: `python "<skill_dir>/session.py" "$ARGUMENTS" set current_step '"1.5"'`

Continue to Step 2.

---

### Step 2 — Ask the Researcher: Coding Level

At the start of this step, read the session state: `python "<skill_dir>/session.py" "$ARGUMENTS" get`

Use AskUserQuestion to ask:

**Question 1:** "At which level of expressiveness would you like the coding to be performed?"
- **IG Core** — Basic structural analysis. Identifies all components at a fundamental level. Best for first-pass coding or large documents. (Recommended for first use)
- **IG Extended** — Deep structural analysis. Adds property hierarchies, component-level nesting, and fine-grained context categorization. Best for complex documents or computational applications.
- **IG Logico** — Full semantic annotation. Builds on IG Extended by adding institutional function labels and ontological annotations (animacy, role, metatype). Best for theory-linked analysis.

Wait for the researcher's answer before proceeding. Save the selected level as the **Coding Level** for all subsequent steps.

Then update the session state (substitute the researcher's selection):

```
python "<skill_dir>/session.py" "$ARGUMENTS" set coding_level '"IG Core"' current_step '"2"'
```

---

### Step 3 — Ask the Researcher: Output Format

At the start of this step, read the session state: `python "<skill_dir>/session.py" "$ARGUMENTS" get`

Use AskUserQuestion to ask:

**Question 2:** "What output format(s) would you like?"
- **In-chat markdown** — Displays full coding in the conversation (original text, IG Script, notes per statement + summary table). Best for review and iteration.
- **CSV / Excel file** — Writes a structured file to disk with one row per statement and one column per IG component. Best for spreadsheet analysis and inter-coder reliability.
- **IG Parser .txt file** — Writes a plain-text file formatted for direct input into the IG Parser tool (github.com/chrfrantz/IG-Parser). Best for computational analysis.
- **All of the above** — Produces all three outputs.

Allow multi-select. Wait for the researcher's answer before proceeding.

> Note: the coded CSV (`<doc_base>_IG_coded.csv`) is **always written** regardless of this selection — it is the input for validation (Step 6) and complexity metrics (Step 11). The selection controls which outputs are *presented* to the researcher.

After recording the researcher's format preference, ask:

**Question 3:** "Would you like to use **multi-agent mode**? Three independent agents will code the document separately. Any disagreement — in statement type, component presence, or component content — will be flagged for your review in a `_review.csv` file saved alongside your other outputs.
- **Yes — multi-agent** (recommended for research use; slower)
- **No — single agent** (faster)"

Save the response as **Multi-Agent Mode**: enabled / disabled.

**If Coding Level is IG Extended or IG Logico**, also ask:

**Question 4:** "Would you like to compute **institutional complexity metrics** after coding? Metrics are derived from the logical operators in each encoded statement and are written to a separate `_IG_metrics.csv` file.
- **Yes** — proceed to select metrics
- **No** — skip"

If the researcher answers **Yes**, ask:

**Question 4a:** "Which metrics would you like to compute? (Select all that apply)

*Basic:*
- [ ] Tree Depth — nesting depth of the encoded statement (1 = flat)
- [ ] ISC — Institutional State Complexity (Eq. 8.1): product of operator variability across nesting levels
- [ ] ISR — Institutional State Regimentation (Eq. 8.2): product of regimentation weight across levels

*Component-level (Table 8.7):*
- [ ] Conditions Variability + Option Count — variability introduced by Cac operators (level 0)
- [ ] Discretion Extent + Option Count — variability introduced by Aim operators (level 0)
- [ ] Activity State Variability + Count — variability from nested Cac (level ≥ 1)
- [ ] Application Variability + Option Count — variability from Bdir/Bind operators (level 0)"

Save as **Compute Metrics**: enabled / disabled and **Selected Metrics**: comma-separated keys from `{depth, isc, isr, conditions, discretion, activity_state, application}` matching the researcher's selections.

Then update the session state (substitute the researcher's responses; if coding level is IG Core or researcher declined metrics, set compute_metrics false and selected_metrics []):

```
python "<skill_dir>/session.py" "$ARGUMENTS" set output_formats '["csv","ig_parser"]' multi_agent_mode true compute_metrics false selected_metrics '[]' current_step '"3"'
```

---

### Step 4 — Pre-Coding Familiarization

At the start of this step, read the session state: `python "<skill_dir>/session.py" "$ARGUMENTS" get`

*(Skip this step if `input_type` is `xlsx` or `csv` — document familiarization is not applicable to pre-identified statement lists. Statement list already confirmed in Step 1.5 or Step 1.)*

Scan the document and report:

1. **Document type** — What kind of rule document is this? (regulation, policy, bylaw, statute, etc.)
2. **Document zones** — Identify the approximate span of each zone: preamble/recitals (presumptive NON-IS), definitions (presumptive CONST), and policy instructions (presumptive IS). Note any zone boundaries that are unclear or absent.
3. **Key actors** — Candidates for Attributes (REG) / Constituted Entities (CONST)
4. **Key actions** — Candidates for Aims (REG) / Constitutive Functions (CONST)
5. **Apparent statement mix** — Primarily regulative, constitutive, or mixed?
6. **Definitions section** — If present, note defined terms; these set the decomposition level
7. **Confirmed settings** — Coding level: [level chosen in Step 2] | Output: [format(s) chosen in Step 3]

Then update the session state: `python "<skill_dir>/session.py" "$ARGUMENTS" set current_step '"4"'`

---

### Step 5 — Identify & Delineate Institutional Statements

At the start of this step, read the session state: `python "<skill_dir>/session.py" "$ARGUMENTS" get`

*(Skip this step if `input_type` is `xlsx` or `csv` — statement list already confirmed in Step 1.5 or Step 1.)*

Scan the document and identify all candidate institutional statements. For each:

- Strip extraneous punctuation (bullets, roman numerals, section markers)
- Reconstruct passive-voice statements into active form **only when the actor appears explicitly in the same sentence or the immediately adjacent sentence** — mark the reconstructed actor with `[ ]` using its exact name from the text. If the actor is not present in the same or adjacent sentence, do not rewrite the statement; leave `A` empty and add a `notes` entry: *"actor absent from text — manual coding required"*
- Decompose compound statements (multiple aims, multiple attributes) into separate logically-combined atomic statements
- Label each with a unique ID: `S1`, `S2`, `S3`, ...
- Classify each as: **REG** (regulative), **CONST** (constitutive), or **NON-IS** (not an institutional statement — retain but do not encode). Do not use HYB — if a statement appears hybrid, assign the type that reflects its **primary institutional function**. Apply the document zone identified in Step 4 item 2 as a prior: statements in the preamble/recital zone are presumptive NON-IS. See `reference/04-heuristics.md` for full NON-IS criteria and REG/CONST decision rules.

**Presentation rule (applies here and in Steps 1 and 1.5):**

- **≤ 50 statements:** Present the full table in-chat with columns: ID | Type | Abbreviated Original Text
- **> 50 statements:** Do **not** paste the full table into the chat. Save the statement list CSV first (see below), then display: the total count, a count per type (REG / CONST / NON-IS), and the first 10 rows as a sample table. Ask the researcher to open `<doc_base>_statement_list.csv` and review it there.

Then ask: *"Does this classification look correct? If any statements should be reclassified or removed, let me know now. Otherwise reply 'yes' to proceed."*

Wait for the researcher's confirmation. Apply any requested reclassifications (and re-save the CSV if it was already written).

Save the confirmed statement list: use the Write tool to create `<doc_base>_statements.json` containing the list of `{"id": ..., "type": ..., "original_text": ...}` dicts, then run via Bash:

```
python "<skill_dir>/write_rows.py" "<doc_base>_statements.json" "<doc_base>_statement_list.csv" --format statements
```

Confirm the saved path to the researcher: *"Statement list saved to `<doc_base>_statement_list.csv`. You can submit this file to the skill in a future session to code the same statements at a different level, skipping the identification step."*

Update the session state:

```
python "<skill_dir>/session.py" "$ARGUMENTS" set statement_list_path '"<doc_base>_statement_list.csv"' current_step '"5"'
```

---

### Step 6 — Encode Each Statement

At the start of this step, read the session state: `python "<skill_dir>/session.py" "$ARGUMENTS" get`

**If Multi-Agent Mode is ENABLED**, skip the encoding below and do this instead:

1. Derive `<doc_base>` and `<skill_dir>` per the Conventions section.

2. **If input was `.xlsx` or a pre-classified `.csv`:** The authoritative statement list was already established in Step 1.5 (or Step 1). Use it directly as the **reference statement list** and skip to item 3. Do not re-run Steps 4 or 5.

   **Otherwise:** The statement list was confirmed and saved in Step 5. Use it as the **reference statement list**.

3. **Ensure the statement list CSV exists.** If it was not yet saved (e.g., xlsx/csv input), write it now via `<doc_base>_statements.json` + `write_rows.py --format statements`, exactly as in Step 5, and update `statement_list_path` in the session state. This file is required for validation in item 7.

   Then present the reference statement list to the researcher one final time before dispatch (using the Step 5 presentation rule: full table if ≤ 50 statements, file-review summary if more) and ask:

   *"Here is the statement list that will be dispatched to the coding agents. Does this look complete? If any statements are missing or should be removed, let me know now. Otherwise reply 'yes' to proceed with agent dispatch."*

   Wait for the researcher's reply. If they provide corrections (additions or removals), update the reference statement list, re-save the statement list CSV, and update the session state before proceeding. Do not dispatch agents until the researcher confirms.

4. **Document size check before dispatch.** Count the number of statements in the confirmed reference list.

   - **≤ 25 statements:** Dispatch all statements in a single batch (proceed as described below).
   - **> 25 statements:** Split the reference list into consecutive batches of up to 25 statements (e.g., S01–S25, S26–S50, …). For each batch: write a per-batch statement list (`<doc_base>_statement_list_batchK.csv`, via `write_rows.py --format statements`), dispatch 3 agents (items 5–7 below), collect their AGENT_DATA blocks, write and validate the three per-batch agent CSVs, then proceed to the next batch. Do not hold more than one batch's AGENT_DATA blocks in context simultaneously. After all batches are written, concatenate the per-batch CSVs per agent (e.g. `_batch1_agent1.csv` + `_batch2_agent1.csv` + … → `_IG_agent1.csv`), then run the inter-agent merge once.

   > **Batch size note:** The 25-statement limit balances agent coding quality against the number of agent calls required for large documents. Larger batches reduce total agent calls but increase the risk of agents skipping statements or producing lower-quality encodings.

   **Agent call estimate:** Calculate total agent calls: `B × 3` if Multi-Agent Mode is ENABLED, `B × 1` if DISABLED (where B is the number of batches). If total calls exceed 9, display this notice and wait for the researcher's reply before dispatching:

   > ⚠ **Large document notice:** Coding this document will require approximately **[N] agent calls** across **[B] batches** of up to 25 statements each. This may take considerable time.
   >
   > To reduce agent calls, consider:
   > - **Switch to single-agent mode** — reduces calls from [N] to [B] *(show only if multi-agent is currently enabled)*
   > - **Split the document** — code it in separate sections, submitting each as its own run; the saved `_statement_list.csv` can be split accordingly
   >
   > Reply **'proceed'** to continue as configured, **'single-agent'** to switch modes, or **'split'** for guidance on dividing the document.

   If the researcher replies **'single-agent'**: update Multi-Agent Mode to DISABLED and recalculate total calls as B × 1. If the researcher replies **'split'**: explain how to divide the statement list into sections (e.g., by article, chapter, or fixed count), then stop — do not dispatch until the researcher resubmits a section. If the researcher replies **'proceed'**: continue as below.

   Update the session state with the batch configuration (substitute actual values):

   ```
   python "<skill_dir>/session.py" "$ARGUMENTS" set batch_config '{"total_statements": 80, "batch_size": 25, "num_batches": 4, "completed_batches": 0}' current_step '"6"'
   ```

5. **Determine the reference files for this run.** Agents read the reference files themselves — do not paste reference content into the prompt. Build the list of absolute paths from the coding level and the statement types present in the (batch) list:

   | File | Include when |
   |------|--------------|
   | `<skill_dir>/reference/01-components.md` | always |
   | `<skill_dir>/reference/05-symbols.md` | always |
   | `<skill_dir>/reference/02-regulative-coding.md` | any REG statement in the batch |
   | `<skill_dir>/reference/03-constitutive-coding.md` | any CONST statement in the batch |
   | `<skill_dir>/reference/06-nesting.md` | coding level is IG Extended or IG Logico |
   | `<skill_dir>/reference/07-context-taxonomy.md` | coding level is IG Extended or IG Logico |
   | `<skill_dir>/reference/08-logico-annotations.md` | coding level is IG Logico |

   Dispatch 3 agents in parallel using `superpowers:dispatching-parallel-agents`. Each agent receives this instruction (substitute N = 1, 2, 3 for the run number, the actual reference file paths, and paste the confirmed statement list for STATEMENT_LIST):

> You are an expert IG 2.0 coder. Encode the statement list below in IG Script. Do not ask the user any questions — all settings are fixed.
>
> **Fixed settings:**
> - Coding level: [Coding Level from Step 2]
>
> ## Reference Files — read these FIRST
>
> Before coding anything, use the Read tool to read each of the following files in full. They contain the complete coding rules you must apply. Do not read any other files or directories, and do not rely on prior knowledge of IG coding where it conflicts with these files:
>
> - [absolute path to each reference file from the table above, one per line]
>
> ---
>
> **Pre-confirmed statement list — types are final:**
>
> The `type` field for each statement has been determined by the orchestrator. **Do not change any statement's type under any circumstances.** Do not apply classification heuristics — the types below are authoritative. Your task is component coding only.
>
> STATEMENT_LIST
>
> **Your task:** Encode each statement in the pre-confirmed list above at the specified coding level, applying the rules in the reference files.
>
> **Verbatim extraction rule:** Every component value must be a verbatim substring of that statement's `original_text` — copied exactly, not paraphrased, reordered, or summarized. The only permitted non-verbatim content is: (1) `[ ]`-bracketed reconstructions under the Actor Sourcing Rules in the reference files (an actor name copied exactly from the source text, or exactly `[any person]`), and (2) mechanically reconstructed nominalized verbs (e.g., "submission of X" → `[submits]`). If you cannot fill a component with verbatim text, leave it empty and explain in `notes`.
>
> Do not add, remove, split, or merge statements, and do not change the type of any statement. Do NOT attempt to use the Write or Bash tools — sub-agents run in a sandboxed context and cannot receive interactive permission prompts.
>
> After completing all encoding, output your coded rows using this exact format at the end of your response:
>
> ### AGENT_DATA
> ```python
> [
>     {"id": "S1", "type": "REG", "coding_level": "IG Core", "original_text": "...", "A": "...", "A_prop": "", "D": "...", "I": "...", "Bdir": "...", "Bdir_prop": "", "Bind": "", "Bind_prop": "", "Cac": "", "Cex": "", "O": "", "E": "", "E_prop": "", "M": "", "F": "", "P": "", "P_prop": "", "ig_script_full": "...", "notes": "..."},
>     ...one dict per statement...
> ]
> ```
>
> Every dict must have exactly these 23 keys in this order:
> `id, type, coding_level, original_text, A, A_prop, D, I, Bdir, Bdir_prop, Bind, Bind_prop, Cac, Cex, O, E, E_prop, M, F, P, P_prop, ig_script_full, notes`
>
> Leave unused fields as empty strings `""`. Do not omit any key. The orchestrator will extract this block and write the CSV file.
>
> **Output size discipline:** Do not reproduce the full original text inside `ig_script_full` if it is longer than the IG Script encoding itself; the `original_text` field already captures it. Keep `notes` to one sentence per statement. This keeps the AGENT_DATA block small enough for the orchestrator to process without context overflow.

6. Wait for all 3 agents to complete.

7. **Collect agent data, write CSVs, and validate.** For each agent N (1, 2, 3):

   - Locate the `### AGENT_DATA` block in the agent's response.
   - Use the Write tool to create `<doc_base>_agentN_rows.json` containing the agent's list of dicts, transcribed exactly (convert it to valid JSON: double-quoted strings, no trailing commas).
   - Run via Bash: `python "<skill_dir>/write_rows.py" "<doc_base>_agentN_rows.json" "<doc_base>_IG_agentN.csv" --format coded` (append `_batchK` to both filenames when batching).
   - **Validation gate:** run via Bash:

     ```
     python "<skill_dir>/validate.py" "<doc_base>_IG_agentN.csv" "<doc_base>_statement_list.csv" --level "<Coding Level>"
     ```

     (use the per-batch statement list when batching)

   - **If the validator reports ERRORs:** re-dispatch that one agent **once**, with the same prompt plus an appended section: *"Your previous output failed validation with the errors below. Fix every error and output the complete corrected AGENT_DATA block (all statements, not only the corrected ones):"* followed by the validator's ERROR lines. Replace the JSON and CSV with the corrected output and re-run the validator. If errors persist after the retry, keep the CSV, and report the remaining error lines to the researcher — the affected statements will be flagged downstream.
   - **WARNINGs** (e.g., non-verbatim values) do not block the merge; collect them and report them in Step 10 (Coding Notes).

   After all three CSVs exist and have been validated, proceed to **Step 6.5**.

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
- *(IG Extended and IG Logico)* [reference/07-context-taxonomy.md](reference/07-context-taxonomy.md) — context annotation types
- *(IG Logico only)* [reference/08-logico-annotations.md](reference/08-logico-annotations.md) — semantic annotation guide

**Verbatim extraction:** Every component value must be a verbatim substring of the statement's `original_text`. The only permitted non-verbatim content is `[ ]`-bracketed reconstruction under the Actor Sourcing Rules (`reference/04-heuristics.md`) and mechanically reconstructed nominalized verbs (e.g., `[submits]`). If a component cannot be filled verbatim, leave it empty and explain in `notes`.

**At IG Extended and IG Logico:** Every `Cac` and `Cex` with explicit content must carry a `[ctx=TYPE]` annotation per `07-context-taxonomy.md`. Do not leave context components unannotated at these levels.

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

**Single-agent validation gate.** After encoding all statements:

1. Use the Write tool to create `<doc_base>_coded_rows.json` containing the full list of coded row dicts.
2. Run via Bash: `python "<skill_dir>/write_rows.py" "<doc_base>_coded_rows.json" "<doc_base>_IG_coded.csv" --format coded`
3. Run via Bash: `python "<skill_dir>/validate.py" "<doc_base>_IG_coded.csv" "<doc_base>_statement_list.csv" --level "<Coding Level>"`
4. **If the validator reports ERRORs:** fix the affected rows yourself (you are the coder), update the JSON, and re-run steps 2–3 until no errors remain. Report any WARNINGs in Step 10.

---

### Step 6.5 — Merge Agent Outputs (Multi-Agent Mode only)

At the start of this step, read the session state: `python "<skill_dir>/session.py" "$ARGUMENTS" get`

If Multi-Agent Mode is ENABLED, run the merge script via Bash:

```python
import subprocess, sys, os

# Substitute actual values resolved in Step 6:
skill_dir = r"ACTUAL_SKILL_DIR"   # e.g. r"C:\path\to\ig-skill"
doc_base  = r"ACTUAL_DOC_BASE"    # e.g. r"C:\path\to\document" (no extension)

agent_csvs      = [f"{doc_base}_IG_agent{i}.csv" for i in range(1, 4)]
consensus_csv   = f"{doc_base}_IG_coded.csv"
review_csv      = f"{doc_base}_IG_review.csv"
reliability_csv = f"{doc_base}_IG_reliability.csv"

result = subprocess.run(
    [sys.executable, os.path.join(skill_dir, "merge.py")]
    + agent_csvs + [consensus_csv, review_csv],
    capture_output=True, text=True,
)
print(result.stdout)
if result.returncode != 0:
    print("merge.py error:", result.stderr)
```

After merge.py completes, immediately run the reliability script via Bash:

```python
import subprocess, sys, os

result = subprocess.run(
    [sys.executable, os.path.join(skill_dir, "reliability.py")]
    + agent_csvs + [reliability_csv],
    capture_output=True, text=True,
)
print(result.stdout)
if result.returncode != 0:
    print("reliability.py error:", result.stderr)
```

Then read the reliability CSV and display an in-chat summary via Bash:

```python
import csv

rows = []
with open(reliability_csv, encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

overall = next(r for r in rows if r["field"] == "OVERALL")
field_rows = [r for r in rows if r["field"] != "OVERALL"]

print(f"\nOverall: {overall['pct_agreement']}% full agreement | Krippendorff's α = {overall['krippendorffs_alpha']}")
print(f"{'Field':<12} {'n':>5} {'% agree':>9} {'α':>8}")
print("-" * 38)
for r in field_rows:
    print(f"{r['field']:<12} {r['n_statements']:>5} {r['pct_agreement']:>9} {r['krippendorffs_alpha']:>8}")
```

Display the reliability summary to the researcher using this in-chat format:

**Inter-coder reliability (3 agents)**

| Field | n | % Agreement | Krippendorff's α |
|-------|---|-------------|-----------------|
| [one row per field from the CSV] |
| **OVERALL** | [n] | [pct] | [α] |

Then add this note: *"Percent agreement = proportion of statements where all 3 agents produced identical values. Krippendorff's α accounts for chance agreement; α ≥ 0.80 is the conventional threshold for reliability in content analysis. For free-text component fields (A, I, Bdir, etc.) exact-string matching is used — minor wording differences count as disagreements, so α for those fields will tend to be conservative. (Note: the consensus/review files use a more forgiving comparison — case, leading articles, and trailing punctuation are normalized before voting — so the review CSV may flag fewer disagreements than the α statistics imply.) The full per-field breakdown is saved to `[base]_IG_reliability.csv`."*

After the script completes:
- Load `consensus_csv` into the internal data record: read each row and treat it as a coded statement record with the same fields as the single-agent path (`id`, `type`, `coding_level`, `original_text`, `A`, `A_prop`, `D`, `I`, `Bdir`, `Bdir_prop`, `Bind`, `Bind_prop`, `Cac`, `Cex`, `O`, `E`, `E_prop`, `M`, `F`, `P`, `P_prop`, `ig_script_full`, `notes`). This record is then available for Steps 7, 8, and 9 exactly as if single-agent encoding had produced it.
- Load `consensus_csv` as the data source for Steps 7, 8, 9 (use the `review_flag` and `disagreement_fields` columns as needed).
- Report to the researcher: total statements coded, number flagged for review, paths to the review CSV and reliability CSV.
- **Fields showing `UNDETERMINED`** had no majority agreement — all three agents produced different values (after normalization). These fields are flagged in the review CSV with all three agent values for manual adjudication. Complexity metrics for statements with `UNDETERMINED` in `ig_script_full` will default to depth=1, ISC=1, ISR=1.
- Cross-check the consensus CSV statement IDs against your reference statement list from Step 6. If any statement you identified is absent from the consensus CSV (all 3 agents missed it), flag it explicitly: report those IDs to the researcher as "Statements identified by the orchestrator but absent from all agent outputs — require manual coding." Add a `review_flag = TRUE` row for each missing statement to the consensus CSV with all component fields empty and `disagreement_fields = "missing from all agent runs"`. (The Step 6 validation gate should have prevented this; this check is a final safety net.)
- If in-chat markdown was selected, display each statement using the in-chat display format defined in the encoding section above. Use the consensus values from `consensus_csv` for each statement. For any statement where `review_flag = TRUE`, use the `[⚠ Sn] REVIEW REQUIRED` format defined there, including the `disagreement_fields` value on the "Flagged fields" line.

Update the session state: `python "<skill_dir>/session.py" "$ARGUMENTS" set current_step '"6.5"'`

---

### Step 7 — Generate CSV / Excel Output (if selected)

At the start of this step, read the session state: `python "<skill_dir>/session.py" "$ARGUMENTS" get`

The coded CSV (`<doc_base>_IG_coded.csv`) already exists at this point — written by the single-agent validation gate (Step 6) or by merge.py (Step 6.5). Every row carries a `skill_version` column identifying the guideline version used (from the skill's `VERSION` file).

- **If CSV output was selected:** confirm the path to the researcher.
- **If the researcher selected neither CSV nor Excel:** tell the researcher the coded CSV exists anyway (it is the input for validation and metrics) and give its path.

**If Multi-Agent Mode was ENABLED:** also confirm:
- Review CSV: `[base]_IG_review.csv`
- Reliability CSV: `[base]_IG_reliability.csv`

If the researcher prefers Excel (`.xlsx`), convert the coded CSV via Bash:

```python
try:
    import openpyxl
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "openpyxl", "--quiet"], check=True)
    import openpyxl
import csv

coded_csv  = r"ACTUAL_CODED_CSV"   # <doc_base>_IG_coded.csv
excel_path = r"ACTUAL_EXCEL_PATH"  # <doc_base>_IG_coded.xlsx

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "IG Coded Statements"
with open(coded_csv, encoding="utf-8", newline="") as f:
    for row in csv.reader(f):
        ws.append(row)
wb.save(excel_path)
print(f"Excel written: {excel_path}")
```

After writing, confirm the file path to the researcher.

**If Multi-Agent Mode was ENABLED and Excel output was selected**, also add a `Reliability` sheet to the Excel workbook via Bash:

```python
import csv, openpyxl

excel_path      = r"ACTUAL_EXCEL_PATH"      # e.g. r"C:\path\to\document_IG_coded.xlsx"
reliability_csv = r"ACTUAL_RELIABILITY_CSV" # e.g. r"C:\path\to\document_IG_reliability.csv"

wb = openpyxl.load_workbook(excel_path)
if "Reliability" in wb.sheetnames:
    del wb["Reliability"]
ws = wb.create_sheet("Reliability")
with open(reliability_csv, encoding="utf-8", newline="") as f:
    for row in csv.reader(f):
        ws.append(row)
ws.append([])  # blank separator row
ws.append(["NOTE: Percent agreement = proportion of statements where all 3 agents produced identical values. "
           "Krippendorff's α (nominal) corrects for chance agreement; α ≥ 0.80 is the conventional reliability "
           "threshold in content analysis (Krippendorff, 2004). For free-text component fields (A, I, Bdir, etc.) "
           "exact-string matching is used — minor wording differences count as disagreements, so α for those fields "
           "will tend to be conservative. Interpret α most strictly for closed-vocabulary fields: type, D, M, F."])
wb.save(excel_path)
print(f"Reliability sheet added to {excel_path}")
```

---

### Step 8 — Generate IG Parser .txt Output (if selected)

At the start of this step, read the session state: `python "<skill_dir>/session.py" "$ARGUMENTS" get`

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

At the start of this step, read the session state: `python "<skill_dir>/session.py" "$ARGUMENTS" get`

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

At the start of this step, read the session state: `python "<skill_dir>/session.py" "$ARGUMENTS" get`

Report:
- Statements with uncertain classification (suggest polymorphic treatment)
- Components that required inference — noted with `[ ]` in IG Script
- Logical operators resolved from ambiguous natural language (`and/or` → `[OR]` or `[XOR]`)
- Passive constructions requiring actor inference
- Any statements decomposed from a single source sentence
- Validator WARNINGs collected in Step 6 (e.g., non-verbatim component values), with the affected statement IDs
- Recommendations for inter-coder reliability checks

---

### Step 11 — Institutional Complexity Metrics *(IG Extended / IG Logico only; skip if Compute Metrics = disabled)*

At the start of this step, read the session state: `python "<skill_dir>/session.py" "$ARGUMENTS" get`

Run `complexity.py` on the coded CSV and write the metrics to a `_IG_metrics.csv` file.

Derive the metrics output path from the coded CSV: if the coded CSV is `[base]_IG_coded.csv`, write to `[base]_IG_metrics.csv`.

Run via Bash (substitute actual paths and the researcher's selected metric keys):

```python
import subprocess, sys, os

skill_dir  = r"ACTUAL_SKILL_DIR"    # directory containing complexity.py
coded_csv  = r"ACTUAL_CODED_CSV"    # e.g. r"C:\path\to\document_IG_coded.csv"
metrics_csv = r"ACTUAL_METRICS_CSV" # e.g. r"C:\path\to\document_IG_metrics.csv"
selected   = "SELECTED_METRIC_KEYS" # comma-separated, e.g. "depth,isc,isr,conditions"

result = subprocess.run(
    [sys.executable, os.path.join(skill_dir, "complexity.py"),
     coded_csv, metrics_csv, "--metrics", selected],
    capture_output=True, text=True,
)
print(result.stdout)
if result.returncode != 0:
    print("complexity.py error:", result.stderr)
```

After the script completes:
1. Confirm the path `[base]_IG_metrics.csv` to the researcher.
2. **If the output was Excel:** Add a `Complexity_Metrics` sheet to the Excel workbook using:

```python
import csv, openpyxl

excel_path  = r"ACTUAL_EXCEL_PATH"
metrics_csv = r"ACTUAL_METRICS_CSV"

wb = openpyxl.load_workbook(excel_path)
if "Complexity_Metrics" in wb.sheetnames:
    del wb["Complexity_Metrics"]
ws = wb.create_sheet("Complexity_Metrics")

with open(metrics_csv, encoding="utf-8", newline="") as f:
    for row in csv.reader(f):
        ws.append(row)

wb.save(excel_path)
print(f"Complexity_Metrics sheet added to {excel_path}")
```

3. Display an in-chat summary table showing ID, Type, and each selected metric column.
4. Note any statements that could not be parsed (empty `ig_script_full`) — these will show default values (depth=1, ISC=1, ISR=1, option counts=0).

---

## Quick Reference: IG Script Symbols

**Regulative:** `A` (Attributes) · `D` (Deontic) · `I` (Aim) · `Bdir` (Direct Object) · `Bind` (Indirect Object) · `Cac` (Activation Condition) · `Cex` (Execution Constraint) · `O` (Or else)

**Constitutive:** `E` (Constituted Entity) · `M` (Modal) · `F` (Constitutive Function) · `P` (Constituting Properties) · `Cac` · `Cex` · `O`

**Properties:** `,p` suffix · **Implied components:** `[ ]` · **Logical operators:** `[AND]` `[OR]` `[XOR]` `[NOT]`

**Nesting:** `{ }` for statement-level and component-level nesting
