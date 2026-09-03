#!/usr/bin/env python3
"""Structural validation for the benchmark CSVs.

Checks that the four tables in data/ hold together: unique IDs, working
references between files, and the few fields that must always be present.
Nothing here knows any biology - a row can pass every check and still
misreport what the paper said.

Usage: python scripts/validate_data.py
Exits 0 if everything passes, 1 otherwise.
"""

import sys
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

REQUIRED_COLUMNS = {
    "studies.csv": ["study_id"],
    "experiments.csv": ["experiment_id", "study_id"],
    "experiment_genes.csv": ["experiment_id", "gene_id"],
    "outcomes.csv": ["outcome_id", "experiment_id", "arm", "source_ref"],
}

VALID_ARMS = {"control", "modified"}


class Report:
    """Collects check results so every problem is reported, not just the first."""

    def __init__(self):
        self.checks = []

    def record(self, label, problems):
        self.checks.append((label, list(problems)))

    def print_summary(self):
        for label, problems in self.checks:
            status = "FAIL" if problems else "PASS"
            print(f"  {status}  {label}")
            for problem in problems:
                print(f"          {problem}")

        failed = [label for label, problems in self.checks if problems]
        total_problems = sum(len(problems) for _, problems in self.checks)

        print()
        print(f"  {len(self.checks) - len(failed)} of {len(self.checks)} checks passed")

        if failed:
            print(f"  {total_problems} problem(s) found in {len(failed)} check(s).")
            print()
            print("FAILED")
        else:
            print()
            print("PASSED - the tables are structurally sound.")

        return not failed


def line_of(index):
    """CSV line number for a DataFrame row: line 1 is the header."""
    return index + 2


def load_tables():
    """Read the four CSVs as strings, with blank cells kept as empty strings."""
    tables = {}
    for filename, columns in REQUIRED_COLUMNS.items():
        path = DATA_DIR / filename
        if not path.exists():
            sys.exit(f"ERROR: missing data file: {path}")

        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
        missing = [column for column in columns if column not in frame.columns]
        if missing:
            sys.exit(f"ERROR: {filename} is missing column(s): {', '.join(missing)}")

        tables[filename] = frame

    return tables


def check_unique(frame, filename, column):
    """Every value in an ID column appears exactly once."""
    problems = []
    counts = frame[column].value_counts()
    for value, count in counts[counts > 1].items():
        lines = [str(line_of(i)) for i in frame.index[frame[column] == value]]
        shown = value if value.strip() else "(blank)"
        problems.append(f"{column} '{shown}' used {count}x, on lines {', '.join(lines)}")
    return problems


def check_unique_pair(frame, filename, columns):
    """A file keyed by a column pair has no duplicate pair."""
    problems = []
    pairs = frame[columns].agg(" + ".join, axis=1)
    counts = pairs.value_counts()
    for value, count in counts[counts > 1].items():
        lines = [str(line_of(i)) for i in frame.index[pairs == value]]
        problems.append(f"{' + '.join(columns)} '{value}' used {count}x, on lines {', '.join(lines)}")
    return problems


def check_reference(child, child_column, parent_ids, label_column=None):
    """Every value in a child column points at an ID that exists in the parent file."""
    problems = []
    for i, value in child[child_column].items():
        if value in parent_ids:
            continue
        shown = value if value.strip() else "(blank)"
        where = f"line {line_of(i)}"
        if label_column is not None:
            where += f" ({label_column}={child.at[i, label_column]})"
        problems.append(f"{where}: {child_column} '{shown}' does not exist")
    return problems


def check_filled(frame, column, label_column):
    """A column that must carry a value on every row."""
    problems = []
    for i, value in frame[column].items():
        if not value.strip():
            problems.append(f"line {line_of(i)} ({label_column}={frame.at[i, label_column]}): {column} is empty")
    return problems


def check_allowed_values(frame, column, allowed, label_column):
    """A column restricted to a fixed set of values."""
    problems = []
    for i, value in frame[column].items():
        if value in allowed:
            continue
        shown = value if value.strip() else "(blank)"
        problems.append(
            f"line {line_of(i)} ({label_column}={frame.at[i, label_column]}): "
            f"{column} is '{shown}', expected one of {', '.join(sorted(allowed))}"
        )
    return problems


def check_has_children(parent, parent_column, child_ids, child_name):
    """Every parent row is referenced by at least one row in a child file."""
    problems = []
    for i, value in parent[parent_column].items():
        if value not in child_ids:
            problems.append(f"line {line_of(i)}: {parent_column} '{value}' has no rows in {child_name}")
    return problems


def main():
    print(f"Validating {DATA_DIR}")
    print()

    tables = load_tables()
    studies = tables["studies.csv"]
    experiments = tables["experiments.csv"]
    genes = tables["experiment_genes.csv"]
    outcomes = tables["outcomes.csv"]

    for filename, frame in tables.items():
        print(f"  {filename:<22} {len(frame):>4} rows")
    print()

    report = Report()

    # IDs are unique within their own file.
    report.record(
        "studies.csv: study_id is unique",
        check_unique(studies, "studies.csv", "study_id"),
    )
    report.record(
        "experiments.csv: experiment_id is unique",
        check_unique(experiments, "experiments.csv", "experiment_id"),
    )
    report.record(
        "outcomes.csv: outcome_id is unique",
        check_unique(outcomes, "outcomes.csv", "outcome_id"),
    )
    # experiment_genes.csv has no single ID column: one experiment may edit
    # several genes, so a row is identified by the experiment and gene together.
    report.record(
        "experiment_genes.csv: experiment_id + gene_id is unique",
        check_unique_pair(genes, "experiment_genes.csv", ["experiment_id", "gene_id"]),
    )

    # References between files point at rows that exist.
    study_ids = set(studies["study_id"])
    experiment_ids = set(experiments["experiment_id"])

    report.record(
        "experiments.csv: every study_id exists in studies.csv",
        check_reference(experiments, "study_id", study_ids, "experiment_id"),
    )
    report.record(
        "experiment_genes.csv: every experiment_id exists in experiments.csv",
        check_reference(genes, "experiment_id", experiment_ids, "gene_id"),
    )
    report.record(
        "outcomes.csv: every experiment_id exists in experiments.csv",
        check_reference(outcomes, "experiment_id", experiment_ids, "outcome_id"),
    )

    # Fields that must always carry a value.
    report.record(
        "outcomes.csv: source_ref is filled in on every row",
        check_filled(outcomes, "source_ref", "outcome_id"),
    )
    report.record(
        "outcomes.csv: arm is 'control' or 'modified' on every row",
        check_allowed_values(outcomes, "arm", VALID_ARMS, "outcome_id"),
    )

    # Every experiment is backed by rows in the child files.
    report.record(
        "experiments.csv: every experiment has at least one outcomes row",
        check_has_children(experiments, "experiment_id", set(outcomes["experiment_id"]), "outcomes.csv"),
    )
    report.record(
        "experiments.csv: every experiment has at least one experiment_genes row",
        check_has_children(experiments, "experiment_id", set(genes["experiment_id"]), "experiment_genes.csv"),
    )

    return 0 if report.print_summary() else 1


if __name__ == "__main__":
    sys.exit(main())
