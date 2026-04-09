"""
Inter-agent reliability comparison for IG-coded CSVs.

Usage:
    python compare.py run1.csv run2.csv run3.csv run4.csv run5.csv
    python compare.py          # uses run1.csv through run5.csv in same directory
"""

import csv
import os
import sys
from itertools import combinations


COMPONENT_COLS = [
    "A", "A_prop", "D", "I",
    "Bdir", "Bdir_prop", "Bind", "Bind_prop",
    "Cac", "Cex", "O",
    "E", "E_prop", "M", "F", "P", "P_prop",
]
TYPE_COL = "type"


def load_csv(path):
    """Load a coded CSV into a dict keyed by statement ID."""
    rows = {}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows[row["id"]] = row
    return rows


def jaccard(a, b):
    """Token-level Jaccard similarity between two strings."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 1.0


def cohens_kappa(labels_a, labels_b):
    """Cohen's kappa for two equal-length sequences of categorical labels."""
    if not labels_a:
        return None
    n = len(labels_a)
    categories = list(set(labels_a) | set(labels_b))
    p_o = sum(a == b for a, b in zip(labels_a, labels_b)) / n
    p_e = sum(
        (labels_a.count(c) / n) * (labels_b.count(c) / n)
        for c in categories
    )
    if p_e >= 1.0:
        return 1.0
    return (p_o - p_e) / (1 - p_e)


def compare_pair(run_a, run_b, name_a, name_b):
    """Print a pairwise comparison report for two runs."""
    print(f"\n{'='*62}")
    print(f"  {name_a}  vs  {name_b}")
    print(f"{'='*62}")

    common_ids = sorted(set(run_a.keys()) & set(run_b.keys()))
    only_a = sorted(set(run_a.keys()) - set(run_b.keys()))
    only_b = sorted(set(run_b.keys()) - set(run_a.keys()))

    print(f"\n  Statements in {name_a}: {len(run_a)}")
    print(f"  Statements in {name_b}: {len(run_b)}")
    print(f"  Common IDs             : {len(common_ids)}")
    if only_a:
        print(f"  Only in {name_a}: {', '.join(only_a)}")
    if only_b:
        print(f"  Only in {name_b}: {', '.join(only_b)}")

    if not common_ids:
        print("  No common statements to compare.")
        return

    # --- Type classification ---
    types_a = [run_a[sid][TYPE_COL] for sid in common_ids]
    types_b = [run_b[sid][TYPE_COL] for sid in common_ids]
    type_agree = sum(a == b for a, b in zip(types_a, types_b)) / len(types_a)
    kappa = cohens_kappa(types_a, types_b)
    print(f"\n  Type classification (REG / CONST / HYB):")
    print(f"    Raw agreement : {type_agree:.1%}")
    print(f"    Cohen's kappa : {kappa:.3f}")

    # --- Per-component ---
    print(f"\n  Component-level agreement:")
    print(f"  {'Component':<12} {'Pres.agree':>11} {'kappa(p)':>10} {'Content Jac.':>13}")
    print(f"  {'-'*12} {'-'*11} {'-'*10} {'-'*13}")

    for col in COMPONENT_COLS:
        pres_a = [bool(run_a[sid].get(col, "").strip()) for sid in common_ids]
        pres_b = [bool(run_b[sid].get(col, "").strip()) for sid in common_ids]

        # Skip columns neither run uses
        if not any(pres_a) and not any(pres_b):
            continue

        pres_agree = sum(a == b for a, b in zip(pres_a, pres_b)) / len(pres_a)
        kp = cohens_kappa(
            ["Y" if p else "N" for p in pres_a],
            ["Y" if p else "N" for p in pres_b],
        )
        kp_str = f"{kp:.3f}" if kp is not None else "  N/A"

        # Content Jaccard where both filled
        sims = [
            jaccard(run_a[sid].get(col, ""), run_b[sid].get(col, ""))
            for sid in common_ids
            if run_a[sid].get(col, "").strip() and run_b[sid].get(col, "").strip()
        ]
        sim_str = f"{sum(sims)/len(sims):.3f}" if sims else "  N/A"

        print(f"  {col:<12} {pres_agree:>11.1%} {kp_str:>10} {sim_str:>13}")


def main(paths):
    runs = [load_csv(p) for p in paths]
    names = [os.path.basename(p) for p in paths]

    print("\nIG SKILL - INTER-AGENT CONSISTENCY REPORT")
    print(f"Comparing {len(runs)} runs: {', '.join(names)}")

    for (i, j) in combinations(range(len(runs)), 2):
        compare_pair(runs[i], runs[j], names[i], names[j])

    print("\n" + "="*62)
    print("Interpretation guide:")
    print("  kappa >= 0.80        -- strong consistency")
    print("  kappa 0.60-0.79      -- moderate; review disagreements")
    print("  kappa < 0.60         -- low; prompt needs refinement")
    print("  Content Jaccard >= 0.70      -- acceptable component-level agreement")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        paths = sys.argv[1:]
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        paths = [os.path.join(here, f"run{i}.csv") for i in range(1, 6)]
    main(paths)
