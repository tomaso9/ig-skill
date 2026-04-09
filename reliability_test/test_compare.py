"""Tests for compare.py utility functions."""

import csv
import os
import pytest
from compare import load_csv, jaccard, cohens_kappa


# --- load_csv ---

def test_load_csv_returns_dict_keyed_by_id(tmp_path):
    csv_path = tmp_path / "test.csv"
    csv_path.write_text(
        "id,type,A,D,I\nS1,REG,farmers,must,submit\nS2,CONST,,is,defined as\n",
        encoding="utf-8",
    )
    result = load_csv(str(csv_path))
    assert set(result.keys()) == {"S1", "S2"}
    assert result["S1"]["A"] == "farmers"
    assert result["S2"]["type"] == "CONST"


# --- jaccard ---

def test_jaccard_identical_strings():
    assert jaccard("organic farmers", "organic farmers") == 1.0


def test_jaccard_no_overlap():
    assert jaccard("organic farmers", "water district") == 0.0


def test_jaccard_partial_overlap():
    score = jaccard("certified organic farmer", "certified farmer")
    assert 0.0 < score < 1.0


def test_jaccard_both_empty():
    assert jaccard("", "") == 1.0


def test_jaccard_one_empty():
    assert jaccard("organic", "") == 0.0
    assert jaccard("", "organic") == 0.0


# --- cohens_kappa ---

def test_kappa_perfect_agreement():
    labels = ["REG", "CONST", "REG", "HYB"]
    assert cohens_kappa(labels, labels) == pytest.approx(1.0)


def test_kappa_no_agreement():
    a = ["REG", "CONST", "REG", "CONST"]
    b = ["CONST", "REG", "CONST", "REG"]
    assert cohens_kappa(a, b) < 0


def test_kappa_empty_input():
    assert cohens_kappa([], []) is None


def test_kappa_all_same_class_both_agree():
    # p_e = 1.0, returns 1.0 by convention
    a = ["REG", "REG", "REG"]
    b = ["REG", "REG", "REG"]
    assert cohens_kappa(a, b) == 1.0
