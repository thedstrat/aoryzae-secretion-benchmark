# aoryzae-secretion-benchmark

A curated dataset of published *Aspergillus oryzae* secretion-engineering experiments, pairing genetic interventions with measured protein-production outcomes for benchmarking secretion-aware and strain-engineering models.

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

### `experiments.csv`

One row per experiment, using the grain defined below.

| Column | Meaning |
| --- | --- |
| `experiment_id` | Unique identifier for the experiment. |
| `study_id` | Study that reports the experiment. |
| `modified_background` | The engineered strain the production strains were built from. |
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
| `edit_type` | Normalized category: `disruption`, `deletion`, or `overexpression`. |
| `edit_notation` | The genetic change written exactly as the paper reported it, e.g. `ΔAosedD::pyrG`. |

### `outcomes.csv`

One row per measured result for one experimental arm or strain.

| Column | Meaning |
| --- | --- |
| `outcome_id` | Unique identifier for the outcome row. |
| `experiment_id` | Experiment that produced the outcome. |
| `arm` | Which side of the comparison a measurement came from: `control` or `modified`. |
| `strain` | Specific strain or independent transformant measured. |
| `measured_what` | What was measured or observed, e.g. max chymosin yield, growth phenotype, conidia formation. |
| `value` | Reported numeric or textual result. |
| `unit` | Unit of the reported value. |
| `fold_vs_control` | Result expressed as a fold change relative to the control. |
| `day` | Culture or measurement day. |
| `method` | The assay used to obtain the measurement. Note that activity-based assays measure only correctly folded, functional protein. |
| `source_ref` | Where in the paper the value came from (figure, table, or section); required on every outcome row. |
| `notes` | Relevant outcome details that do not fit another column. |

### Scope rule: outcomes vs. experiment notes

An **outcome row** (in `outcomes.csv`) is an observed consequence of the genetic intervention that affects how useful the engineered strain is — product yield, growth, sporulation, morphology, or another performance tradeoff.

An **experiment note** (the `notes` column in `experiments.csv`) is evidence explaining *why* an effect occurred, or supporting the interpretation of an outcome — enzyme activity assays, protein localization, Western blots confirming identity, or the gene-expression rationale for why a gene was chosen.

There is no separate column distinguishing benchmarkable outcomes from side effects. `measured_what` already does that: a computational user filters to the metrics their model predicts, while a human reads the full set and sees both what an edit gained and what it cost.

### Experiment grain

One experiment is one intervention × cargo × control × culture condition. Independent transformants of the same intervention are separate rows in `outcomes.csv`, distinguished by `strain`; they are never separate experiments.

### ID conventions

| ID | Format | Example |
| --- | --- | --- |
| `study_id` | `{FIRSTAUTHOR}{YEAR}`, uppercase | `ZHU2012` |
| `experiment_id` | `{study_id}_{SHORTLABEL}` | `ZHU2012_CHY` |
| `outcome_id` | `{study_id}_{3-digit sequence}` | `ZHU2012_001` |

`outcome_id` is deliberately sequential and meaningless — meaning lives in `strain` and `measured_what`, which can be corrected without invalidating an ID.

### `conditions` format

One human-readable string, with a fixed field order: medium, pH start (pH end by dN), volume, temperature, inoculum, duration. No tildes. Scientific notation as `2e5` / `1e6`, not exponent notation like `2x10^5`. Use `not_reported` for anything the paper omits.

Example: `5x DPY, pH 5.5 (5.3 by d4), 20 mL, 30C, 2e5 conidia, 3-6 d`

### Data conventions

- `TODO` means the value has not yet been checked against the paper.
- `not_reported` means the paper was checked and does not provide the value.
- A blank value means the field genuinely does not apply.
- `source_ref` identifies the figure, table, or section that supplied a value and is required on every outcome row.
