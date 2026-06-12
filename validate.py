"""
Validation gate for ig-code coded outputs.

Checks a coded CSV (one agent run, or the single-agent output) against the
authoritative statement list and IG 2.0 structural rules. Run this on every
coded CSV before merging or delivering results.

Usage:
    python validate.py <coded.csv> <statement_list.csv> --level "IG Core" [--strict]

Exit codes:
    0   no errors (warnings allowed unless --strict)
    1   errors found, or warnings found with --strict

ERROR checks (structural -- must be fixed before merge/delivery):
    E1   required columns missing from the coded CSV
    E2   duplicate statement IDs
    E3   ID set differs from the statement list (missing or extra statements)
    E4   `type` differs from the pre-assigned type in the statement list
    E5   `type` not one of REG / CONST / NON-IS
    E6   NON-IS row has non-empty component fields
    E7   REG row missing Aim (I), or CONST row missing E or F, without a
         "manual coding" note
    E8   unbalanced ( ) or { } in ig_script_full
    E9   at IG Extended / IG Logico: non-empty Cac or Cex without a [ctx=...]
         annotation in ig_script_full
    E10  forbidden invented bracket label (e.g. [actor], [any person or entity]);
         only verbatim text or [any person] is allowed inside [ ]

WARNING checks (reported; gate only with --strict):
    W1   component value not found verbatim in original_text (after removing
         [ ]-reconstructions, logical operators, and ` | ` joins)
    W2   ctx= value outside the codebook context taxonomy
    W3   regfunc= / confunc= value outside the codebook taxonomy (the codebook
         marks these taxonomies as non-exhaustive, hence warning not error)
    W4   deprecated `constfunc=` prefix used (codebook prefix is `confunc`)
"""

import argparse
import csv
import re
import sys
from collections import Counter

COMPONENT_FIELDS = [
    "A", "A_prop", "D", "I",
    "Bdir", "Bdir_prop", "Bind", "Bind_prop",
    "Cac", "Cex", "O",
    "E", "E_prop", "M", "F", "P", "P_prop",
]

REQUIRED_FIELDS = ["id", "type", "coding_level", "original_text"] + COMPONENT_FIELDS + [
    "ig_script_full", "notes",
]

VALID_TYPES = {"REG", "CONST", "NON-IS"}

# Codebook v1.4 closed/known vocabularies
CTX_VALUES = {"temporal", "spatial", "domain", "procedural", "method",
              "purpose", "effect", "state", "event"}
REGFUNC_VALUES = {"comply", "violate", "detect compliance", "detect violation",
                  "reward", "sanction", "accept", "reject", "appeal"}
CONFUNC_VALUES = {"definition", "functional", "composition", "organization",
                  "lifecycle", "conferral", "relationship", "intent", "information"}

# Invented generic actor labels that are never allowed inside [ ]
FORBIDDEN_BRACKET_LABELS = {
    "actor", "the actor", "the agency", "responsible party",
    "any person or entity", "person or entity", "person/user",
    "regulated entity", "actor inferred from context", "person", "entity",
}
ALLOWED_GENERIC_LABEL = "any person"

_BRACKET_RE = re.compile(r"\[([^\[\]]+)\]")
_OPERATOR_RE = re.compile(r"\[(?:AND|OR|XOR|NOT)\]", re.IGNORECASE)
_ANNOTATION_RE = re.compile(r"^\s*\w+\s*=")


def load_rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _norm_text(s):
    return re.sub(r"\s+", " ", s).strip().casefold()


def _balanced(text, open_ch, close_ch):
    depth = 0
    for ch in text:
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def _bracket_contents(value):
    """Bracket contents that are reconstructions, not annotations or operators."""
    out = []
    for m in _BRACKET_RE.finditer(value):
        content = m.group(1)
        if _OPERATOR_RE.fullmatch(f"[{content}]"):
            continue
        if _ANNOTATION_RE.match(content):
            continue
        out.append(content)
    return out


def _verbatim_chunks(value):
    """Chunks of a component value that should appear verbatim in original_text."""
    chunks = []
    for part in value.split("|"):
        part = _BRACKET_RE.sub(" ", part)          # drop reconstructions/annotations
        part = re.sub(r"[(){}]", " ", part)        # drop grouping syntax
        part = _norm_text(part)
        if len(part) >= 3:
            chunks.append(part)
    return chunks


