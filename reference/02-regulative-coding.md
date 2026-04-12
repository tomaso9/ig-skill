# Regulative Statement Coding Guidelines

Source: IG 2.0 Codebook v1.4, Section 4.2

---

## IG Core — Regulative Statements

**IG Core** provides basic structural analysis. Human readable; moderate syntactic detail.

### General Coding Principles

1. Identify and encode: **Attributes** → **Deontic** → **Aim** → **Object(s)** → **Context** → **Or else**
2. Where a component is absent but inferable, enclose in `[ ]`
3. Attribute properties use `,p` suffix; objects similarly
4. Context defaults: no Activation Condition → *"under all conditions"*; no Execution Constraint → *"no constraints"*

### Component-by-Component Guidelines

#### Attributes (A)
- Decompose into actor + actor property where analytically meaningful
- Use policy definitions to determine decomposition level
- If a regulation distinguishes between types (e.g., organic vs. non-organic farmers), capture the type as a property

```
A,p(Certified) A(farmer) D(must) I(submit) Bdir(organic system plan) Cex(annually).
```

#### Deontic (D)
- Encodes prescriptive force: *must* (obligation), *may* (permission), *must not* / *may not* (prohibition)
- The deontic sits on a continuum; encode the explicit language used

```
A(certifier) D(must) I(notify) Bind(farmer) Bdir(of compliance).
```

#### Aim (I)
- The focal action verb of the statement
- For compound actions, decompose into separate logically-combined statements (see Decomposition below)

#### Object — Direct (Bdir) and Indirect (Bind)
- **Direct object**: receiver of the Aim
- **Indirect object**: entity toward/for which the Aim is directed at the direct object
- Caution: indirect objects preceded by prepositions are sometimes mistaken for context

```
A(certifier) D(must) I(send) Bind(farmer) Bdir(notification of compliance) Cex(within 30 days).
```

**Pitfall — Object vs. Constraint:** Ask: *Does this clause qualify the object, or qualify the action?*
- "audits on product stock" → qualifies the audit (type) → Object
- "twice per year" → qualifies when the action occurs → Execution Constraint

**Bdir vs. Bind for notification/reporting/filing statements:** When the statement involves sending, filing, forwarding, or notifying:
- **Bdir** = the document, report, or notification itself (the thing sent/filed)
- **Bind** = the recipient (the entity to/for whom it is sent)

```
A(certifier) D(must) I(send) Bind(farmer) Bdir(notification of compliance) Cex(within 30 days).
A(applicant) D(shall) I(forward) Bdir(copies of permit applications) Bind(to the supplier of water).
```

Do not misclassify recipients preceded by prepositions ("to X", "with X") as Execution Constraints — consider them as Bind first.

**Bdir_prop at IG Core:** Use `Bdir_prop` only when the policy functionally distinguishes the qualifier from the base object — that is, when different provisions apply to different subtypes of that object, or when the qualifier is itself a defined term. If the qualifier is merely descriptive and the same rules apply regardless, fold it into the `Bdir` text.
- *"Copies of permit applications and notices of intent"* → `Bdir(copies of permit applications and notices of intent)` (one combined Bdir; no functional subtype distinction)
- *"A written notification of noncompliance"* → `Bdir,p(written) Bdir(notification of noncompliance)` (only if "written" is a functionally distinct requirement in the regulation)

#### Context: Activation Condition (Cac) vs. Execution Constraint (Cex)

**Activation Condition**: Discretized setting or event that *activates* the non-context part of the statement.
- Signals a change in attributes, objects, or setting
- Linguistically: adverbial clauses (*when*, *upon*, *starting*, *in the event that*)

**Execution Constraint**: Qualifies *how* the action is performed without activating a new setting.
- Temporal, spatial, procedural modifiers
- Linguistically: qualifiers (*annually*, *in person*), prepositional phrases (*in accordance with*)

**Heuristic**: Can the action occur without this clause? If removing the clause changes *when* the rule applies → Activation Condition. If removing it only removes how → Execution Constraint.

**Exception clauses in prohibitions:** When a prohibition contains "except [condition]" or "except under [permit/authority]", code the exception as **Cex** — it qualifies the scope of the prohibition without changing when it is triggered.
- *"Transportation of hazardous materials is prohibited **except under permit** of the NYSDOT"* → `Cex(except under permit of the NYSDOT)`
- *"Disposal... is prohibited **except for incidental deposition** from plowing operations"* → `Cex(except for incidental deposition from plowing operations)`

Do **not** encode such exceptions as Or-else (O). O is reserved for consequence/sanction clauses (see below).

