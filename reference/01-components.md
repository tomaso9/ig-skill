# IG 2.0 Component Definitions

Source: Frantz & Siddiki, IG 2.0 Codebook v1.4 (October 2024)

---

## Regulative Statement Components

A **regulative statement** describes actors' duties and discretion linked to specific actions within contextual parameters. Necessary components: **Attributes**, **Aim**, **Context**. Sufficient (optional): **Deontic**, **Object**, **Or else**.

| Symbol | Component | Definition |
|--------|-----------|------------|
| `A` | **Attributes** | The actor (individual or corporate) that carries out, or is expected to/to not carry out, the action. May include descriptors (properties). **Necessary.** |
| `D` | **Deontic** | Prescriptive/permissive operator: to what extent is the action compelled, restrained, or discretionary? Common values: *must*, *shall*, *may*, *must not*, *may not*. **Optional.** |
| `I` | **Aim** | The goal or action assigned to the Attribute. **Necessary.** |
| `Bdir` | **Direct Object** | The inanimate or animate receiver of the Aim. Can be real-world or abstract. **Optional.** |
| `Bind` | **Indirect Object** | Object affected by the application of the Aim to the Direct Object. **Optional.** |
| `Cac` | **Activation Condition** (Context) | Precondition that activates the non-context part of the statement (discretized setting or event). **Necessary (may be implied as "under all conditions").** |
| `Cex` | **Execution Constraint** (Context) | Qualifier of the Aim: temporal, spatial, procedural, or other constraints on how the action is performed. **Necessary (may be implied as "no constraints").** |
| `O` | **Or else** | Sanctioning provision for non-compliance; expressed as a nested institutional statement. **Optional.** |

---

## Constitutive Statement Components

A **constitutive statement** parameterizes an institutional setting by introducing, modifying, or constituting features. Necessary: **Constituted Entity**, **Constitutive Function**, **Context**. Sufficient: **Modal**, **Constituting Properties**, **Or else**.

| Symbol | Component | Definition |
|--------|-----------|------------|
| `E` | **Constituted Entity** | The entity being constituted, reconstituted, modified, or directly affected. **Necessary.** |
| `M` | **Modal** | Operator signaling necessity or (im)possibility of constitution (epistemic, not deontic). Common values: *shall*, *is*, *must*, *may*. **Optional.** |
| `F` | **Constitutive Function** | Expression linking Constituted Entity to the institutional setting (defines, establishes, modifies, confers status). **Necessary.** |
| `P` | **Constituting Properties** | Properties that parameterize the Constituted Entity via the Constitutive Function. **Optional.** |
| `Cac` | **Activation Condition** | Same as regulative. **Necessary (may be implied).** |
| `Cex` | **Execution Constraint** | Same as regulative. **Necessary (may be implied).** |
| `O` | **Or else** | Consequence of non-fulfillment of the Constitutive Function; expressed as a nested statement. Consequences can be existential (invalidating policy). **Optional.** |

---

## Properties

Properties refine components using the `,p` suffix:

- `A,p(Certified) A(farmer)` — actor property "certified" + actor "farmer"
- `Bdir,p(written) Bdir(notification)` — object property "written" + object "notification"
- `E,p(Council) E(Chair)` — entity property

At **IG Extended**, multiple properties receive numeric indices: `A,p1(...)`, `A,p2(...)`.
Properties of properties (second-order): `A,p1,p1(...)`.

---

## Implied Components

When a component is absent from the text but can be inferred from context, wrap it in square brackets:

- `A([certifier])` — actor inferred from context
- `I([sends])` — action nominalized in the original text, reconstructed

---

## Object-Property Hierarchy (IG Extended)

When objects have nested descriptor relationships, use numeric indexing:

```
Bdir,p1,p1,p; Bdir,p1,p2,p(proposed)
Bdir,p1,p1(suspension) or Bdir,p1,p2(revocation)
of Bdir,p1(certification)
```

Where a property applies to multiple elements, separate references with semicolons:
`A1,p1; A2,p1` — property p1 applies to both A1 and A2.

---

## Named Entities Rule

Named entities (e.g., *United States Department of Agriculture*, *National Organic Standards Board*) are **never decomposed** into component properties. They are coded as full Attributes, Objects, Constituted Entities, or Constituting Properties.
