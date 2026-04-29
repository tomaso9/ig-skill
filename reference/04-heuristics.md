# Statement Type Heuristics & Pre-Coding Guidelines

Source: IG 2.0 Codebook v1.4, Sections 2.5, 3

---

## Pre-Coding Steps

### General Steps (All Levels)

1. **Familiarize** with the institutional setting: read the document fully before coding
2. **Organize content** into three parts:
   - *Preamble* — contextualizes the institution; may contain both regulative and constitutive statements
   - *Definitions* — almost always constitutive; use to determine decomposition level
   - *Policy instructions* — core institutional statements, organized by sections/subsections
3. **Delineate statements**: identify sentence boundaries; note that one sentence may contain multiple institutional statements
4. **Verify** that each candidate statement meets minimum syntactic requirements:
   - Regulative: at least Attributes + Aim + Context (may be implied)
   - Constitutive: at least Constituted Entity + Constitutive Function + Context (may be implied)
5. **Text that is not an institutional statement**: retain and annotate as "domain-specific background"

### Data Cleaning

- Remove extraneous punctuation: bullets, roman numerals, section labels
- Fix typos that impede parsing
- Preserve all text content (do not delete non-IS text; mark it `NON-IS`)

### Passive-to-Active Conversion (IG Core recommended)

Convert passive statements to active form **only when the actor appears explicitly in the source text within a defined proximity window** (see Actor Sourcing Rules below). Mark the reconstructed actor with `[ ]` using its exact name as it appears in the text — do not paraphrase, generalize, or substitute.

- Original: *"Notifications of compliance must be sent to farmers within 30 days of facility inspections."*
- Active (actor named in same paragraph): *"[Certifier] must send farmers notifications of compliance within 30 days of facility inspections."*

Do **not** infer an actor from document-wide knowledge, general regulatory patterns, or training knowledge. If the actor cannot be identified from the proximity window, do not reconstruct the passive form.

### Actor Sourcing Rules

These rules determine when `[ ]` may be used and what goes in it. Apply them in order — use the first rule that matches.

| Priority | Situation | Action |
|----------|-----------|--------|
| 1 | Actor named explicitly in the **same sentence** (passive construction with "by [actor]" or equivalent) | Convert to active; use `[ ]` with actor's exact name from text |
| 2 | Actor named explicitly in the **immediately preceding or following sentence** | Convert to active; use `[ ]` with actor's exact name from text |
| 3 | Actor named explicitly **elsewhere in the same paragraph** | Use `[ ]` with actor's exact name; add note: *"actor inferred from paragraph [N]"* |
| 4 | Statement is an **impersonal prohibition** (*"X is prohibited"*, *"no person shall"*) **or an impersonal obligation** (*"X must be done"*, *"Y shall conform"*, *"Z are required to…"*) where the duty is universal — no actor class is specified or recoverable from the proximity window | Use `[any person]`. This encodes the semantic universal of the statement. **Only this exact form is permitted** — do not write `[any person or entity]`, `[person/user]`, `[person or entity]`, `[regulated entity]`, or any other variation. |
| 5 | Actor not present within the same paragraph | Leave `A` **empty**; add note: *"actor absent from text — manual coding required"* |

**Never use `[actor]`, `[actor inferred from context]`, `[any person or entity]`, `[person/user]`, `[regulated entity]`, or any other invented label.** Exactly two forms are permitted inside `[ ]`: (1) an actor name copied verbatim from the source text, or (2) `[any person]` under Priority 4. Nothing else.

**Hint (codebook p. 65):** When a statement contains an aim linked to an object as a noun (passive construction), this signals a missing or implied actor. Check prepositional clauses such as "by [actor]" for clues. If found, that actor is the Attribute; if not found within the same paragraph, leave `A` empty.

### Statement Decomposition (Pre-processing for IG Core)

Statements with multiple Aims should be decomposed into separate statements:
- *"The producer must establish and maintain year-round livestock living conditions."*
- → S1: *"The producer must establish year-round livestock living conditions."*
- → S2: *"The producer must maintain year-round livestock living conditions."*

---

