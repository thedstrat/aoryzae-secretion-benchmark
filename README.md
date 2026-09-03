# aoryzae-secretion-benchmark

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22288125.svg)](https://doi.org/10.5281/zenodo.22288125)

A curated dataset of published *Aspergillus oryzae* secretion-engineering experiments, pairing genetic interventions with measured protein-production outcomes for benchmarking secretion-aware and strain-engineering models.

## Citation

If you use this dataset, please cite it:

> Delistraty, J. (2026). A. oryzae secretion-engineering benchmark (v0.2.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22288125

Please also cite the original papers the data comes from. They are listed with DOIs in `data/studies.csv`.

## What's in data/

The `data/` directory contains four CSV tables, populated incrementally as papers are curated.

### `studies.csv`

One row per published paper.

| Column | Meaning |
| --- | --- |
| `study_id` | Unique identifier for the study. |
| `authors` | Paper authors. |
| `year` | Publication year. |
| `title` | Paper title. |
| `journal` | Journal that published the paper. |
| `doi` | Digital Object Identifier for the paper. |
| `pmid` | PubMed identifier for the paper. |
| `pdf_url` | Direct link to the article PDF when a stable official publisher or repository link is available. This is a convenience field; `doi` remains the canonical reference. May be blank or require publisher access. |

Only official publisher or repository links (e.g. the publisher's own site, PMC, J-STAGE) belong in `pdf_url`. Unofficial mirrors such as ResearchGate or Sci-Hub, and local file paths, are not used.

### `experiments.csv`

One row per experiment, using the grain defined below.

| Column | Meaning |
| --- | --- |
| `experiment_id` | Unique identifier for the experiment. |
| `study_id` | Study that reports the experiment. |
| `edited_parent_strain` | The genetically edited parent strain used to create the measured production strains. |
| `control_strain` | The strain the modified one was measured against. |
| `cargo` | The protein the fungus was engineered to produce and secrete ("cargo" is standard usage for anything moved through the secretory pathway). |
| `construct` | The DNA design used to express the cargo — promoter, carrier fusion, cleavage site, terminator, marker. |
| `conditions` | Culture setup as one readable string; format defined below. |
| `notes` | Evidence explaining why an effect occurred, or supporting the interpretation of an outcome — see the scope rule below. |

### `experiment_genes.csv`

One row per gene edit in an experiment; an experiment with several edited genes has several rows.

| Column | Meaning |
| --- | --- |
| `experiment_id` | Experiment in which the gene was edited. |
| `gene_id` | Stable identifier for the edited gene. |
| `gene_name` | Readable name or symbol for the edited gene. |
| `edit_type` | The kind of edit, using the paper's own term. Values so far: `disruption`. Others (`deletion`, `knockdown`, `overexpression`) will be added as papers require them. |
| `edit_notation` | The genetic change written exactly as the paper reported it, e.g. `ΔAosedD::pyrG`. |

### `outcomes.csv`

One row per measured result for one experimental arm or strain.

| Column | Meaning |
| --- | --- |
| `outcome_id` | Unique per row, formatted `{study_id}_{3-digit sequence}`. |
| `experiment_id` | Which experiment this measurement belongs to. |
| `strain` | The exact strain that produced this measurement. |
| `arm` | Which side of the comparison: `control` or `modified`. |
| `value` | The number reported. |
| `unit` | What the number is measured in. |
| `measured_what` | What was measured, e.g. `Highest secreted CHY yield reported`, growth, broth viscosity, conidia formation. |
| `vs_control` | How this compares to its control. For example, `2.9x` means 2.9 times the control; the control itself is `1.0x`. |
| `day` | Timepoint the value was taken at. |
| `assay` | The method used. Activity-based assays measure only correctly folded, functional protein, so a mg/L value derived from activity is not directly comparable to one measured by mass. |
| `source_ref` | The figure, table, or section the value came from. Required on every row. |
| `notes` | Caveats needed to read the value correctly. |

Reading one row: `78.0 | mg/L | Highest secreted CHY yield reported | 2.9x` means the strain reached a maximum chymosin yield of 78.0 mg/L, which is 2.9 times the amount produced by its control strain.

One row = one measurement. A strain with both a yield and a growth measurement gets two rows, distinguished by `measured_what` — never one row holding two values.

Strain names repeat across studies from the same lab. `SlD-AKC1` appears in both `ZHU2012` and `YOON2010` with different reported values (27.3 and 28.7 mg/L). Always group by `experiment_id`, not by strain alone.

The two assays used so far:

- `milk-clotting assay` — measures functional chymosin by testing how well the culture liquid clots milk.
- `lysozyme activity assay` — measures functional lysozyme by testing how well the culture liquid breaks down bacterial cells.

### Scope rule: outcomes vs. experiment notes

`outcomes.csv` holds **paired measurements**: a value produced by a named strain, with a control to compare against. Yield, activity, spore counts, and other quantified results belong here.

Unquantified observations go in the relevant experiment's `notes`. "Grew normally", "impaired sporulation with no counts given", and similar statements are real findings but have no value, no unit, and no control measurement, so they do not form rows.

The test is whether the paper measured something against a control, not whether the finding matters.

An **experiment note** (the `notes` column in `experiments.csv`) also covers evidence explaining *why* an effect occurred, or supporting the interpretation of an outcome — enzyme activity assays, protein localization, Western blots confirming identity, or the gene-expression rationale for why a gene was chosen.

Among rows that do qualify for `outcomes.csv`, there is no separate column distinguishing benchmarkable outcomes from side effects. `measured_what` already does that: a computational user filters to the metrics their model predicts, while a human reads the full set and sees both what an edit gained and what it cost.

### Experiment grain

One experiment is one intervention × cargo × control × culture condition. Independent transformants of the same intervention are separate rows in `outcomes.csv`, distinguished by `strain`; they are never separate experiments.

### ID conventions

| ID | Format | Example |
| --- | --- | --- |
| `study_id` | `{FIRSTAUTHOR}{YEAR}`, uppercase | `ZHU2012` |
| `experiment_id` | `{study_id}_{SHORTLABEL}` | `ZHU2012_CHY` |
| `outcome_id` | `{study_id}_{3-digit sequence}` | `ZHU2012_001` |

`outcome_id` is deliberately sequential and meaningless — meaning lives in `strain` and `measured_what`, which can be corrected without invalidating an ID.

When two studies share first author and year, append a short distinguishing suffix to `study_id`, e.g. `NEMOTO2009RNAI` vs. `NEMOTO2009AUT` — two different 2009 papers by the same first author.

A `study_id` may be a placeholder used when the first author isn't yet known, and may be renamed once the citation is confirmed (e.g. `CHSB2003` was renamed to `MULLER2003` once the paper was identified). Renaming a `study_id` requires updating every dependent row in `experiments.csv`, `experiment_genes.csv`, and `outcomes.csv`.

### `conditions` format

One human-readable string, with a fixed field order: medium, pH start (pH end by dN), volume, temperature, inoculum, duration. No tildes. Scientific notation as `2e5` / `1e6`, not exponent notation like `2x10^5`. Use `not_reported` for anything the paper omits.

Example: `5x DPY, pH 5.5 (5.3 by d4), 20 mL, 30C, 2e5 conidia, 3-6 d`

### Data conventions

- `TODO` means the value has not yet been checked against the paper.
- `not_reported` means the paper was checked and does not provide the value.
- A blank value means the field genuinely does not apply.
- `source_ref` identifies the figure, table, or section that supplied a value and is required on every outcome row.

## How papers get curated

Everything you need to add a new paper to the dataset.

### What counts as one experiment

One experiment is **one gene change, tested with one cargo protein, against one control strain, under one set of growth conditions**. Change any one of those four things and you have a second experiment.

Building the same strain twice is not a second experiment. If a paper made two independent transformants carrying the same edit and measured both, that is one experiment with two rows in `outcomes.csv`, told apart by `strain`.

### What earns a row in `outcomes.csv`

A row is a measurement with something to compare it against: a number from a named strain, and a control that number can be read against. No number, or nothing to read it against, means no row.

### Everything else goes in the experiment's notes

The `notes` field on the experiment holds the rest. That covers two kinds of thing:

- **Evidence about why something worked** — protease assays, protein localization, Western blots confirming a protein is what the authors say it is.
- **Observations with no number attached** — "grew normally", or impaired sporulation with no counts given.

These are real findings. They are just not measurements against a control, so they do not become rows.

### Results the paper reports but published elsewhere

Papers often mention results that appeared in some other publication. Those do not get rows here. Go to the original paper and curate the number from there, or skip it.

### What to put in a cell

- `TODO` — not checked against the paper yet.
- `not_reported` — checked, and the paper does not give it.
- Blank — the field does not apply.

### Every outcome needs a source

Every row in `outcomes.csv` needs a `source_ref` pointing at the figure, table, or section the number came from, so anyone can go back and check it.

### Record what the paper says

Write down what is on the page, not what you think the authors meant. If a paper contradicts itself, record both versions and note the conflict rather than picking one.

## Validating the data

`scripts/validate_data.py` checks that the files hold together structurally: IDs are unique within each file, references between files point at rows that exist, `source_ref` and `arm` are filled in on every outcome, and every experiment has at least one gene row and one outcome row.

```
python scripts/validate_data.py
```

It exits non-zero if anything fails. It needs pandas.

The script catches typos and broken links between files. It does not catch wrong biology — that is caught by reading the paper.

## License

The data is released under [CC0 1.0 Universal](LICENSE): it is factual information taken from published papers, free for anyone to use for any purpose. Please cite the original papers, which are all listed in `studies.csv`.
