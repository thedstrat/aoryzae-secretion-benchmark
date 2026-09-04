#!/usr/bin/env python3
"""Structural validation for the benchmark CSVs.

Checks that the four tables in data/ hold together: IDs are unique,
references between files point at rows that exist, and the fields that must
always carry a value do. Nothing here knows any biology - a row can pass
every check and still misreport what the paper said.

Usage: python scripts/validate_data.py
Exits 0 if everything passes, 1 if anything fails.
"""

import sys
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
ARMS = {"control", "modified"}


def load(name):
    """Read a CSV as strings, keeping blank cells as empty strings rather than NaN."""
    path = DATA / name
    if not path.exists():
        sys.exit(f"ERROR: missing data file: {path}")
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def at_line(i):
    """The CSV line number for row i - line 1 is the header."""
    return i + 2


def unique(column, what):
    """Report any value in an ID column that appears more than once."""
    counts = column.value_counts()
    return [
        f"{what} '{value}' repeats on lines "
        + ", ".join(str(at_line(i)) for i in column.index[column == value])
        for value in counts[counts > 1].index
    ]


def rows_failing(frame, column, ok, complaint, id_column=None):
    """Report every row whose value in `column` fails the test `ok`.

    `complaint` finishes the message; any '{}' in it is filled with the value.
    """
    problems = []
    for i, value in frame[column].items():
        if ok(value):
            continue
        where = f"line {at_line(i)}"
        if id_column:
            where += f" ({id_column}={frame.at[i, id_column]})"
        problems.append(f"{where}: {column} {complaint.format(value or '(blank)')}")
    return problems


def main():
    studies = load("studies.csv")
    experiments = load("experiments.csv")
    genes = load("experiment_genes.csv")
    outcomes = load("outcomes.csv")

    print(f"Validating {DATA}\n")
    for name, frame in [("studies.csv", studies), ("experiments.csv", experiments),
                        ("experiment_genes.csv", genes), ("outcomes.csv", outcomes)]:
        print(f"  {name:<22} {len(frame):>4} rows")
    print()

    study_ids = set(studies["study_id"])
    experiment_ids = set(experiments["experiment_id"])
    measured = set(outcomes["experiment_id"])
    edited = set(genes["experiment_id"])

    # experiment_genes.csv has no single ID column: one experiment may edit
    # several genes, so a row is identified by experiment and gene together.
    # The gene half of that key is gene_name, not gene_id: gene_id is allowed
    # to be TODO until the locus tag is looked up, and several TODO rows under
    # one experiment are distinct edits, not duplicates.
    gene_keys = genes["experiment_id"] + " + " + genes["gene_name"]

    checks = [
        ("studies.csv: study_id is unique",
            unique(studies["study_id"], "study_id")),
        ("experiments.csv: experiment_id is unique",
            unique(experiments["experiment_id"], "experiment_id")),
        ("outcomes.csv: outcome_id is unique",
            unique(outcomes["outcome_id"], "outcome_id")),
        ("experiment_genes.csv: experiment_id + gene_name is unique",
            unique(gene_keys, "experiment_id + gene_name")),

        ("experiments.csv: every study_id exists in studies.csv",
            rows_failing(experiments, "study_id", lambda v: v in study_ids,
                         "'{}' does not exist", "experiment_id")),
        ("experiment_genes.csv: every experiment_id exists in experiments.csv",
            rows_failing(genes, "experiment_id", lambda v: v in experiment_ids,
                         "'{}' does not exist", "gene_id")),
        ("outcomes.csv: every experiment_id exists in experiments.csv",
            rows_failing(outcomes, "experiment_id", lambda v: v in experiment_ids,
                         "'{}' does not exist", "outcome_id")),

        ("outcomes.csv: source_ref is filled in on every row",
            rows_failing(outcomes, "source_ref", lambda v: v.strip(),
                         "is empty", "outcome_id")),
        ("outcomes.csv: arm is 'control' or 'modified' on every row",
            rows_failing(outcomes, "arm", lambda v: v in ARMS,
                         "is '{}', expected control or modified", "outcome_id")),

        ("experiments.csv: every experiment has at least one outcomes row",
            rows_failing(experiments, "experiment_id", lambda v: v in measured,
                         "'{}' has no rows in outcomes.csv")),
        ("experiments.csv: every experiment has at least one experiment_genes row",
            rows_failing(experiments, "experiment_id", lambda v: v in edited,
                         "'{}' has no rows in experiment_genes.csv")),
    ]

    for label, problems in checks:
        print(f"  {'FAIL' if problems else 'PASS'}  {label}")
        for problem in problems:
            print(f"          {problem}")

    failed = [label for label, problems in checks if problems]
    print(f"\n  {len(checks) - len(failed)} of {len(checks)} checks passed")

    if failed:
        print("\nFAILED")
        return 1
    print("\nPASSED - the tables are structurally sound.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
