# Problem Statement: Column Matcher

Column Matcher is the problem of determining whether an observed column in a changing tabular dataset semantically corresponds to a known canonical column, while preserving uncertainty, ambiguity, conflict, and the possibility of unknown or newly emerging concepts.

It is a column-level schema matching problem under schema drift.

## Context

Tabular data sources evolve over time. A column that represented a business concept in one dataset version may later appear with a different name, type, format, or context.

Example:

```text
2020-2023: nome
2024+:     nome_aluno
```

Both columns may represent the same canonical concept:

```text
student_name
```

This is a schema drift problem: upstream table metadata changes over time, while downstream analysis expects stable structure. In practice, this creates brittle pipelines when analytical code depends directly on source column names.

## Problem

The core problem is:

> Given an observed column in a changing table, determine whether it semantically corresponds to a known canonical column.

This is not a column-renaming problem. Renaming is only a downstream consequence. The actual problem is identifying semantic correspondence between an observed column and a canonical concept.

This belongs to the broader family of schema matching problems: finding correspondences between elements of different schemas.

## Formal Definition

Given a set of observed columns:

$C = \{c_1, c_2, \ldots, c_n\}$

and a set of canonical columns:

$S = \{s_1, s_2, \ldots, s_m\}$


determine a partial correspondence:

$R \subseteq C \times S$

where each pair:

$(c_i, s_j)$

means that observed column `ci` represents canonical column `sj`.

Some observed columns may have no valid correspondence.

## Core Question

For each observed column:

```text
What canonical concept, if any, does this column represent?
```

Possible outcomes:

```text
MATCH        the column corresponds to a known canonical column
UNKNOWN      no reliable correspondence is available
IGNORE       the column is known but outside the analytical schema
NEW_CONCEPT  the column appears meaningful but has no canonical equivalent yet
AMBIGUOUS    multiple canonical columns are plausible
CONFLICTING  the correspondence conflicts with other columns or schema expectations
```

## Why This Is Hard

Column names alone are not reliable.

Examples:

```text
nome       may mean student_name, school_name, guardian_name, or municipality_name
codigo     may mean student_id, school_id, municipality_code, or class_code
data       may mean birth_date, enrollment_date, reference_date, or update_date
municipio  may mean municipality_name, municipality_code, residence_municipality, or school_municipality
```

The same name can mean different things in different contexts. Different names can refer to the same concept. A column can also keep the same name while its meaning changes.

Therefore, the problem is semantic, contextual, and temporal — not merely lexical.

## Scope

This problem concerns column-level interpretation under schema drift.

Initial scope:

```text
one observed column → zero or one canonical column
```

Out of scope:

```text
row-level entity resolution
record deduplication
data cleaning
value normalization
missing-value imputation
business metric computation
complex N:M transformations
automatic ontology discovery
```

Examples of out-of-scope transformations:

```text
first_name + last_name → full_name
address → street + number + neighborhood
gender_code → normalized_gender
```

These may be future downstream tasks, but they are not the core problem.

## Required Problem Output

For each observed column, the problem output must preserve uncertainty.

A valid output identifies:

```text
source column
candidate canonical concept, if any
correspondence status
uncertainty level
ambiguity or conflict, when present
```

The problem is not solved by forcing every source column into the nearest canonical column.

## Main Failure Modes

```text
false match
  an observed column is assigned to the wrong canonical column

false non-match
  a valid correspondence exists but is missed

ambiguous match
  multiple canonical columns are plausible

silent drift
  the column name remains stable, but its meaning changes

schema gap
  a valid new concept appears but is absent from the canonical schema

conflict
  multiple observed columns appear to correspond to the same canonical column

missing required concept
  a required canonical concept is absent from the observed table
```

The most dangerous failure mode is a false confident match.

## Success Criteria

The problem is well handled when:

```text
canonical correspondences are identified correctly
ambiguous cases remain explicit
unknown columns are not forced into wrong matches
schema drift is detected as semantic change, not only name change
the same concept remains stable across dataset versions
the result is reviewable and auditable
```

---

[1]: https://vldb.org/pvldb/vol4/p695-bernstein_madhavan_rahm.pdf "Generic Schema Matching, Ten Years Later"
