"""
Institutional complexity metrics for IG 2.0 coded statements.

Implements Institutional Tree Depth, ISC (Eq. 8.1), ISR (Eq. 8.2), and
Table 8.7 component-level metrics from Frantz & Siddiki (2022), Chapter 8.

Usage:
    python complexity.py <input_csv> <output_csv> [--metrics m1,m2,...]

Metric keys (comma-separated for --metrics):
    depth          Institutional Tree Depth (1 = flat, +1 per nesting level)
    isc            Institutional State Complexity (Eq. 8.1)
    isr            Institutional State Regimentation (Eq. 8.2)
    conditions     Conditions Variability + Option Count  (Cac, level 0)
    discretion     Discretion Extent + Option Count       (I/Aim, level 0)
    activity_state Activity State Variability + Count     (Cac, level >= 1)
    application    Application Variability + Option Count (Bdir/Bind, level 0)

Input CSV must contain columns: id, type, ig_script_full
Output is always written to <output_csv> (name it with _IG_metrics.csv suffix by convention).
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ALL_METRIC_KEYS = ['depth', 'isc', 'isr', 'conditions', 'discretion', 'activity_state', 'application']

# Component names in IG Script (longest first so the regex alternation matches greedily)
_COMP_NAMES = [
    'A_prop', 'Bdir_prop', 'Bind_prop', 'E_prop', 'P_prop',
    'Bdir', 'Bind', 'Cac', 'Cex',
    'A', 'D', 'I', 'O', 'E', 'M', 'F', 'P',
]

# Matches a component token: name + optional ,p suffix + optional [annotations]
_COMP_RE = re.compile(
    r'(' + '|'.join(re.escape(c) for c in _COMP_NAMES) + r')'
    r'(?:,p(?:\d+(?:,p\d+)*)?)?'   # optional ,p or ,p1 or ,p1,p2 ... property suffix
    r'(?:\[[^\[\]]*\])*',           # zero or more [annotation] blocks
)

# Matches a logical combination operator
_OP_RE = re.compile(r'\[(AND|OR|XOR|NOT)\]', re.IGNORECASE)

# Base-name normalisation: _prop variants map back to their root component
_BASE_MAP = {
    'A_prop': 'A', 'Bdir_prop': 'Bdir', 'Bind_prop': 'Bind',
    'E_prop': 'E', 'P_prop': 'P',
}


# ---------------------------------------------------------------------------
# DoV / ISR helpers  (Frantz & Siddiki 2022, Table 8.6, Eq. 8.1–8.2)
# ---------------------------------------------------------------------------

def _dov(op: str, k: int) -> float:
    """Degree of Variability for k components joined by op."""
    if k <= 1:
        return 1.0
    op = op.upper()
    if op == 'AND':
        return 1.0
    if op == 'XOR':
        return float(k)
    if op == 'OR':
        return float(2 ** k - 1)
    return 1.0  # unknown op → AND semantics


def _isr_weight(op: str, k: int) -> float:
    """ISR contribution = k / DoV."""
    d = _dov(op, k)
    return (k / d) if d else 0.0


# ---------------------------------------------------------------------------
# Bracket utilities
# ---------------------------------------------------------------------------

def _find_matching(text: str, pos: int, open_c: str, close_c: str) -> int:
    """Return index of the close_c that matches open_c at text[pos]."""
    depth = 0
    for i in range(pos, len(text)):
        if text[i] == open_c:
            depth += 1
        elif text[i] == close_c:
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1  # unmatched — return end-of-string


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def _parse_scope(text: str, level: int = 0) -> dict:
    """
    Recursively parse one IG Script scope.

    Returns:
        {
          'level':     int,
          'tokens':    list of ('COMP', base_name) | ('OP', op) | ('NESTED', sub),
          'nested':    list of sub-scope dicts  (from {} blocks),
          'max_depth': int,
        }
    """
    tokens: list = []
    nested: list = []
    i = 0
    n = len(text)

    while i < n:
        c = text[i]

        # Whitespace and terminal punctuation
        if c in ' \t\n\r.,;':
            i += 1
            continue

        # Logical operator [AND], [OR], [XOR], [NOT]
        m = _OP_RE.match(text, i)
        if m:
            op = m.group(1).upper()
            tokens.append(('OP', op))
            i = m.end()
            continue

        # Annotation-only bracket that is NOT an operator, e.g. [stype=monitored]
        if c == '[':
            close = _find_matching(text, i, '[', ']')
            i = close + 1
            continue

        # Component token
        m = _COMP_RE.match(text, i)
        if m:
            raw_name = m.group(1)
            base = _BASE_MAP.get(raw_name, raw_name)
            j = m.end()
            # Skip whitespace
            while j < n and text[j] in ' \t\n\r':
                j += 1
            # Must be followed by ( or { to count as a real component token
            if j >= n or text[j] not in ('(', '{'):
                i += 1  # stray letter — skip one char and keep scanning
                continue
            if text[j] == '(':
                close = _find_matching(text, j, '(', ')')
                # Scan inside () for bare {} component-level nesting
                inner = text[j + 1:close]
                _collect_brace_blocks(inner, level + 1, nested)
                i = close + 1
            else:  # text[j] == '{'
                close = _find_matching(text, j, '{', '}')
                inner = text[j + 1:close]
                sub = _parse_scope(inner, level + 1)
                nested.append(sub)
                i = close + 1
            tokens.append(('COMP', base))
            continue

        # Bare { } block (statement-level or Or-else nesting)
        if c == '{':
            close = _find_matching(text, i, '{', '}')
            inner = text[i + 1:close]
            sub = _parse_scope(inner, level + 1)
            nested.append(sub)
            tokens.append(('NESTED', sub))
            i = close + 1
            continue

        # Anything else — skip
        i += 1

    max_depth = level
    for sub in nested:
        if sub['max_depth'] > max_depth:
            max_depth = sub['max_depth']

    return {'level': level, 'tokens': tokens, 'nested': nested, 'max_depth': max_depth}


def _collect_brace_blocks(text: str, level: int, out: list) -> None:
    """Find and recursively parse bare { } blocks inside parenthesised content."""
    i = 0
    n = len(text)
    while i < n:
        if text[i] == '(':
            close = _find_matching(text, i, '(', ')')
            i = close + 1
        elif text[i] == '{':
            close = _find_matching(text, i, '{', '}')
            inner = text[i + 1:close]
            sub = _parse_scope(inner, level)
            out.append(sub)
            i = close + 1
        else:
            i += 1


# ---------------------------------------------------------------------------
# Operator-group extraction
# ---------------------------------------------------------------------------

def _extract_groups(tokens: list) -> List[Tuple[str, str, int]]:
    """
    From a token list, find consecutive COMP tokens of the same type.
    Explicit operators between consecutive same-type tokens are recorded;
    implicit AND applies when no operator appears between them.

    Returns list of (op, comp_name, k) where k >= 1.
    """
    groups: List[Tuple[str, str, int]] = []
    current_comp: str = ''
    current_op: str = 'AND'
    current_k: int = 0
    pending_op: str = ''

    def _flush():
        if current_comp and current_k:
            groups.append((current_op, current_comp, current_k))

    for tok in tokens:
        kind = tok[0]
        if kind == 'OP':
            if tok[1] != 'NOT':
                pending_op = tok[1]
        elif kind == 'COMP':
            comp = tok[1]
            if comp == current_comp:
                # Same component — extend the current run
                if pending_op:
                    current_op = pending_op
                current_k += 1
                pending_op = ''
            else:
                # Different component — flush and start new run
                _flush()
                current_comp = comp
                current_op = pending_op or 'AND'
                current_k = 1
                pending_op = ''
        elif kind == 'NESTED':
            # Bare nested block (horizontal nesting) — break any active component run
            _flush()
            current_comp = ''
            current_k = 0
            pending_op = ''

    _flush()
    return groups


# ---------------------------------------------------------------------------
# Level aggregation
# ---------------------------------------------------------------------------

def _collect_by_level(parse_result: dict) -> Dict[int, List[Tuple[str, str, int]]]:
    """Return all operator groups keyed by nesting level."""
    by_level: Dict[int, List[Tuple[str, str, int]]] = {}

    def _recurse(pr: dict) -> None:
        lvl = pr['level']
        for g in _extract_groups(pr['tokens']):
            by_level.setdefault(lvl, []).append(g)
        for sub in pr['nested']:
            _recurse(sub)

    _recurse(parse_result)
    return by_level


# ---------------------------------------------------------------------------
# ISC / ISR  (Eq. 8.1–8.2)
# ---------------------------------------------------------------------------

def _compute_isc(by_level: Dict[int, List[Tuple[str, str, int]]], max_level: int) -> float:
    """
    ISC = product across levels of (sum of DoV for groups with k >= 2 at that level).
    A level with no such groups contributes factor 1.
    """
    isc = 1.0
    for lvl in range(max_level + 1):
        level_sum = sum(_dov(op, k) for op, _, k in by_level.get(lvl, []) if k >= 2)
        if level_sum > 0:
            isc *= level_sum
    return isc


def _compute_isr(by_level: Dict[int, List[Tuple[str, str, int]]], max_level: int) -> float:
    """
    ISR = product across levels of (sum of k/DoV for groups with k >= 2 at that level).
    A level with no such groups contributes factor 1.
    """
    isr = 1.0
    for lvl in range(max_level + 1):
        level_sum = sum(_isr_weight(op, k) for op, _, k in by_level.get(lvl, []) if k >= 2)
        if level_sum > 0:
            isr *= level_sum
    return isr


# ---------------------------------------------------------------------------
# Component-level metrics  (Table 8.7)
# ---------------------------------------------------------------------------

def _component_metric(
    by_level: Dict[int, List[Tuple[str, str, int]]],
    target_comps: List[str],
    target_levels: List[int],
) -> Tuple[float, int]:
    """
    Variability = product of DoV for groups with k >= 2 matching target component/level.
    Option count = sum of k across those groups.
    Returns (variability, option_count).
    """
    variability = 1.0
    option_count = 0
    found_any = False
    for lvl in target_levels:
        for op, comp, k in by_level.get(lvl, []):
            if comp in target_comps and k >= 2:
                variability *= _dov(op, k)
                option_count += k
                found_any = True
    if not found_any:
        return 1.0, 0
    return variability, option_count


# ---------------------------------------------------------------------------
# Top-level parse + metric computation
# ---------------------------------------------------------------------------

def parse_ig_script(ig_script: str) -> dict:
    """Parse one ig_script_full value. Returns intermediate data for metric computation."""
    text = (ig_script or '').strip()
    if not text:
        return {'depth': 1, 'by_level': {}, 'max_level': 0}
    pr = _parse_scope(text, level=0)
    by_level = _collect_by_level(pr)
    return {'depth': pr['max_depth'] + 1, 'by_level': by_level, 'max_level': pr['max_depth']}


def compute_metrics(parsed: dict, selected_keys: List[str]) -> dict:
    """Compute the requested metrics from a parse result dict."""
    by_level = parsed['by_level']
    max_level = parsed['max_level']
    results: dict = {}

    if 'depth' in selected_keys:
        results['tree_depth'] = parsed['depth']

    if 'isc' in selected_keys:
        results['ISC'] = round(_compute_isc(by_level, max_level), 4)

    if 'isr' in selected_keys:
        results['ISR'] = round(_compute_isr(by_level, max_level), 4)

    if 'conditions' in selected_keys:
        v, k = _component_metric(by_level, ['Cac'], [0])
        results['cond_variability_L0'] = round(v, 4)
        results['cond_option_count_L0'] = k

    if 'discretion' in selected_keys:
        v, k = _component_metric(by_level, ['I'], [0])
        results['discret_extent_L0'] = round(v, 4)
        results['discret_option_count_L0'] = k

    if 'activity_state' in selected_keys:
        higher = list(range(1, max_level + 1)) if max_level >= 1 else []
        v, k = _component_metric(by_level, ['Cac'], higher)
        results['activity_state_var_L1plus'] = round(v, 4)
        results['activity_state_opt_L1plus'] = k

    if 'application' in selected_keys:
        v, k = _component_metric(by_level, ['Bdir', 'Bind'], [0])
        results['app_variability_L0'] = round(v, 4)
        results['app_option_count_L0'] = k

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_summary(results: list, metric_cols: list) -> None:
    col_w = max(14, *(len(c) for c in metric_cols)) + 2
    id_w, type_w = 10, 8
    header = f"{'ID':<{id_w}} {'Type':<{type_w}}" + ''.join(f" {c:<{col_w}}" for c in metric_cols)
    print(header)
    print('-' * len(header))
    for r in results:
        line = f"{r['id']:<{id_w}} {r['type']:<{type_w}}"
        for c in metric_cols:
            line += f" {str(r.get(c, '')):<{col_w}}"
        print(line)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Compute institutional complexity metrics for IG 2.0 coded statements.'
    )
    parser.add_argument('input_csv', help='Input CSV with ig_script_full column')
    parser.add_argument('output_csv', help='Output CSV path (use _IG_metrics.csv suffix by convention)')
    parser.add_argument(
        '--metrics',
        default=','.join(ALL_METRIC_KEYS),
        help=f"Comma-separated metric keys. Available: {', '.join(ALL_METRIC_KEYS)}",
    )
    args = parser.parse_args()

    selected_keys = [k.strip() for k in args.metrics.split(',') if k.strip() in ALL_METRIC_KEYS]
    if not selected_keys:
        print(f"No valid metric keys. Available: {', '.join(ALL_METRIC_KEYS)}", file=sys.stderr)
        sys.exit(1)

    # Read input
    try:
        with open(args.input_csv, encoding='utf-8', newline='') as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"Input file not found: {args.input_csv}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("Input CSV is empty.", file=sys.stderr)
        sys.exit(1)

    if 'ig_script_full' not in rows[0]:
        print("Column 'ig_script_full' not found in input CSV.", file=sys.stderr)
        sys.exit(1)

    # Compute metrics
    output_rows = []
    metric_cols: list = []
    for row in rows:
        ig_text = row.get('ig_script_full') or ''
        parsed = parse_ig_script(ig_text)
        metrics = compute_metrics(parsed, selected_keys)
        if not metric_cols:
            metric_cols = list(metrics.keys())
        out = {'id': row.get('id', ''), 'type': row.get('type', '')}
        out.update(metrics)
        output_rows.append(out)

    # Write output CSV
    fieldnames = ['id', 'type'] + metric_cols
    out_path = Path(args.output_csv)
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Metrics CSV: {out_path} ({len(output_rows)} statements)\n")
    _print_summary(output_rows, metric_cols)


if __name__ == '__main__':
    main()
