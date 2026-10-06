#!/usr/bin/env python3
"""Structural validation for the benchmark CSVs.

Checks that the four tables in data/ hold together: IDs are unique,
references between files point at rows that exist, and the fields that must
always carry a value do. Nothing here knows any biology - a row can pass
every check and still misreport what the paper said.

Output is split in two. ERRORS mean the data is broken and must be fixed:
duplicate IDs, references that point nowhere, a column holding a value it
cannot hold. WARNINGS mean a human has to decide something - a vocabulary
term the README does not declare, a control measurement that looks
duplicated - and may well be correct, so they do not fail the run.

Usage: python scripts/validate_data.py [--strict]
Exits 0 if there are no errors, 1 if there are. With --strict, warnings
count as errors too, which is what a CI run should use.
"""

import sys
from pathlib import Path

import pandas as pd

from build_edited_genes import COLUMN as EDITED_GENES, column_for

DATA = Path(__file__).resolve().parent.parent / "data"
ARMS = {"control", "modified"}

# The vocabularies the README declares, which is where they are defined for a
# reader. They are listed again here so a term that reaches the CSVs without
# reaching the README gets noticed; adding one is a maintainer decision
# (Rule 6), so it deliberately takes an edit in both places. These sets are
# supersets of what the data currently uses: the README lists values no
# curated paper has needed yet.
VOCABULARIES = {
    "host_effect": {
        "no_reported_defect", "conidiation_impaired", "conidiation_reduced",
        "conidiation_largely_restored", "not_reported",
    },
    "gene_role": {
        "remove_protease", "fix_misrouting", "block_autophagy",
        "enhance_trafficking", "reduce_competition", "improve_folding",
        "change_shape", "target_regulator", "design_the_construct", "unknown",
    },
    "edit_type": {
        "disruption", "promoter_replacement", "deletion", "overexpression",
    },
}

# Rule 2: existing papers contribute roughly this many outcome rows each. Only
# the upper bound warns - a study part-way through curation is legitimately
# short, and warning on that would fire on ordinary work in progress.
USUAL_OUTCOME_ROWS = (4, 11)


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


def matches_gene_rows(experiments, genes):
    """Report every experiments.csv row whose edited_genes_vs_control is stale.

    The column is generated from experiment_genes.csv, so the two disagreeing
    means experiments.csv was hand-edited or a gene row moved under it since
    it was last built.
    """
    if EDITED_GENES not in experiments.columns:
        return [f"experiments.csv has no {EDITED_GENES} column; "
                "run python scripts/build_edited_genes.py"]
    expected = column_for(experiments, genes)
    return [
        f"line {at_line(i)} ({experiments.at[i, 'experiment_id']}): "
        f"{EDITED_GENES} is '{value or '(blank)'}', expected '{want}'"
        for (i, value), want in zip(experiments[EDITED_GENES].items(), expected)
        if value != want
    ]


def count(n, what):
    """'1 error', '2 errors' - a summary line reads badly without it."""
    return f"{n} {what}" if n == 1 else f"{n} {what}s"


def report(checks, tag):
    """Print one PASS/FAIL/WARN line per check, then any lines it produced.

    A problem may carry a '-> decide:' continuation after a newline; it is
    indented under the line it belongs to.
    """
    for label, problems in checks:
        print(f"  {tag if problems else 'PASS'}  {label}")
        for problem in problems:
            first, *rest = problem.split("\n")
            print(f"          {first}")
            for line in rest:
                print(f"            {line}")


# --- warnings --------------------------------------------------------------
#
# Each of these returns lines a human has to read, not defects. Every line
# ends with a "-> decide:" sentence saying what the decision actually is, so
# the reader does not have to reconstruct it from the rule number.


def undeclared_terms(frame, column, id_column):
    """Report values in `column` that the README vocabulary table does not list.

    A term the CSVs use but the README does not declare may be the right new
    term or a synonym for one that already fits. Rule 6 makes that the
    maintainer's call, so it warns rather than failing.
    """
    allowed = VOCABULARIES[column]
    where = {}
    for i, value in frame[column].items():
        if value in allowed:
            continue
        where.setdefault(value, []).append(f"line {at_line(i)} ({frame.at[i, id_column]})")
    return [
        f"{column} '{value or '(blank)'}' is not declared, on " + ", ".join(lines)
        + f"\n-> decide: new {column} '{value or '(blank)'}' - add to the README "
        + "vocabulary table, or use an existing value ("
        + ", ".join(sorted(allowed)) + ")"
        for value, lines in where.items()
    ]


