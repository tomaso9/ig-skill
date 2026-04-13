"""Tests for merge.py — multi-agent IG coding merge and flag logic."""

import csv
import pytest
from merge import load_csv, merge_three

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FIELDNAMES = [
    "id", "type", "coding_level", "original_text",
    "A", "A_prop", "D", "I",
    "Bdir", "Bdir_prop", "Bind", "Bind_prop",
    "Cac", "Cex", "O",
    "E", "E_prop", "M", "F", "P", "P_prop",
    "ig_script_full", "notes",
]

BASE_ROW = {
    "id": "S1", "type": "REG", "coding_level": "IG Core",
    "original_text": "Farmers must submit forms.",
    "A": "farmers", "A_prop": "", "D": "must", "I": "submit",
    "Bdir": "forms", "Bdir_prop": "", "Bind": "", "Bind_prop": "",
    "Cac": "", "Cex": "", "O": "",
    "E": "", "E_prop": "", "M": "", "F": "", "P": "", "P_prop": "",
    "ig_script_full": "A(farmers) D(must) I(submit) Bdir(forms).",
    "notes": "",
}


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def make_paths(tmp_path, rows_per_run):
    """Write 3 CSVs and return their paths."""
    paths = []
    for i, rows in enumerate(rows_per_run, 1):
        p = str(tmp_path / f"agent{i}.csv")
        write_csv(p, rows)
        paths.append(p)
    return paths


# ---------------------------------------------------------------------------
# load_csv
# ---------------------------------------------------------------------------

def test_load_csv_keys_by_id(tmp_path):
    p = str(tmp_path / "run.csv")
    write_csv(p, [dict(BASE_ROW, id="S1"), dict(BASE_ROW, id="S2")])
    result = load_csv(p)
    assert set(result.keys()) == {"S1", "S2"}
    assert result["S1"]["A"] == "farmers"


# ---------------------------------------------------------------------------
# merge_three — no disagreements
# ---------------------------------------------------------------------------

def test_identical_runs_produce_no_flags(tmp_path):
    paths = make_paths(tmp_path, [[dict(BASE_ROW)]] * 3)
    c = str(tmp_path / "consensus.csv")
    r = str(tmp_path / "review.csv")
    merge_three(paths, c, r)

    consensus = read_csv(c)
    assert len(consensus) == 1
    assert consensus[0]["review_flag"] == "FALSE"
    assert consensus[0]["disagreement_fields"] == ""
    assert consensus[0]["A"] == "farmers"

    review = read_csv(r)
    assert len(review) == 0


# ---------------------------------------------------------------------------
# merge_three — single field disagreement
# ---------------------------------------------------------------------------

def test_single_field_disagreement_flagged(tmp_path):
    """Run 2 fills Cac; runs 1 and 3 leave it empty."""
    rows = [
        [dict(BASE_ROW, Cac="")],
        [dict(BASE_ROW, Cac="in Zone I")],
        [dict(BASE_ROW, Cac="")],
    ]
    paths = make_paths(tmp_path, rows)
    c = str(tmp_path / "consensus.csv")
    r = str(tmp_path / "review.csv")
    merge_three(paths, c, r)

    consensus = read_csv(c)
    assert consensus[0]["review_flag"] == "TRUE"
    assert "Cac" in consensus[0]["disagreement_fields"]

    review = read_csv(r)
    assert len(review) == 1
    assert review[0]["id"] == "S1"
    assert review[0]["field"] == "Cac"
    assert review[0]["run1_value"] == ""
    assert review[0]["run2_value"] == "in Zone I"
    assert review[0]["run3_value"] == ""


# ---------------------------------------------------------------------------
# merge_three — consensus value selection
# ---------------------------------------------------------------------------

def test_majority_vote_used_as_consensus(tmp_path):
    """Runs 1 and 3 agree on A; run 2 differs — majority wins."""
    rows = [
        [dict(BASE_ROW, A="farmers")],
        [dict(BASE_ROW, A="certified farmers")],
        [dict(BASE_ROW, A="farmers")],
    ]
    paths = make_paths(tmp_path, rows)
    c = str(tmp_path / "consensus.csv")
    r = str(tmp_path / "review.csv")
    merge_three(paths, c, r)

    consensus = read_csv(c)
    assert consensus[0]["A"] == "farmers"
    assert consensus[0]["review_flag"] == "TRUE"


def test_no_majority_falls_back_to_run1(tmp_path):
    """All three differ — run1 value used as consensus."""
    rows = [
        [dict(BASE_ROW, A="farmers")],
        [dict(BASE_ROW, A="certified farmers")],
        [dict(BASE_ROW, A="organic farmers")],
    ]
    paths = make_paths(tmp_path, rows)
    c = str(tmp_path / "consensus.csv")
    r = str(tmp_path / "review.csv")
    merge_three(paths, c, r)

    consensus = read_csv(c)
    assert consensus[0]["A"] == "farmers"
    assert consensus[0]["review_flag"] == "TRUE"


# ---------------------------------------------------------------------------
# merge_three — type disagreement
# ---------------------------------------------------------------------------

def test_type_disagreement_flagged(tmp_path):
    rows = [
        [dict(BASE_ROW, type="REG")],
        [dict(BASE_ROW, type="CONST")],
        [dict(BASE_ROW, type="REG")],
    ]
    paths = make_paths(tmp_path, rows)
    c = str(tmp_path / "consensus.csv")
    r = str(tmp_path / "review.csv")
    merge_three(paths, c, r)

    consensus = read_csv(c)
    assert consensus[0]["review_flag"] == "TRUE"
    assert "type" in consensus[0]["disagreement_fields"]

    review = read_csv(r)
    assert any(row["field"] == "type" for row in review)


# ---------------------------------------------------------------------------
# merge_three — multiple fields disagree
# ---------------------------------------------------------------------------

def test_multiple_disagreeing_fields_produce_multiple_review_rows(tmp_path):
    """Cac and Cex both disagree — two rows in review CSV."""
    rows = [
        [dict(BASE_ROW, Cac="", Cex="annually")],
        [dict(BASE_ROW, Cac="in Zone I", Cex="")],
        [dict(BASE_ROW, Cac="", Cex="annually")],
    ]
    paths = make_paths(tmp_path, rows)
    c = str(tmp_path / "consensus.csv")
    r = str(tmp_path / "review.csv")
    merge_three(paths, c, r)

    review = read_csv(r)
    assert len(review) == 2
    fields = {row["field"] for row in review}
    assert "Cac" in fields
    assert "Cex" in fields


# ---------------------------------------------------------------------------
# merge_three — review CSV content column
# ---------------------------------------------------------------------------

def test_review_csv_records_consensus_used(tmp_path):
    rows = [
        [dict(BASE_ROW, Cac="")],
        [dict(BASE_ROW, Cac="in Zone I")],
        [dict(BASE_ROW, Cac="")],
    ]
    paths = make_paths(tmp_path, rows)
    c = str(tmp_path / "consensus.csv")
    r = str(tmp_path / "review.csv")
    merge_three(paths, c, r)

    review = read_csv(r)
    assert review[0]["consensus_used"] == ""  # majority is ""
