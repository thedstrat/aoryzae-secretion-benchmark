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
