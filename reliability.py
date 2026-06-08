"""
Inter-coder reliability for multi-agent IG coding.

Computes per-field percent agreement and Krippendorff's Alpha (nominal)
from three independently coded agent CSVs.

Usage:
    python reliability.py agent1.csv agent2.csv agent3.csv reliability.csv

Output columns:
    field                 -- IG component name, or OVERALL (pooled across all fields)
    n_statements          -- statements where all 3 agents produced a value
    n_full_agreement      -- of those, statements where all 3 values match
    pct_agreement         -- n_full_agreement / n_statements * 100
    krippendorffs_alpha   -- nominal Krippendorff's Alpha; "N/A" if not computable

Notes:
    - Empty string ("") means a component is absent from a statement and is treated
      as the category ABSENT — two agents that both leave a field empty have agreed.
    - None means the agent did not code the statement at all (excluded from counts).
    - Alpha is computed over all statements where at least 2 agents provided a value.
    - Free-text fields (A, I, Bdir, …) use exact-string comparison, so minor wording
      differences count as disagreement. Interpret alpha for those fields cautiously.
"""

import csv
import re
import sys
from collections import Counter


COMPARE_FIELDS = [
    "type",
    "A", "A_prop", "D", "I",
    "Bdir", "Bdir_prop", "Bind", "Bind_prop",
    "Cac", "Cex", "O",
    "E", "E_prop", "M", "F", "P", "P_prop",
]


def _id_sort_key(sid):
    m = re.match(r'^([A-Za-z]*)(\d+)(.*)$', sid)
    return (m.group(1), int(m.group(2)), m.group(3)) if m else (sid, 0, "")


def load_csv(path):
    rows = {}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows[row["id"]] = row
    return rows


def _krippendorffs_alpha_nominal(matrix):
    """
    Compute Krippendorff's Alpha for nominal data.

    matrix : list of lists, shape (n_units, n_raters).
              None = rater did not code this unit (missing).
              "" or any string = valid category value.

    Returns float in [-1, 1], or None if not computable (< 2 usable units).

    Formula (Hayes & Krippendorff 2007, Artstein & Poesio 2008):
      D_o = sum_u [ sum_{c≠k} d(v_uc, v_uk) ] / sum_u [ m_u * (m_u - 1) ]
      D_e = sum_{v≠w} n_v * n_w  /  n * (n - 1)
      α   = 1 - D_o / D_e
    where d(v, v') = 0 if v == v' else 1  (nominal metric)
    """
    usable = [(unit, sum(v is not None for v in unit))
              for unit in matrix]
    usable = [(unit, m) for unit, m in usable if m >= 2]
    if len(usable) < 2:
        return None

    # Observed disagreement
    D_o_num = 0
    D_o_den = 0
    for unit, m_u in usable:
        vals = [v for v in unit if v is not None]
        D_o_den += m_u * (m_u - 1)
        for c in range(len(vals)):
            for k in range(len(vals)):
                if c != k and vals[c] != vals[k]:
                    D_o_num += 1
    if D_o_den == 0:
        return None
    D_o = D_o_num / D_o_den

    # Expected disagreement
    all_vals = [v for unit, _ in usable for v in unit if v is not None]
    n = len(all_vals)
    if n < 2:
        return None
    counts = Counter(all_vals)
    D_e_num = sum(c1 * c2
                  for v1, c1 in counts.items()
                  for v2, c2 in counts.items()
                  if v1 != v2)
    D_e = D_e_num / (n * (n - 1))
    if D_e == 0:
        return 1.0

    return 1.0 - D_o / D_e


def _field_stats(field, runs, all_ids):
    """Return (n_all3, n_full_agree, matrix_for_alpha) for one field."""
    matrix = []
    n_all3 = 0
    n_full_agree = 0

    for sid in all_ids:
        vals = [
            r[sid].get(field, "").strip() if sid in r else None
            for r in runs
        ]
        n_present = sum(v is not None for v in vals)
        if n_present < 2:
            continue
        matrix.append(vals)
        if n_present == 3:
            n_all3 += 1
            if len(set(vals)) == 1:
                n_full_agree += 1

    return n_all3, n_full_agree, matrix


def compute_reliability(agent_paths, output_path):
    runs = [load_csv(p) for p in agent_paths]
    all_ids = sorted(
        set().union(*[r.keys() for r in runs]),
        key=_id_sort_key,
    )

    rows_out = []
    all_matrix = []
    total_all3 = 0
    total_full_agree = 0

    for field in COMPARE_FIELDS:
        n_all3, n_full_agree, matrix = _field_stats(field, runs, all_ids)
        pct = (n_full_agree / n_all3 * 100) if n_all3 > 0 else None
        alpha = _krippendorffs_alpha_nominal(matrix)

        rows_out.append({
            "field": field,
            "n_statements": n_all3,
            "n_full_agreement": n_full_agree,
            "pct_agreement": f"{pct:.1f}" if pct is not None else "N/A",
            "krippendorffs_alpha": f"{alpha:.3f}" if alpha is not None else "N/A",
        })

        all_matrix.extend(matrix)
        total_all3 += n_all3
        total_full_agree += n_full_agree

    overall_pct = (total_full_agree / total_all3 * 100) if total_all3 > 0 else None
    overall_alpha = _krippendorffs_alpha_nominal(all_matrix)
    rows_out.append({
        "field": "OVERALL",
        "n_statements": total_all3,
        "n_full_agreement": total_full_agree,
        "pct_agreement": f"{overall_pct:.1f}" if overall_pct is not None else "N/A",
        "krippendorffs_alpha": f"{overall_alpha:.3f}" if overall_alpha is not None else "N/A",
    })

    fieldnames = [
        "field", "n_statements", "n_full_agreement",
        "pct_agreement", "krippendorffs_alpha",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    pct_str = f"{overall_pct:.1f}%" if overall_pct is not None else "N/A"
    alpha_str = f"{overall_alpha:.3f}" if overall_alpha is not None else "N/A"
    print(f"Reliability: {output_path}")
    print(f"Overall ({len(COMPARE_FIELDS)} fields, {total_all3} statement-field pairs): "
          f"{pct_str} agreement, α = {alpha_str}")

    return rows_out


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python reliability.py agent1.csv agent2.csv agent3.csv reliability.csv")
        sys.exit(1)
    compute_reliability(sys.argv[1:4], sys.argv[4])
