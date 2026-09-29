#!/usr/bin/env python3
"""Regenerate the edited_genes_vs_control column in experiments.csv.

experiment_genes.csv is the source of truth for gene edits. This script
rewrites experiments.csv so the column restates, one cell per experiment,
the distinct gene_name values that experiment edited relative to its
control - the same set the gene rows already carry, in the order they
first appear there.

A cell reads TODO where the summary cannot be trusted: the experiment has
no gene rows at all, or one of its gene_name values is blank or TODO. An
empty cell would claim the experiment edited nothing, which is a different
statement and never the right one here.

The column is derived, so it is regenerated rather than edited: run this
after changing experiments.csv or experiment_genes.csv.

Usage: python scripts/build_edited_genes.py
"""

import sys
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"

COLUMN = "edited_genes_vs_control"
AFTER = "control_strain"
SEPARATOR = "; "
TODO = "TODO"


def summarise(genes):
    """Map each experiment_id in experiment_genes.csv to its column value.

    Genes are listed once each, in order of first appearance, however many
    edit rows they have; the whole cell becomes TODO if any gene_name under
    that experiment is missing or still TODO.
    """
    listed, incomplete = {}, set()
    for experiment_id, gene_name in zip(genes["experiment_id"], genes["gene_name"]):
        seen = listed.setdefault(experiment_id, [])
        name = gene_name.strip()
        if not name or name == TODO:
            incomplete.add(experiment_id)
        elif name not in seen:
            seen.append(name)
    return {
        experiment_id: TODO if experiment_id in incomplete else SEPARATOR.join(seen)
        for experiment_id, seen in listed.items()
    }


def column_for(experiments, genes):
    """The column's values, one per experiments.csv row, in row order.

    An experiment with no rows at all in experiment_genes.csv gets TODO:
    the edits are unknown, not absent.
    """
    summary = summarise(genes)
    return [summary.get(value, TODO) for value in experiments["experiment_id"]]


def place(experiments, values):
    """Return experiments with the column holding `values`, sitting after AFTER."""
    experiments = experiments.drop(columns=[COLUMN], errors="ignore")
    experiments.insert(list(experiments.columns).index(AFTER) + 1, COLUMN, values)
    return experiments


def main():
    experiments = pd.read_csv(DATA / "experiments.csv", dtype=str, keep_default_na=False)
    genes = pd.read_csv(DATA / "experiment_genes.csv", dtype=str, keep_default_na=False)

    values = column_for(experiments, genes)
    experiments = place(experiments, values)
    experiments.to_csv(DATA / "experiments.csv", index=False, lineterminator="\n")

    print(f"Wrote {COLUMN} for {len(experiments)} experiments in {DATA / 'experiments.csv'}")

    edited = set(genes["experiment_id"])
    todo = [
        (experiment_id, "no rows in experiment_genes.csv" if experiment_id not in edited
         else "a gene_name is missing or TODO")
        for experiment_id, value in zip(experiments["experiment_id"], values)
        if value == TODO
    ]
    if todo:
        print(f"\n  {len(todo)} cell(s) written as TODO:")
        for experiment_id, why in todo:
            print(f"    {experiment_id}: {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
