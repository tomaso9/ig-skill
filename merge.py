"""
Multi-agent IG coding merge and flag script.

Compares three independently coded CSVs field by field. Any field where
the three values are not all identical is flagged for human review.
Consensus value: majority vote (2-vs-1), or run1 fallback when all differ.

Usage:
    python merge.py agent1.csv agent2.csv agent3.csv consensus.csv review.csv
"""

import csv
import re
import sys
from collections import Counter


def _id_sort_key(sid):
    """Natural sort key for statement IDs like S1, S2, S10, S10a.
    Splits into (prefix, number, suffix) so S2 < S10 < S10a."""
    m = re.match(r'^([A-Za-z]*)(\d+)(.*)$', sid)
    if m:
        return (m.group(1), int(m.group(2)), m.group(3))
    return (sid, 0, '')


FIELDNAMES = [
    "id", "type", "coding_level", "original_text",
    "A", "A_prop", "D", "I",
    "Bdir", "Bdir_prop", "Bind", "Bind_prop",
    "Cac", "Cex", "O",
    "E", "E_prop", "M", "F", "P", "P_prop",
    "ig_script_full", "notes",
]

COMPARE_FIELDS = [
    "type",
    "A", "A_prop", "D", "I",
    "Bdir", "Bdir_prop", "Bind", "Bind_prop",
    "Cac", "Cex", "O",
    "E", "E_prop", "M", "F", "P", "P_prop",
]

PASSTHROUGH_FIELDS = [f for f in FIELDNAMES if f not in COMPARE_FIELDS and f != "id"]


def load_csv(path):
    """Load a coded CSV into a dict keyed by statement ID."""
    rows = {}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows[row["id"]] = row
    return rows


def _majority_or_first(values):
    """Return majority value (count > 1), or values[0] if no majority."""
    counts = Counter(values)
    top_value, top_count = counts.most_common(1)[0]
    return top_value if top_count > 1 else values[0]


def merge_three(paths, consensus_path, review_path):
    """
    Merge three agent CSVs into consensus and review outputs.

    consensus_path: standard IG columns + review_flag + disagreement_fields
    review_path:    one row per (statement, field) pair that disagreed
    """
    runs = [load_csv(p) for p in paths]
    all_ids = sorted(set().union(*[r.keys() for r in runs]), key=_id_sort_key)

    consensus_rows = []
    review_rows = []

    for sid in all_ids:
        run_rows = [r.get(sid, {}) for r in runs]
        present = sum(1 for r in runs if sid in r)
        if present < 2:
            print(f"WARNING: statement {sid!r} found in only {present} run(s); skipping.", file=sys.stderr)
            continue
        consensus_row = {"id": sid}

        # Passthrough fields: use first non-empty value across runs
        for field in PASSTHROUGH_FIELDS:
            for rr in run_rows:
                val = rr.get(field, "").strip()
                if val:
                    consensus_row[field] = val
                    break
            else:
                consensus_row[field] = ""

        # Compare fields: flag any disagreement
        disagreeing_fields = []
        for field in COMPARE_FIELDS:
            values = [rr.get(field, "").strip() for rr in run_rows]
            if len(set(values)) == 1:
                consensus_row[field] = values[0]
            else:
                disagreeing_fields.append(field)
                chosen = _majority_or_first(values)
                consensus_row[field] = chosen
                review_rows.append({
                    "id": sid,
                    "field": field,
                    "run1_value": values[0],
                    "run2_value": values[1],
                    "run3_value": values[2],
                    "consensus_used": chosen,
                })

        consensus_row["review_flag"] = "TRUE" if disagreeing_fields else "FALSE"
        consensus_row["disagreement_fields"] = ", ".join(disagreeing_fields)
        consensus_rows.append(consensus_row)

    # Write consensus CSV
    consensus_fieldnames = FIELDNAMES + ["review_flag", "disagreement_fields"]
    with open(consensus_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=consensus_fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(consensus_rows)

    # Write review CSV
    review_fieldnames = ["id", "field", "run1_value", "run2_value", "run3_value", "consensus_used"]
    with open(review_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=review_fieldnames)
        writer.writeheader()
        writer.writerows(review_rows)

    flagged = sum(1 for r in consensus_rows if r["review_flag"] == "TRUE")
    print(f"Consensus: {consensus_path} ({len(consensus_rows)} statements, {flagged} flagged)")
    print(f"Review:    {review_path} ({len(review_rows)} disagreements)")
    return consensus_rows, review_rows


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python merge.py agent1.csv agent2.csv agent3.csv consensus.csv review.csv")
        sys.exit(1)
    merge_three(sys.argv[1:4], sys.argv[4], sys.argv[5])
