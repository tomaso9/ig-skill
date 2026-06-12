"""
CSV writer for the ig-code skill.

Reads rows from a JSON file (a list of objects) and writes a CSV sorted in
natural statement-ID order (S2 < S10 < S10a). For coded output, every row is
stamped with the skill version from the VERSION file next to this script.

Usage:
    python write_rows.py <rows.json> <output.csv> --format coded
    python write_rows.py <rows.json> <output.csv> --format statements

Formats:
    statements  columns: id, type, original_text  (the statement list)
    coded       the full 23 IG component columns + skill_version
"""

import argparse
import csv
import json
import os
import re
import sys

CODED_FIELDS = [
    "id", "type", "coding_level", "original_text",
    "A", "A_prop", "D", "I",
    "Bdir", "Bdir_prop", "Bind", "Bind_prop",
    "Cac", "Cex", "O",
    "E", "E_prop", "M", "F", "P", "P_prop",
    "ig_script_full", "notes",
]

STATEMENT_FIELDS = ["id", "type", "original_text"]


def _id_sort_key(row):
    m = re.match(r'^([A-Za-z]*)(\d+)(.*)$', row["id"])
    return (m.group(1), int(m.group(2)), m.group(3)) if m else (row["id"], 0, "")


def read_version():
    version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")
    try:
        with open(version_file, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return "unknown"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rows_json", help="JSON file containing a list of row objects")
    parser.add_argument("output_csv", help="output CSV path")
    parser.add_argument("--format", choices=["coded", "statements"], required=True)
    args = parser.parse_args()

    with open(args.rows_json, encoding="utf-8") as f:
        rows = json.load(f)
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        print("ERROR: rows JSON must be a list of objects", file=sys.stderr)
        sys.exit(1)
    missing_id = [i for i, r in enumerate(rows) if not str(r.get("id", "")).strip()]
    if missing_id:
        print(f"ERROR: rows at indices {missing_id} have no 'id'", file=sys.stderr)
        sys.exit(1)

    if args.format == "statements":
        fieldnames = list(STATEMENT_FIELDS)
    else:
        fieldnames = CODED_FIELDS + ["skill_version"]
        version = read_version()
        for r in rows:
            r["skill_version"] = version

    known = set(fieldnames)
    extra_keys = sorted({k for r in rows for k in r} - known)
    if extra_keys:
        print(f"WARNING: ignoring unexpected keys: {', '.join(extra_keys)}", file=sys.stderr)
    for r in rows:
        for f_ in fieldnames:
            r.setdefault(f_, "")

    rows = sorted(rows, key=_id_sort_key)
    with open(args.output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Written: {args.output_csv} ({len(rows)} rows, format={args.format})")


if __name__ == "__main__":
    main()
