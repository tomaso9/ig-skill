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

Convert passive statements to active form to make the Attributes explicit:
- Original: *"Notifications of compliance must be sent to farmers within 30 days of facility inspections."*
- Active: *"[Certifier] must send farmers notifications of compliance within 30 days of facility inspections."*
- Note: mark inferred actor with `[ ]`

### Inferred Actor Labels (project convention)

When the responsible actor must be inferred, use brackets `[ ]` and apply the following standard labels:

| Situation | Standard label | Example |
|-----------|---------------|---------|
| Impersonal prohibition ("X is prohibited") | `[any person]` | `[any person] D([shall not]) I(discharge)...` |
| Passive obligation where actor is clear from section context | `[actor inferred from context, e.g., applicant]` | `[applicant] D(shall) I(forward)...` |
| Actor entirely unresolvable from text or context | `[actor]` | `[actor] D(must) I(report)...` |

**Hint (codebook p. 65):** When a statement contains an aim linked to an object as a noun (passive construction), this signals a missing or implied actor. Check prepositional clauses such as "by [actor]" for clues. If found, that actor is the Attribute; if not, infer from institutional context and mark with `[ ]`.

### Statement Decomposition (Pre-processing for IG Core)

Statements with multiple Aims should be decomposed into separate statements:
- *"The producer must establish and maintain year-round livestock living conditions."*
- → S1: *"The producer must establish year-round livestock living conditions."*
- → S2: *"The producer must maintain year-round livestock living conditions."*

---

## Heuristics for Identifying Statement Types

### General Heuristics

| Question | If YES → |
|----------|----------|
| Does the statement introduce, parameterize, or modify fundamental aspects of the action situation (actor definitions, rights, roles, object definitions, affordances)? | **Constitutive** |
| Does the statement signal unambiguous agency and specify duty, discretion, or sanctions for transgression linked to an actor? | **Regulative** |
| Both criteria are satisfied? | → Test for **Hybrid** (see below) |

### Specific Heuristics (Table 4)

| Heuristic | Constitutive Signals | Regulative Signals |
|-----------|---------------------|--------------------|
| **Function** | Primary purpose: define, introduce, modify an entity, or parameterize the system | Primary purpose: compel, restrain, permit, assign expectations about an actor's behavior |
| **Consequence of Violation** | Violation leads to **systemic/existential** consequence (entity doesn't come about, policy invalidated) | Violation leads to **localized** consequence (sanction on an actor) |
| **Deontic vs. Modal** | Modal describes the general necessity/possibility of a constitution (*Access shall be maintained*) | Deontic describes duty/permission imposed on a responsible actor (*Certifier shall maintain access*) |
| **Actor/Entity as Target of Conferral** | Actor/entity is **receiving** a right, role, authority, or status | Actor is being **obligated** to perform a behavior |

---

## Interpretational Scope

When a statement is ambiguous between regulative and constitutive:

**Narrow scope**: Focus on the statement in isolation, including its direct semantics and function. Does not resolve links to other statements. → Tends toward constitutive for overarching parametric statements.

**Wide scope**: Resolve semantic links to other statements; may reconstruct the statement in behavioral terms. → Tends toward regulative via actor reconstruction.

**Best practice**: Define the interpretational scope at the beginning of the study/coding exercise and apply consistently.

---

## Hybrid & Polymorphic Statements

### Regulative-Constitutive Hybrid (REG-CONST)
A **regulative statement** that embeds a constitutive sub-statement (e.g., introduces a new entity in the Object component).

```
A(Certifier) D(must) I(revoke) Bdir{E(certification) M(shall) [NOT] F(be valid)
P(for non-compliant operations)}.
```

The overall statement is **regulative** (primary purpose: regulate behavior), with a constitutive element nested in the object.

### Constitutive-Regulative Hybrid (CONST-REG)
A **constitutive statement** whose Or else clause is a regulative statement.

```
E(Board) M(shall) F(consist of) P(seven members), O{A(Appointing Authority) D(must)
I(fill) Bdir(vacancies) Cex(within 30 days)}.
```

### Polymorphic Statements
Statements that can be legitimately encoded in **both** regulative and constitutive forms (e.g., rights statements that can be read as actor obligation or entity parameterization). Encode both:

```
// Constitutive encoding:
E(Members) of the E,p(Council) M(shall) F(have the right) P(to hold any public office).

// Regulative encoding (via jural correlatives):
A([Authority]) D([must]) [NOT] I(disqualify) Bdir(member of the Council)
Cex(from holding any public office).
```

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