```
Cac(Upon entrance into agreement with organic farmer), A(certifier) D(must) I(inspect)
Bdir(farmer's operation) Cex(within 60 days).
```

#### Or else (O)
- Encodes **consequences or sanctions** for non-compliance — payoffs attached to the monitored statement
- Encoded as a **vertically nested** statement using braces
- Can itself contain horizontally nested statements
- **O is not for exception clauses.** "Except under permit X" or "except as determined by Y" belongs in **Cex**. O is only used when there is an explicit consequence of transgression (e.g., "or else certifier will revoke certification").

```
A(farmers) D(must not) I(apply) Bdir(synthetic chemicals) Cac(once certification is conferred),
O{A(certifier) D(will) I(revoke) Bdir(certification) from Bind(farmer)}.
```

For multiple or-else options:
```
O {{A(certifier) D(will) I(revoke) Bdir(certification) from Bind(farmer)}
   [XOR]
   {A(certifier) D(will) I(fine) Bdir(farmer)}}.
```

---

## Decomposition of Component-Level Combinations

When a statement contains **multiple values for the same component**, decompose into separate logically-combined atomic statements:

| Situation | Example | Decomposition |
|-----------|---------|---------------|
| Multiple Attributes | "Certifiers and Inspectors must seek accreditation" | S1: Certifiers... [AND] S2: Inspectors... |
| Multiple Aims | "Inspectors must sign and file reports" | S1: ...sign reports [AND] S2: ...file reports |
| Multiple Conditions | "Inspectors must conduct visits in person twice per year" | S1: ...in person [AND] S2: ...twice per year |

**Do NOT decompose** when components are inseparably coupled:
- "Farmers must pay $250 for application and service fees" — inseparable because the fee is combined.

---

## IG Extended — Regulative Statements

**IG Extended** adds fine-grained structural analysis. Enforces features optional at IG Core.

### Additional Features

1. **Property Hierarchy Decomposition**: Attributes, Objects, and their properties are decomposed into hierarchical relationships with numeric indices (`A,p1`, `A,p2`, `Bdir,p1,p1`)
2. **Component-level Nesting**: Components can be substituted with entire institutional statements (expressed in braces `{ }` on the component)
3. **Richer Context Categorization**: Context annotated by circumstantial type (temporal, spatial, procedural) per the Context Taxonomy
4. **Decomposition of Embedded Actions**: Nominalized actions (conceptual reification) are reconstructed as full institutional statements

### Component-Level Nesting Example

```
A,p1(certified) A(farmer) A,p2{whose Bdir(certification) is I([suspended]) by A(Secretary)
Cex(under this section)} D(may) Cac(at any time) I(submit) Bdir,p(recertification) Bdir(request).
```

### Embedded Action Reconstruction

Original: *"When an inspection reveals noncompliance, a notification shall be sent."*
→ Reconstruct as: *"When [Program Manager] inspects accredited certifying agent AND [Program Manager] reveals noncompliance, [Program Manager] shall send notification to certifying agent."*

---

## IG Logico — Regulative Statements

**IG Logico** adds semantic annotations to all components using the taxonomy prefixes from [04-heuristics.md](04-heuristics.md) and the taxonomies.

### Annotation Syntax

```
A[type=animate; role=originator](Program Manager)
D[stringency=prescription](must)
I[act=administer; regfunc=sanction](impose)
Bdir1,p[prop=quals](monetary) Bdir1[object=sanction](fine)
```

Statement-level annotation (precedes statement scope):
```
[regulativeStatement]{A(Official) D(must) I(impose) Bdir(fine).}
```

### Regulative Functions (regfunc annotation)

Common regulative functions to annotate on Aim:
- `detect violation` — reveal, identify, observe non-compliance
- `sanction` — fine, suspend, revoke, penalize
- `comply` — adhere, follow, conform
- `monitor` — inspect, audit, review
- `report` — notify, inform, submit
- `authorize` — certify, accredit, approve

---

## Full IG Core Example

**Original text:**
*"Organic certifier must send farmer notification of compliance within 30 days of inspection."*

**Coded (IG Core):**
```
A,p(Organic) A(certifier) D(must) I(send) Bind(farmer) Bdir(notification of compliance)
Cex(within thirty days of inspection).
```

**Coded (IG Extended):**
```
A,p1(Organic) A(certifier) D(must) I(send)
Bind[anim=animate](farmer) Bdir,p(of compliance) Bdir[anim=inanimate](notification)
Cex[type=temporal](within thirty days) Cex[type=event](of inspection).
```