def studies_without_a_control(experiments, outcomes):
    """Report studies that have curated experiments but no control measurement.

    Controls are shared: Rule 12 lets several experiments read against one
    control row, so an experiment of its own having no control row is normal.
    A whole study having none means nothing in it can be read against
    anything, which is usually a missing row rather than a decision.
    """
    study_of = dict(zip(experiments["experiment_id"], experiments["study_id"]))
    with_control = {
        study_of[experiment]
        for experiment in outcomes.loc[outcomes["arm"] == "control", "experiment_id"]
        if experiment in study_of
    }
    curated = {}
    for experiment, study in study_of.items():
        if experiment in set(outcomes["experiment_id"]) and study not in with_control:
            curated.setdefault(study, []).append(experiment)
    return [
        f"{study} has no outcome row with arm=control, across "
        f"{len(experiments_in)} experiment(s): " + ", ".join(sorted(experiments_in))
        + "\n-> decide: add the control measurement the paper reports, or say in "
        "notes what these values are read against"
        for study, experiments_in in sorted(curated.items())
    ]


def duplicated_control_measurements(outcomes, experiments):
    """Report one control measurement that appears under several experiments.

    Rule 12: a control measured once gets one row, however many experiments
    cite it. The same strain, number, unit, quantity, day and assay appearing
    twice in one study is either that duplication or a genuine re-measurement,
    which the rows cannot distinguish - hence a warning. Rows with no number
    are skipped: Rule 11 allows a relative control to carry none, and those
    would collide with each other for a reason that is not a defect.
    """
    study_of = dict(zip(experiments["experiment_id"], experiments["study_id"]))
    groups = {}
    controls = outcomes[outcomes["arm"] == "control"]
    for i, row in controls.iterrows():
        if not row["value"].strip():
            continue
        key = (study_of.get(row["experiment_id"], "?"), row["strain"], row["value"],
               row["unit"], row["measured_what"], row["day"], row["assay"])
        groups.setdefault(key, []).append(
            f"{row['outcome_id']} ({row['experiment_id']}, {row['source_ref']})")
    problems = []
    for key, rows in sorted(groups.items()):
        if len(rows) < 2:
            continue
        study, strain, value, unit, measured_what, day, assay = key
        problems.append(
            f"{study}: {strain} {value} {unit} {measured_what}"
            + (f", day {day}" if day.strip() else "")
            + f" recorded on {len(rows)} rows: " + ", ".join(rows)
            + "\n-> decide: one cultivation recorded several times (consolidate to "
            "one row), or measured again under conditions these columns do not "
            "show (say which in notes)")
    return problems


def unusual_outcome_counts(experiments, outcomes):
    """Report a study whose outcome row count sits above the usual range.

    Rule 2: more rows is not more value, and a high count usually means
    strains crossed with conditions and measurements, or a duplicated control.
    """
    study_of = dict(zip(experiments["experiment_id"], experiments["study_id"]))
    counts = {}
    for experiment in outcomes["experiment_id"]:
        if experiment in study_of:
            counts[study_of[experiment]] = counts.get(study_of[experiment], 0) + 1
    low, high = USUAL_OUTCOME_ROWS
    return [
        f"{study} has {count} outcome rows; papers here run about {low} to {high}"
        "\n-> decide: confirm the paper really reports this many distinct "
        "measurements, or look for conditions crossed with strains and a control "
        "counted more than once"
        for study, count in sorted(counts.items())
        if count > high
    ]


def main(strict=False):
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

    errors = [
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
                         "'{}' does not exist", "gene_name")),
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

        (f"experiments.csv: {EDITED_GENES} agrees with experiment_genes.csv",
            matches_gene_rows(experiments, genes)),
    ]

    warnings = [
        ("experiments.csv: host_effect is a declared vocabulary value",
            undeclared_terms(experiments, "host_effect", "experiment_id")),
        ("experiment_genes.csv: gene_role is a declared vocabulary value",
            undeclared_terms(genes, "gene_role", "gene_name")),
        ("experiment_genes.csv: edit_type is a declared vocabulary value",
            undeclared_terms(genes, "edit_type", "gene_name")),

        ("outcomes.csv: every curated study has a control measurement",
            studies_without_a_control(experiments, outcomes)),
        ("outcomes.csv: no control measurement is recorded twice",
            duplicated_control_measurements(outcomes, experiments)),
        ("studies.csv: outcome row count per study is in the usual range",
            unusual_outcome_counts(experiments, outcomes)),
    ]

    print("ERRORS - the data is broken and must be fixed\n")
    report(errors, "FAIL")
    print("\nWARNINGS - a human decision is needed; these do not fail the run\n")
    report(warnings, "WARN")

    error_count = sum(len(problems) for _, problems in errors)
    warning_count = sum(len(problems) for _, problems in warnings)
    checked = len(errors) + len(warnings)
    print(f"\n  {checked} checks run: {len(errors)} error, {len(warnings)} warning")
    print(f"\n  {count(error_count, 'error')}, {count(warning_count, 'warning')}.")

    if error_count:
        print("\nFAILED - fix the errors above.")
        return 1
    if warning_count and strict:
        print("\nFAILED - warnings count as errors under --strict.")
        return 1
    if warning_count:
        print("\nPASSED - the tables are structurally sound. Read the warnings.")
        return 0
    print("\nPASSED - the tables are structurally sound.")
    return 0


if __name__ == "__main__":
    sys.exit(main("--strict" in sys.argv[1:]))
