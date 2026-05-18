# IG Logico: Semantic Annotation Decision Guide

Source: Frantz & Siddiki (2022), Chapter 6, pp. 201–219 (Table 6.2)

Required at **IG Logico** only. Apply annotations selectively to components where the distinction carries analytical value. Each annotation uses the format `ComponentName[taxonomy=value](content)`.

---

## Annotation Syntax

Single annotation:
```
A[anim=animate](Program Manager)
```

Multiple taxonomies (semicolons):
```
A[anim=animate; role=originator](Program Manager)
```

Multiple values within one taxonomy (commas):
```
Bdir[anim=inanimate; metatype=concrete](notification)
```

Statement-level annotation (precedes braces):
```
[regulativeStatement]{A(Official) D(must) I(impose) Bdir(fine).}
```

---

## 1. Animacy Taxonomy (`anim=`)

**Applies to:** A, A_prop, Bdir, Bdir_prop, Bind, Bind_prop, Cac, Cex, E, E_prop, P, P_prop

| Value | Definition | Decision Rule |
|-------|-----------|---------------|
| `animate` | Entity capable of intentional action: humans, organizations, or any entity to which agency is attributed by the institutional text | Ask: *Could this entity be held accountable for performing or failing to perform an action?* → YES → `animate` |
| `inanimate` | Objects, artifacts, documents, rules, abstract concepts, processes | Everything that is not animate |

**Edge cases:**
- Inanimate subjects of passive statements that are anthropomorphized by the text (e.g., *"A sailing vessel shall not impede…"*) → `animate` (the text attributes agency)
- Organizational entities (boards, departments, agencies) → `animate`
- Documents, permits, certifications, plans → `inanimate`

---

## 2. Metatype Taxonomy (`metatype=`)

**Applies to:** Same components as Animacy

| Value | Definition | Decision Rule |
|-------|-----------|---------------|
| `concrete` | Entity with physically observable presence OR institutional status observable through effect (actions, artifacts, violations as acts, certifications as status) | Ask: *Is this observable in the world or detectable through institutional action?* → YES → `concrete` |
| `abstract` | Purely mental or cognitive concept without directly observable institutional manifestation: beliefs, goals, suspicions, intentions | Ask: *Is this only accessible through an actor's subjective mental state?* → YES → `abstract` |

**Examples:**
- `notification` → `concrete` (physically sent, verifiable)
- `certification` → `concrete` (institutional status observable through effect)
- `violation` (as an act) → `concrete` (observable behavior)
- `belief that X is in violation` → `abstract` (mental state)
- `reason to believe` → `abstract`

---

## 3. Role Taxonomy (`role=`)

**Applies to:** A, A_prop, Bdir, Bdir_prop, Bind, Bind_prop, E, E_prop, P, P_prop

Captures the situational positioning of entities in the action situation.

### Role Characterizations

| Value | Definition | Typical component |
|-------|-----------|-------------------|
| `originator` | Entity from which the action originates; the agent performing the regulated activity | A (default for Attributes) |
| `recipient` | Entity receiving whatever is conferred, transmitted, or acted upon | Bdir, Bind (default for Objects) |
| `possessor` | Entity that owns or controls an object or another entity | Properties (e.g., *"farmer's certification"* → farmer is possessor) |

### Effect Characterizations

| Value | Definition |
|-------|-----------|
| `experiencer` | Indirectly affected actor — observes or is affected by, but does not directly receive, the activity |
| `advantaged` | Entity distinctively advantaged (beneficiary) by the referenced activity or function; may not be the direct recipient |
| `disadvantaged` | Entity distinctively burdened (maleficiary) by the referenced activity; may not be the direct recipient |

**Decision order:**
1. Is the entity performing the regulated action? → `originator`
2. Is the entity directly receiving the action or conferred status? → `recipient`
3. Is the entity an owner/controller of a referenced entity? → `possessor`
4. Is the entity indirectly observing or affected without direct receipt? → `experiencer`
5. Does the action distinctively benefit or burden this entity? → `advantaged` or `disadvantaged`

---

## 4. Regulative Functions Taxonomy (`regfunc=`)

**Applies to:** I (Aim) only

Annotates the institutional function of the regulated activity. Select the label that best captures the function within the action situation.

