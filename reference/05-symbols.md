# IG Script Symbol Reference

Source: IG 2.0 Codebook v1.4, Section 4.1 (Table 6)

---

## Base Syntax

```
componentSymbol(encoded content)
```

For combined values:
```
componentSymbol(shared value (left value [logicalOperator] right value) shared value)
```

Example: `I(to (revise [AND] resubmit))`
Nested precedence: `I((revise [AND] resubmit) [OR] revoke)`

---

## Component Symbols

| Symbol | Applies To | Level | Description | Example |
|--------|-----------|-------|-------------|---------|
| `A` | Regulative | Core | Attributes (actor) | `A(Certifier)` |
| `D` | Regulative | Core | Deontic | `D(must)`, `D(may)`, `D(must not)` |
| `I` | Regulative | Core | Aim (action) | `I(submit)`, `I(monitor)` |
| `Bdir` | Regulative | Core | Direct Object | `Bdir(certification)` |
| `Bind` | Regulative | Core | Indirect Object | `Bind(organic farmer)` |
| `Cac` | Both | Core | Activation Condition | `Cac(Upon accreditation)` |
| `Cex` | Both | Core | Execution Constraint | `Cex(at any time)` |
| `O` | Both | Core | Or else (nested stmt) | `O{A(official) D(may) I(sanction)...}` |
| `E` | Constitutive | Core | Constituted Entity | `E(Council)` |
| `M` | Constitutive | Core | Modal | `M(shall)`, `M(is)` |
| `F` | Constitutive | Core | Constitutive Function | `F(consists of)`, `F(means)` |
| `P` | Constitutive | Core | Constituting Properties | `P(organic farming representatives)` |

---

## Property Suffix

| Syntax | Level | Description | Example |
|--------|-------|-------------|---------|
| `,p` | Core | Single property of a component | `A,p(Certified) A(farmer)` |
| `,p1`, `,p2` | Extended | Multiple properties (indexed) | `Bdir,p1(written) Bdir(notification)` |
| `,p1,p1` | Extended | Second-order property | `A,p1,p1(...)` |
| `;` separator | Extended | Property applies to multiple elements | `A1,p1; A2,p1(...)` |

---

## Brackets & Braces

| Symbol | Context | Description | Example |
|--------|---------|-------------|---------|
| `( )` | Component | Component classification (wraps content) | `A(Certifier)` |
| `[ ]` | Component | Implied/inferred component | `A([certifier])`, `I([sends])` |
| `[ ]` | Component | Semantic annotation (IG Extended/Logico) | `A[type=animate](Official)` |
| `{ }` | Statement | Horizontal nesting scope | `{stmt1 [AND] stmt2}` |
| `{ }` | Statement | Vertical nesting (Or else / consequence) | `O{A(official) D(may) I(sanction)...}` |
| `{ }` | Component | Component-level nesting | `Cac{A(citizen) I(violates) Bdir(rule)}` |

---

## Logical Operators

| Operator | Meaning | Use |
|----------|---------|-----|
| `[AND]` | Conjunction | Both/all apply | `I(review [AND] assess)` |
| `[OR]` | Inclusive disjunction (AND/OR) | One or more apply | `I(review [OR] assess)` |
| `[XOR]` | Exclusive disjunction (EITHER/OR) | Exactly one applies | `I(approve [XOR] reject)` |
| `[NOT]` | Negation | Inverts component or statement | `D(must [NOT])`, `{stmt [NOT]}` |

Precedence via inner parentheses:
```
I(firstAction [AND] (secondAction [OR] thirdAction))
```

---

## Statement-Level Annotation (IG Logico)

Precedes the statement scope:
```
[regulativeStatement]{A(Official) D(must) I(impose) Bdir(fine).}
[constitutiveStatement]{E(Board) M(shall) F(consist of) P(seven members).}
```

---

## Nesting Patterns

### Vertical Nesting (Or else)
```
stmt1{stmt2}
```
Example:
```
A(citizen) D(must) I(conform) Bdir(with policy)
O{A(official) D(may) I(sanction) Bdir(citizen) Cex(immediately)}.
```

### Horizontal Nesting (AND/OR/XOR combinations)
```
{stmt1 [AND] stmt2}
```

### Component-Level Nesting
```
A(Official) D(must) I(impose) Bdir(fine) Cac{A(citizen) I(violates) Bdir(rule)}.
```

### Multi-Level Vertical Nesting
```
(stmt1 [AND] stmt2),
OR ELSE (stmt3 [XOR] stmt4),
OR ELSE stmt5.
```

---

## Semantic Annotation Key-Value Format (IG Logico)

```
componentSymbol[taxonomy=value; taxonomy=value](content)
```

| Taxonomy Prefix | Taxonomy | Example Values |
|----------------|----------|----------------|
| `anim` | Animacy | `animate`, `inanimate` |
| `metatype` | Metatype | `abstract`, `concrete` |
| `role` | Role | `originator`, `recipient`, `possessor`, `experiencer`, `beneficiary` |
| `regfunc` | Regulative Function | `sanction`, `comply`, `monitor`, `report`, `authorize`, `detect violation` |
| `constfunc` | Constitutive Function | `define`, `establish`, `confer`, `modify`, `qualify`, `scope` |
| `ref` | Reference | `"policy"`, `"section"` |
| `stringency` | Prescriptiveness | `prescription`, `permission`, `prohibition` |

Multiple values within a taxonomy: separate with comma.
Multiple taxonomies: separate with semicolon.

```
A[anim=animate; role=originator; metatype=concrete](Program Manager)
```
