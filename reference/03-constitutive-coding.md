# Constitutive Statement Coding Guidelines

Source: IG 2.0 Codebook v1.4, Section 4.3

---

## What Makes a Statement Constitutive?

A **constitutive statement** parameterizes an institutional setting — it introduces, modifies, defines, or otherwise constitutes features of an institutional system (actors, roles, objects, affordances, processes, environmental characteristics).

Key signals:
- Defines or introduces an entity or role (*"X is defined as..."*, *"X shall mean..."*, *"X consists of..."*)
- Confers rights, authority, or status on an entity
- Establishes or modifies rules about the institutional setting itself
- Consequence of violation is **existential** (invalidates policy, dissolves entity) rather than a behavioral sanction

---

## IG Core — Constitutive Statements

### Syntactic Structure

```
[Cac(...)] E(...) M(...) F(...) [P(...)] [Cex(...)] [O{...}]
```

Necessary: **E** (Constituted Entity), **F** (Constitutive Function), **Context** (Cac/Cex, may be implied).
Optional: **M** (Modal), **P** (Constituting Properties), **O** (Or else).

### Component Guidelines

#### Constituted Entity (E)
- The entity being defined, established, modified, or conferred status upon
- Can be an actor, role, object, artifact, or the policy itself
- Properties encoded with `,p` suffix: `E,p(Council) E(Chair)`
- **Source constraint:** Use the entity name exactly as it appears in the source text. Do not substitute, generalize, or infer the entity from surrounding sections. If the entity is implied but not named, leave `E` empty and add note: *"constituted entity absent from text — manual coding required"*

#### Modal (M)
- Signals epistemic necessity or possibility of the constitution (not behavioral duty)
- Distinguish from Deontic (D): *Deontic = behavioral obligation; Modal = existential necessity*
- Common values: *shall*, *is*, *must*, *may* (context determines whether deontic or modal)

