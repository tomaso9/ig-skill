# Context Taxonomy

Source: Frantz & Siddiki (2022), Section 5.1.6 (pp. 166–171, Fig. 5.7)

Required at **IG Extended** and above. Every `Cac` and `Cex` with explicit content must carry a `[ctx=TYPE]` annotation. Where a context component is absent (implied default), no annotation is needed.

---

## Annotation Syntax

Place the annotation between the component symbol and the opening bracket:

```
Cac[ctx=event](upon receipt of application)
Cex[ctx=temporal](within 30 days)
Cex[ctx=procedural](as specified in Section 5)
```

Multiple context types on a single component (use semicolons):

```
Cex[ctx=temporal; ctx=procedural](within 30 days as specified in Attachment A)
```

---

## The Four Context Categories

### 1. Substantive Context

Contextual aspects pertaining to the wider institutional setting and its metaphysical embedding. Three sub-types:

| Sub-type | Key: `ctx=` | Signals | Examples |
|----------|-------------|---------|---------|
| **Temporal** | `temporal` | Points in time, time frames, frequencies | *at 8 am*, *from 9am to 5pm*, *annually*, *within 30 days*, *before the deadline* |
| **Spatial** | `spatial` | Location, direction, path | *at the town hall*, *within Zone I*, *on the way home*, *through the watershed* |
| **Domanial** | `domain` | Activity realm, topical realm, existential realm | *during accreditation*, *for drinking water*, *in the context of organic operations* |

---

### 2. Procedural Context

Procedural or methodical aspects. Two sub-types:

| Sub-type | Key: `ctx=` | Signals | Examples |
|----------|-------------|---------|---------|
| **Procedural order** | `procedural` | Execution sequence, cross-references to instructions, mandatory procedures | *first…, second…*, *as specified in Section 5(2)*, *pursuant to*, *in accordance with*, *following the procedures laid out in* |
| **Method / Instrumental** | `method` | Means (instrument used) or manner (behavioral form) | *by mail*, *in person*, *by handshake*, *using the approved form* |

---

### 3. Aspirational Context

Motivation and objectives underlying a provision. Two sub-types:

| Sub-type | Key: `ctx=` | Signals | Examples |
|----------|-------------|---------|---------|
| **Purpose** | `purpose` | Goal or intent of the regulated activity | *in order to protect the watershed*, *for the purpose of compliance*, *to ensure public safety* |
| **Effect** | `effect` | Satisfaction of a prior condition or anticipated outcome | *if pollution thresholds are met*, *once certification is achieved*, *upon fulfillment of requirements* |

---

### 4. Situational Context

State transitions and situational changes specific to the institutional setting. Two sub-types:

| Sub-type | Key: `ctx=` | Signals | Examples |
|----------|-------------|---------|---------|
| **State** | `state` | A condition of affairs that persists over time; a precondition reflecting an ongoing circumstance | *when organic farmers are in violation*, *where the operation is non-compliant*, *if the permit is valid* |
| **Event** | `event` | An instantaneous occurrence that signals a state change; a trigger event | *upon accreditation*, *upon receipt of complaint*, *when a violation is detected*, *after the election of* |

---

## Decision Guide

```
Is the clause a precondition that activates the statement (Cac)?
│
├── Does it reference a point in time, duration, or frequency?  → ctx=temporal
├── Does it reference a location, direction, or path?           → ctx=spatial
├── Does it reference a topical or activity domain?             → ctx=domain
├── Does it reference a persistent state of affairs?            → ctx=state
└── Does it reference an instantaneous triggering event?        → ctx=event

Is the clause a qualifier on how the action is performed (Cex)?
│
├── Does it reference a time limit or schedule?                 → ctx=temporal
├── Does it cross-reference a procedure, section, or rule?      → ctx=procedural
├── Does it specify the means or manner of execution?           → ctx=method
├── Does it state the purpose or goal of the action?            → ctx=purpose
└── Does it state the expected effect or outcome?               → ctx=effect
```

**Tip — Cac vs. Cex:** If removing the clause changes *when* or *whether* the rule applies → Cac. If it only changes *how* → Cex. See `04-heuristics.md` for the full Cac/Cex decision flowchart.

---

## Compound and Uncertain Cases

- **Multiple types:** Annotate all that apply, semicolon-separated: `Cex[ctx=temporal; ctx=procedural]`
- **Domain-specific extension:** For specific research domains, the taxonomy may be extended with domain-specific sub-types. Document any extensions in study design notes.
- **Uncertain:** If the clause is clearly a context element but its type is ambiguous, annotate the broader category (e.g., `ctx=state` or `ctx=event`) and add a note in the `notes` field.

---

## Examples in IG Script

```
A(certifier) D(may) I(revoke) Bdir,p(violating farmers')
Bdir(certifications)
Cac[ctx=state](when organic farmers violate organic farming provisions)
Cex[ctx=procedural](following the procedures laid out in the regulation).

A(Program Manager) D(shall) I(send) Bdir,p(written) Bdir(notification)
Bind,p(accredited) Bind(certifying agent)
Cac[ctx=event](when inspection reveals noncompliance)
Cex[ctx=procedural](in accordance with Section 5).

A(certified organic farmers) D(must) I(submit) Bdir(organic system plan)
Cex[ctx=temporal](annually)
Cex[ctx=procedural](as specified in this Part).

E(no person) M(shall) F(discharge) P(pollutants)
Cac[ctx=domain](into the watershed)
Cex[ctx=procedural](except as provided in Section 18-24 of this Part).
```