## Non-Institutional Statements (NON-IS)

### Step 1: Apply the normative force test first

Meeting the minimum syntactic criteria (A + I for regulative; E + F for constitutive) is necessary but **not sufficient** for IS classification. A statement must also carry **normative force**:

- **Prescriptive/permissive/prohibitive force** — the statement establishes a duty, permission, or prohibition on an actor's future or ongoing behavior (regulative)
- **Constitutive force** — the statement establishes, modifies, or defines an institutional element — an actor, role, right, object, or rule (constitutive)

A statement that only asserts a fact, records a completed event, or describes a state of affairs carries **neither** kind of normative force and is **NON-IS**, regardless of whether it contains an actor and a verb.

> *"NYCDEP has submitted the proposed Watershed Regulations to NYSDOH."*
> → Has A + I + Bdir, but carries no forward-looking normative force. **NON-IS.**

> *"NYSDOH has issued a SEQR Findings Statement."*
> → Records a completed administrative act. **NON-IS.**

### Step 2: Apply the document zone prior

Rule documents typically have three zones with different base rates of IS:

| Zone | Content | Default presumption |
|------|---------|-------------------|
| **Preamble / recitals** | "Whereas" clauses, findings, contextual background, statements of purpose | **Presumptive NON-IS** — treat as NON-IS unless normative force can be demonstrated |
| **Definitions** | Defined terms for use throughout the document | Presumptive **CONST** |
| **Policy instructions** | The core operative rules, organized by sections and subsections | Presumptive **IS** |

Identify each zone during Step 4 pre-coding familiarization. When a candidate statement falls in the preamble/recital zone, apply heightened scrutiny before classifying it as IS.

### Recognizable NON-IS patterns

| Pattern | Signal | Example |
|---------|--------|---------|
| **Perfective past** | *"has [verb]ed"*, *"was [verb]ed"* — completed event | *"NYCDEP has submitted X to NYSDOH"* |
| **State-of-affairs declaration** | Bare factual assertion, no normative operator | *"The Watershed is located in..."* |
| **Recital / whereas clause** | *"Whereas..."*, *"The Parties acknowledge that..."* | Preamble text establishing shared factual basis |
| **Findings statement** | Records a determination already made | *"NYSDOH has issued a SEQR Findings Statement"* |
| **Bare cross-reference** | Points to content defined elsewhere; no rule of its own | *"as set forth in Attachment W"* (standalone sentence) |
| **Heading or label** | Section title, article header, organizational marker | *"Article III — Watershed Regulations"* |
| **Explanatory parenthetical** | Clarifies a term or abbreviation inline, without establishing a rule | *"(hereinafter 'the City')"* as a standalone sentence |

**Caution — perfective past in policy sections:** Some policy sections use perfective past to establish legal conditions precedent ("The City has registered contracts and paid first payments") — these may carry constitutive or regulative force. Apply the normative force test before defaulting to NON-IS.

### How to encode NON-IS rows

- Set `type` = `NON-IS`
- Populate `original_text` with the source sentence
- Leave **all IG component fields empty** (`A`, `D`, `I`, `Bdir`, `Bdir_prop`, `Bind`, `Bind_prop`, `Cac`, `Cex`, `O`, `E`, `E_prop`, `M`, `F`, `P`, `P_prop`, `ig_script_full`)
- Add a `notes` entry naming the pattern: e.g., *"perfective past — records completed submission; no prescriptive force"*

---

## Heuristics for Identifying Statement Types (REG vs. CONST)

### General Heuristics

| Question | If YES → |
|----------|----------|
| Does the statement introduce, parameterize, or modify fundamental aspects of the action situation (actor definitions, rights, roles, object definitions, affordances)? | **Constitutive** |
| Does the statement signal unambiguous agency and specify duty, discretion, or sanctions for transgression linked to an actor? | **Regulative** |
| Both criteria are satisfied? | → Assign the type that matches the statement's **primary institutional function** (see below) |

### Specific Heuristics (Table 4)