**Heuristic:** Ask: *"Does this operator assign a duty to an actor, or signal that something is required to exist/be the case?"*
- "Access to mediation **shall** be maintained" → Modal (existential requirement, actor implied)
- "The certifier **shall** maintain access" → Deontic (actor's duty)

#### Constitutive Function (F)
- The expression linking Constituted Entity to the institutional setting
- Common verbs: *is defined as*, *means*, *consists of*, *includes*, *is established as*, *shall be*, *has the right to*, *is authorized to*

#### Constituting Properties (P)
- Properties that parameterize the Constituted Entity via the Constitutive Function
- Can be physical or abstract; animate or inanimate

#### Context (Cac / Cex)

Cac and Cex apply to constitutive statements with the same force as to regulative statements. Do not skip these components simply because the statement is definitional or constitutive.

**Activation Condition (Cac)** — a precondition that activates when or for whom the constitution takes effect:
- Temporal triggers: *"Starting January 1..."*, *"As of the effective date..."*, *"Upon adoption..."*, *"After the election of..."*
- Event triggers: *"In the event that the position becomes vacant..."*, *"Once the application is submitted..."*
- Conditional qualifiers: *"Where applicable..."*, *"In cases where..."*, *"When the Council is constituted..."*

**Execution Constraint (Cex)** — a clause qualifying how, in what procedural manner, or under what restrictions the constitution operates, without changing when it applies:
- Procedural qualifiers: *"pursuant to..."*, *"in accordance with [Section X]..."*, *"as defined in..."*
- Scope limiters: *"to the extent allowed by law"*, *"within the meaning of this Part"*, *"subject to approval by..."*
- Functional purpose clauses: *"to [perform some function]"*, *"for the purpose of..."* (when clearly a constraint on how properties are exercised, not the properties themselves)

**Decision rule — P vs. Cex:** Ask: *"Does this clause define what the entity IS (content of constitution) or HOW/UNDER WHAT CONDITIONS the entity operates?"* The former belongs in P; the latter is Cex.

**When Cac/Cex is genuinely absent:** Pure definitional statements (*"X means Y"*) without temporal, conditional, or procedural qualifiers have no Cac/Cex. Leave both fields empty — do not infer a universal condition.

**Signal to check:** Any adverbial clause, dependent clause, or prepositional phrase that is not core to P should be evaluated as Cac or Cex before leaving the fields empty. Apply the decision guide in [04-heuristics.md](04-heuristics.md#activation-condition-vs-execution-constraint-decision-guide).

#### Or else (O)
- Consequence of non-fulfillment; can be **existential** (e.g., invalidation)
- `O{E(certification) M(shall) [NOT] F(be valid)}` — existential consequence

---

### IG Core Constitutive Examples

**Definitions:**
*"'Secretary' means the Secretary of Agriculture."*
```
E(Secretary) F(means) P(the Secretary of Agriculture).
```

**Role establishment:**
*"Starting January 1, the Department of Agriculture is the certifying authority."*
```
Cac(Starting January 1), E(Department of Agriculture) F(is) P(the certifying authority).
```

**Membership composition:**
*"From 1st January onwards, the Council shall include organic farming representatives to review chemical allowances within organic food production standards."*
```
Cac(From 1st January onwards), E(Council) M(shall) F(include)
P(organic farming representatives) Cex(to review chemical allowances within organic food production standards).
```

**Rights conferral:**
*"Members of the Council shall have the right to hold any public office or employment."*
```
E(Members) of the E,p(Council) M(shall) F(have the right) P(to hold any public office or employment).
```

---

## IG Extended — Constitutive Statements

Adds:
1. **Property Hierarchy Decomposition** for Constituted Entity and Constituting Properties
2. **Component-level Nesting**: Constituted Entity, Constituting Properties, or Context may embed institutional statements
3. **Richer Context Categorization** using Context Taxonomy

### Component-Level Nesting in Constitutive Statements

```
Cac(In the event that the Board Chair position becomes vacant),
E(Vice-Chair) F(is) P(the chief executive of the Council).
```

Here the activation condition could itself be expressed as a nested institutional statement.

---

## IG Logico — Constitutive Statements

Adds semantic annotations using Constitutive Functions taxonomy.

### Constitutive Functions (constfunc annotation)

Annotate the Constitutive Function (F) component:
- `define` — definitional statements
- `establish` — creation of entities or positions
- `confer` — conferral of rights, authority, status
- `modify` — modification of existing entities
- `qualify` — eligibility or boundary criteria
- `scope` — outcomes or scope of an action situation

```
E(Secretary) F[constfunc=define](means) P(the Secretary of Agriculture).
```

```
Cac(From January 1st onward), E(National Organic Standards Advisory Council)
M[stringency=necessity](shall) F[constfunc=establish](be)
P(within the Department of Agriculture).
```

---

## Second-Order Constitutive Statements

Constitutive statements can nest within component-level properties of other constitutive statements:

*"Livestock producers must maintain health care practices that include feed rations as defined by the organic standards."*

Here "feed rations" is a constituting property that is itself defined by a nested constitutive statement:

```
A(Livestock producers) D(must) I(maintain) Bdir,p(health care)
Bdir(practices) Bdir,p1{E(feed rations) M(are) F(defined) P(by the organic standards)}.
```

---

## Distinguishing Constitutive from Regulative

Use this checklist (see also [04-heuristics.md](04-heuristics.md)):

| Question | → Constitutive if YES | → Regulative if YES |
|----------|-----------------------|---------------------|
| Does the statement introduce/define/modify an entity? | ✓ | |
| Does the statement regulate actor behavior (duty/discretion/prohibition)? | | ✓ |
| Is the consequence existential (invalidation)? | ✓ | |
| Is the consequence localized (sanction on an actor)? | | ✓ |
| Does the modal signal epistemic necessity ("it is required that X exists")? | ✓ | |
| Does the modal signal duty ("actor must do X")? | | ✓ |
| Does the statement confer rights, authority, or status? | ✓ | |
