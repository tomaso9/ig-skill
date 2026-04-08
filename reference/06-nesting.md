# Nesting in Institutional Statements

Source: IG 2.0 Codebook v1.4, Sections 2.2, 2.2.2, 2.2.3

---

## Two Forms of Nesting

IG 2.0 recognizes two main nesting types:
- **Statement-level nesting**: Horizontal and vertical
- **Component-level nesting**: A component is substituted with an institutional statement

---

## Horizontal Nesting

**Definition**: Logical combination of two or more statements that capture co-occurring or alternative content (same component type occurring multiple times).

**Purpose**: Represents compound activities, multiple actors, or multiple objects within a single institutional arrangement.

**Syntax**: `{stmt1 [logicalOperator] stmt2}`

**Operators**: `[AND]` (both apply), `[OR]` (one or more), `[XOR]` (exactly one)

### Examples

Single AND combination:
```
{A(Organic farmers) D(must) I(commit to) Bdir(organic farming standards)}
[AND]
{A(Organic farmers) D(must) I(accommodate) Bdir(regular reviews of their practices)}
```

Complex with precedence:
```
({stmt1 [AND] stmt2}) [XOR] ({stmt3})
```

---

## Vertical Nesting

**Definition**: Consequential relationship between a **monitored statement** (the main rule) and a **consequential statement** (the or-else/sanction).

**Syntax**: `monitoredStatement{consequentialStatement}`

The Or else (`O`) is syntactically the vertical nesting connector.

### Examples

Simple vertical nesting:
```
A(Organic farmers) D(must) I(comply) Bdir(with organic farming regulations),
O{A(Certifiers) D(must) I(revoke) Bdir(the organic farming certification)}.
```

Multi-level vertical nesting:
```
(stmt1 [AND] stmt2),
OR ELSE (stmt3 [XOR] stmt4),
OR ELSE stmt5.
```

Combined horizontal + vertical:
```
({A(farmers) D(must) I(comply) Bdir(with regulations)}
 [AND]
 {A(farmers) D(must) I(accommodate) Bdir(regular review)}),
O {{A(Certifiers) D(must) I(suspend) Bdir(certification)}
   [XOR]
   {A(Certifiers) D(must) I(revoke) Bdir(certification)}},
O {A(USDA) D(may) I(revoke) Bdir(certifier's accreditation)}.
```

---

## Component-Level Nesting

**Definition**: An individual component of an institutional statement is replaced by another institutional statement (or statement of fact).

**When to use**: When a component (Attributes, Objects, Context conditions/constraints) is itself expressed as an action or institutional statement.

**Syntax**: Use `{ }` on the component instead of `( )`

**Applicable components**:
- Regulative: Attributes, Objects (Bdir/Bind), Context (Cac/Cex)
- Constitutive: Constituted Entity, Constituting Properties, Context

### Examples

**Activation Condition as nested statement:**
```
A(Official) D(must) I(impose) Bdir(fine) Cac{A(citizen) I(violates) Bdir(rule)}.
```

**Object as nested statement:**
```
A(Inspectors) D(must) I(ensure) Bdir{A(organic farmers) I(comply) Bdir(with organic farming regulations)}.
```

**Attribute property as nested statement (belief/assessment):**
```
A(Program managers) A,p1(who believe) A,p1,p1{that A(certified operation) I(has violated) Bdir(the Act)}
D(may) I(pursue) Bdir(revocation proceedings).
```

---

## Atomic vs. Non-Atomic Statements

An **atomic institutional statement** contains:
- All necessary components (no component-level combinations or nesting)
- Each component has exactly one value

A statement is **not atomic** if it contains:
- Multiple values for the same component (component-level combinations)
- Any component-level nesting

**Rule**: Always attempt to decompose compound statements into atomic statements linked by logical operators before encoding. This improves downstream analytical tractability.

---

## Nesting Decision Guide

```
Does the statement contain multiple regulated activities or actors?
└── YES → Horizontal nesting: decompose into {S1 [AND/OR/XOR] S2}

Does the statement contain a consequence clause ("or else", "otherwise")?
└── YES → Vertical nesting: S1 O{S2}

Does a component (actor, object, condition) itself read like an action or statement?
└── YES → Component-level nesting: replace ( ) with { } on that component
```