| Category | Value | Description | Example verbs |
|----------|-------|-------------|---------------|
| **Compliance action** | `comply` | Actor conforming to an institutional expectation | adhere, follow, conform, submit, report |
| | `violate` | Actor departing from an institutional expectation | refuse, fail to submit, operate non-compliantly |
| **Monitoring** | `detect compliance` | Detecting or verifying that an actor conforms | inspect, audit, verify, confirm, review |
| | `detect violation` | Detecting or verifying that an actor has violated | reveal noncompliance, identify violation, flag |
| **Enforcement** | `reward` | Positive incentive issued in response to compliance | certify, accredit, authorize, approve, grant |
| | `sanction` | Negative consequence issued in response to violation | suspend, revoke, fine, penalize, impose |
| **Enforcement response** | `accept` | Actor accepting the outcome of an enforcement action | comply with suspension, accept penalty |
| | `reject` | Actor challenging an enforcement outcome | contest, dispute, object to |
| | `appeal` | Formal challenge to an enforcement outcome (subset of reject) | appeal, request review, petition |

**Notes:**
- These categories are domain-adaptable. For studies focused on process modeling, lifecycle functions (`initiate`, `interrupt`, `resume`, `conclude`) may be appended.
- Apply the most specific label that fits; if multiple apply, use the primary institutional function in context.

---

## 5. Constitutive Functions Taxonomy (`constfunc=`)

**Applies to:** F (Constitutive Function) only

| Category | Value | Description | Example verbs/patterns |
|----------|-------|-------------|----------------------|
| **Entity definition** | `define` | Introduces or defines an entity in the institutional setting | means, is defined as, shall mean, refers to |
| **Relationship** | `relate` | Establishes a structural or functional relationship between entities | consists of, includes, is composed of, is embedded in |
| **Lifecycle** | `lifecycle` | Marks a change in an entity's lifecycle status | is established, is dissolved, takes effect, expires |
| **Status conferral** | `confer` | Assigns rights, authority, powers, privileges, or liabilities | has the right to, is authorized to, is eligible for, is liable for |
| **Meta-constitutive** | `purpose` | States the purpose or objective of the institution itself | is intended to, aims to, serves the purpose of |
| | `substitute` | Replaces or supersedes another provision | replaces, supersedes, amends, nullifies |
| | `amend` | Modifies an existing provision without replacing it | is amended to, is revised to, is supplemented by |

---

## 6. Vertical Nesting Annotations (`stype=`)

**Applies to:** Statement-level (precedes the statement or Or-else block)

| Value | Definition |
|-------|-----------|
| `stype=monitored` | Statement whose compliance is subject to oversight; the "leading" statement in a vertical nesting pair |
| `stype=consequential` | Statement specifying consequences for non-compliance; the "or-else" statement |
| `stype=monitoring` | Statement that performs the monitoring function (detects and signals potential violations) |

A single statement can carry multiple labels (e.g., a consequential statement that is itself monitored by another statement).

```
[stype=monitored]{A(farmer) D(must) I(submit) Bdir(plan) Cex[ctx=temporal](annually).}
O[stype=consequential]{A(certifier) D(may) I(revoke) Bdir(certification).}
```

---

## 7. Consequence Annotations (`consequence=`)

**Applies to:** O (Or-else) — annotates the type of consequence

| Value | Definition |
|-------|-----------|
| `consequence=social` | Social, economic, or status-affecting consequence on an actor or the institutional setting |
| `consequence=configurational` | Re-parameterizes the institutional setting itself (changes roles, rights, or rules) |

```
O[consequence=social]{A(certifier) D(must) I(revoke) Bdir(certification).}
O[consequence=configurational]{E(approved operation) M(shall) [NOT] F(be valid) P(for export).}
```

---

## Quick Reference: Component–Taxonomy Matrix

| Taxonomy | A | A_prop | D | I | Bdir | Bdir_prop | Bind | Bind_prop | Cac | Cex | E | E_prop | F | P | P_prop | O |
|----------|---|--------|---|---|------|-----------|------|-----------|-----|-----|---|--------|---|---|--------|---|
| `anim=`  | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | — |
| `metatype=` | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | — |
| `role=`  | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | — | ✓ | ✓ | — |
| `regfunc=` | — | — | — | ✓ | — | — | — | — | — | — | — | — | — | — | — | — |
| `constfunc=` | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — | — |
| `ctx=`   | — | — | — | — | — | — | — | — | ✓ | ✓ | — | — | — | — | — | — |
| `stype=` | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | ✓ |
| `consequence=` | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | ✓ |