| Heuristic | Constitutive Signals | Regulative Signals |
|-----------|---------------------|--------------------|
| **Function** | Primary purpose: define, introduce, modify an entity, or parameterize the system | Primary purpose: compel, restrain, permit, assign expectations about an actor's behavior |
| **Consequence of Violation** | Violation leads to **systemic/existential** consequence (entity doesn't come about, policy invalidated) | Violation leads to **localized** consequence (sanction on an actor) |
| **Deontic vs. Modal** | Modal describes the general necessity/possibility of a constitution (*Access shall be maintained*) | Deontic describes duty/permission imposed on a responsible actor (*Certifier shall maintain access*) |
| **Actor/Entity as Target of Conferral** | Actor/entity is **receiving** a right, role, authority, or status | Actor is being **obligated** to perform a behavior |

### Recurring Type-Boundary Problems

Apply these rules to specific surface forms that consistently generate inter-coder disagreement. They take precedence over the general heuristics above when the pattern matches.

---

#### "are responsible for" statements

*"The Committee is responsible for reviewing permit applications."*

Default classification: **REG**. Treat "responsible for [verb]-ing" as a behavioral obligation; encode the gerund phrase as Aim. `A(Committee) D([must]) I(review) Bdir(permit applications)`. Note: *"'responsible for' treated as obligation"*.

**Override → CONST:** If the statement appears in an establishment or definitions section and assigns responsibility as part of *creating or defining a role* (e.g., *"The program officer, who shall be responsible for certification decisions, is hereby established"*), the primary function is constitutive; encode as CONST and capture the responsibility clause in P.

**Override → NON-IS:** If the statement records an existing organizational arrangement in descriptive, past-oriented language with no forward-looking normative force (*"The Environmental Office has historically been responsible for this area"*), classify NON-IS.

---

#### Passive constructions with inanimate grammatical subjects ("shall be documented")

*"Inspection results shall be documented."* / *"Records shall be maintained for three years."*

The presence of an inanimate subject does **not** change the statement type. Apply this two-question test:

> *"Is someone required to do something?"* → **REG** (leave A empty per Priority 5; do not reclassify as CONST or NON-IS because the actor is missing)
>
> *"Is something required to be/contain/consist of something?"* → **CONST** (`E` = the inanimate subject; `F` = the constitutive function; `P` = the required content)

**REG examples:** *"Results shall be documented"* (someone must document); *"Applications shall be submitted"* (someone must submit) — actor absent; leave A empty.

**CONST examples:** *"The application shall include the following items"* (E = application; F = shall include; P = the items); *"The plan shall be accompanied by a map"* (E = plan; F = shall be accompanied by; P = a map).

Discriminator: Can you reconstruct the passive as *"[actor] must [verb] [object]"* where [actor] is animate? If yes → REG. If the subject IS the thing being defined or constituted → CONST.

---

#### Objective/goal statements ("The goal of X is to…" / "The purpose of X is to…")

*"The purpose of this Part is to protect the watershed."*

Default classification: **NON-IS** — goal and purpose statements without a deontic modal and without an identifiable actor describe rationale but impose no obligation, permission, or constitutive effect.

**Override → CONST:** When the statement uses a modal of necessity (*"The purpose of this Part **shall be** to protect…"*), it constitutes the purpose as an institutional property: `E(this Part) M(shall) F(be) P(to protect the watershed)`.

**Override → REG:** When a goal clause is embedded in a genuine obligation (*"All certifiers shall ensure that the goal of organic integrity is maintained"*), classify as REG; the goal clause becomes Bdir.

---

#### Process-description statements using shall/will with an inanimate subject

*"The application process shall proceed as follows."* / *"The permit shall be issued within 30 days."*

When *shall/will* applies to an **inanimate process, document, or instrument** (not a named actor) and defines procedural sequence, form, or requirements, classify as **CONST**: the process or document is being constituted.

**REG contrast:** *"The hearing officer shall issue the permit within 30 days"* — animate named actor → REG.

Discriminator: Substitute the subject into *"[subject] must do this."* If that sentence is grammatically incoherent (because the subject is a process or document, not an actor), the statement is CONST.

---

#### "is required" / "is necessary" with an inanimate subject

*"A permit is required to operate in Zone I."* / *"Prior approval is necessary before construction."*

When the grammatical subject of "is required" or "is necessary" is an inanimate institutional object (permit, approval, certification, license, plan), classify as **CONST**: the statement establishes that object as a mandatory institutional prerequisite.

Encode: `E(permit) M(is) F(required) P(to operate in Zone I)`. If the condition reads more naturally as qualifying *when* the permit is required: `E(permit) M(is) F(required) Cac(to operate in Zone I)`.

**REG contrast:** *"The applicant is required to submit a permit application"* — animate subject → REG. Paraphrase and encode as `A(applicant) D(must) I(submit) Bdir(permit application)`.

---

#### Summary decision flowchart for the five patterns above

```
Does the statement describe rationale or purpose only (no modal, no actor)?
└── YES → NON-IS (goal/purpose pattern)

Does the statement have a modal (shall, must, will, is required)?
├── Animate subject or actor identifiable within proximity window?
│   └── YES → REG (use Actor Sourcing Rules for A)
└── Inanimate subject?
    ├── Subject is a process/document/instrument being constituted?
    │   └── YES → CONST
    └── Subject is a person-shaped obligation missing its actor?
        └── YES → REG (leave A empty per Priority 5)
```

---

## Interpretational Scope

When a statement is ambiguous between regulative and constitutive:

**Narrow scope**: Focus on the statement in isolation, including its direct semantics and function. Does not resolve links to other statements. → Tends toward constitutive for overarching parametric statements.

**Wide scope**: Resolve semantic links to other statements; may reconstruct the statement in behavioral terms. → Tends toward regulative via actor reconstruction.

**Best practice**: Define the interpretational scope at the beginning of the study/coding exercise and apply consistently.

---

## Statements with Both Regulative and Constitutive Features

Some statements serve both regulative and constitutive functions simultaneously. HYB is **not a valid type** — every statement must be resolved to either REG or CONST based on its primary institutional function.

### Decision rule: primary function

Ask: *What would be lost if this statement were removed from the document?*

- If the answer is **a behavioral constraint or permission on an actor** → **REG**
- If the answer is **a definition, role, right, status, or systemic structure** → **CONST**

### Regulative statement with embedded constitutive content

A regulative statement may introduce or reference an entity in its object component. Encode the overall statement as **REG**; the constitutive element is captured via nesting in Bdir or Bind:

```
A(Certifier) D(must) I(revoke) Bdir{E(certification) M(shall) [NOT] F(be valid)
P(for non-compliant operations)}.
```

### Constitutive statement with an Or-else clause

A constitutive statement may carry a regulative Or-else clause. Encode the overall statement as **CONST**; the regulative enforcement is captured in O:

```
E(Board) M(shall) F(consist of) P(seven members), O{A(Appointing Authority) D(must)
I(fill) Bdir(vacancies) Cex(within 30 days)}.
```

### Polymorphic statements

Some statements can be legitimately read as either REG or CONST (e.g., rights statements). Choose the encoding that best reflects the statement's function in this document. Record the alternative reading in the `notes` field. Do not produce two rows.

---

## Activation Condition vs. Execution Constraint: Decision Guide

```
Is the clause a precondition that activates the entire non-context part of the statement?
├── YES → Does it signal a discrete setting (temporal, spatial, event)?
│         ├── YES → ACTIVATION CONDITION (Cac)
│         └── NO  → EXECUTION CONSTRAINT (Cex)
└── NO  → Does it qualify the way the action is performed?
          └── YES → EXECUTION CONSTRAINT (Cex)
```

**Key terms by type:**

| Activation Condition signals | Execution Constraint signals |
|-----------------------------|------------------------------|
| *when*, *upon*, *starting*, *in the event that*, *once*, *after* (event) | *especially*, *particularly*, *specifically*, *in accordance with*, *annually*, *in person* |

**Context-clause interdependencies**: If clause B can only apply once clause A is satisfied, A is the activation condition and B is the execution constraint. If both must be satisfied together to activate the statement, both are activation conditions.