def validate(coded_path, statement_list_path, level, strict=False):
    errors, warnings = [], []
    rows = load_rows(coded_path)
    ref_rows = load_rows(statement_list_path)
    ref_types = {r["id"]: r["type"] for r in ref_rows}

    # E1 — required columns
    header = set(rows[0].keys()) if rows else set()
    missing_cols = [c for c in REQUIRED_FIELDS if c not in header]
    if missing_cols:
        errors.append(f"E1 header: missing columns: {', '.join(missing_cols)}")
        _report(errors, warnings, strict)
        return errors, warnings

    # E2 — duplicate IDs
    id_counts = Counter(r["id"] for r in rows)
    for sid, n in sorted(id_counts.items()):
        if n > 1:
            errors.append(f"E2 {sid}: appears {n} times")

    # E3 — ID set match
    coded_ids, ref_ids = set(id_counts), set(ref_types)
    for sid in sorted(ref_ids - coded_ids):
        errors.append(f"E3 {sid}: in statement list but missing from coded CSV")
    for sid in sorted(coded_ids - ref_ids):
        errors.append(f"E3 {sid}: in coded CSV but not in statement list")

    extended = level in ("IG Extended", "IG Logico")

    for row in rows:
        sid = row["id"]
        rtype = row.get("type", "").strip()
        script = row.get("ig_script_full", "")
        notes = row.get("notes", "").casefold()
        original = _norm_text(row.get("original_text", ""))

        # E4 — type unchanged
        if sid in ref_types and rtype != ref_types[sid]:
            errors.append(f"E4 {sid}: type changed from {ref_types[sid]!r} to {rtype!r}")

        # E5 — valid type
        if rtype not in VALID_TYPES:
            errors.append(f"E5 {sid}: invalid type {rtype!r}")
            continue

        # E6 — NON-IS rows must be empty
        if rtype == "NON-IS":
            filled = [f for f in COMPONENT_FIELDS + ["ig_script_full"] if row.get(f, "").strip()]
            if filled:
                errors.append(f"E6 {sid}: NON-IS row has non-empty fields: {', '.join(filled)}")
            continue

        # E7 — necessary components present (or noted)
        noted = "manual coding" in notes
        if rtype == "REG" and not row.get("I", "").strip() and not noted:
            errors.append(f"E7 {sid}: REG row has empty Aim (I) and no 'manual coding' note")
        if rtype == "CONST":
            for f_ in ("E", "F"):
                if not row.get(f_, "").strip() and not noted:
                    errors.append(f"E7 {sid}: CONST row has empty {f_} and no 'manual coding' note")

        # E8 — balanced brackets in ig_script_full
        if script:
            if not _balanced(script, "(", ")"):
                errors.append(f"E8 {sid}: unbalanced ( ) in ig_script_full")
            if not _balanced(script, "{", "}"):
                errors.append(f"E8 {sid}: unbalanced {{ }} in ig_script_full")

        # E9 — ctx annotation required at Extended/Logico
        if extended:
            for comp in ("Cac", "Cex"):
                if row.get(comp, "").strip():
                    pattern = re.compile(re.escape(comp) + r"(?:,p[\d,p]*)?\[[^\]]*ctx\s*=")
                    if not pattern.search(script):
                        errors.append(
                            f"E9 {sid}: non-empty {comp} without [ctx=...] annotation in ig_script_full"
                        )

        # E10 + W1 — bracket labels and verbatim extraction
        for f_ in COMPONENT_FIELDS:
            value = row.get(f_, "")
            if not value.strip():
                continue
            for content in _bracket_contents(value):
                norm = _norm_text(content)
                if norm == ALLOWED_GENERIC_LABEL:
                    continue
                if norm in FORBIDDEN_BRACKET_LABELS:
                    errors.append(f"E10 {sid} {f_}: forbidden bracket label [{content}]")
            for chunk in _verbatim_chunks(value):
                if chunk not in original:
                    warnings.append(
                        f"W1 {sid} {f_}: value not verbatim in original_text: {chunk!r}"
                    )

        # W2/W3/W4 — taxonomy values in ig_script_full annotations
        for m in _BRACKET_RE.finditer(script):
            for part in m.group(1).split(";"):
                kv = part.split("=", 1)
                if len(kv) != 2:
                    continue
                key, raw_vals = kv[0].strip().casefold(), kv[1]
                values = [v.strip().casefold() for v in raw_vals.split(",")]
                if key == "ctx":
                    for v in values:
                        if v not in CTX_VALUES:
                            warnings.append(f"W2 {sid}: unknown ctx value {v!r}")
                elif key == "regfunc":
                    for v in values:
                        if v not in REGFUNC_VALUES:
                            warnings.append(f"W3 {sid}: unknown regfunc value {v!r}")
                elif key == "confunc":
                    for v in values:
                        if v not in CONFUNC_VALUES:
                            warnings.append(f"W3 {sid}: unknown confunc value {v!r}")
                elif key == "constfunc":
                    warnings.append(f"W4 {sid}: deprecated prefix 'constfunc=' (use 'confunc=')")

    _report(errors, warnings, strict)
    return errors, warnings


def _report(errors, warnings, strict):
    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"WARNING {w}")
    print(f"\nValidation: {len(errors)} error(s), {len(warnings)} warning(s)")


def main():
    parser = argparse.ArgumentParser(description="Validate an ig-code coded CSV")
    parser.add_argument("coded_csv")
    parser.add_argument("statement_list_csv")
    parser.add_argument("--level", required=True,
                        choices=["IG Core", "IG Extended", "IG Logico"])
    parser.add_argument("--strict", action="store_true",
                        help="treat warnings as failures")
    args = parser.parse_args()

    errors, warnings = validate(args.coded_csv, args.statement_list_csv,
                                args.level, strict=args.strict)
    if errors or (args.strict and warnings):
        sys.exit(1)


if __name__ == "__main__":
    main()
