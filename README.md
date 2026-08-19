# aoryzae-secretion-benchmark

A curated dataset of published Aspergillus oryzae secretion-engineering experiments. Describes gene changes with measured protein-yield outcomes. Used for validating metabolic and secretion models.

## Layout

```
data/
  studies.csv          study_id
  experiments.csv      experiment_id, study_id, cargo_protein, cargo_uniprot
  experiment_genes.csv experiment_id, gene_symbol, locus_tag
  outcomes.csv         outcome_id, experiment_id
scripts/
notebooks/
README.md
```

## What's in data/

Each row follows a chain: a paper reports an experiment, the experiment changed some genes, and the experiment produced results.

- **[studies.csv](data/studies.csv):** One row per published paper the data comes from.
- **[experiments.csv](data/experiments.csv):** One row per comparison: researchers modified the fungus and measured it against an unmodified control. Also records which protein they were trying to produce and how that was set up.
- **[experiment_genes.csv](data/experiment_genes.csv):** Which genes were changed in each experiment. A separate file because one experiment can change many genes at once.
- **[outcomes.csv](data/outcomes.csv):** What was measured. A separate file because one experiment usually reports several things: protein yield, growth rate, side effects.

Right now these files only have headers: columns get filled in as papers are curated.
