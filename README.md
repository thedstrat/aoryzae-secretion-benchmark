# aoryzae-secretion-benchmark

A curated dataset of published *Aspergillus oryzae* secretion-engineering experiments — gene changes paired with measured protein-yield outcomes. Used for validating metabolic and secretion models.

## What's in data/

The `data/` directory contains four CSV tables. They are currently headers only; rows are added as papers are curated.

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
| `evidence_type` | Whether the experiment validates production (`production`) or supports a mechanism (`mechanism`). |
| `modified_background` | Starting biological strain or background that was modified. |
| `control_strain` | Strain used as the comparison control. |
| `cargo` | Protein or other product the experiment aims to produce or secrete. |
| `construct` | Genetic construct used to express the cargo. |
| `conditions` | Culture setup as one readable string: medium, pH, volume, temperature, inoculum, and duration. |
| `notes` | Relevant experiment details that do not fit another column. |

### `experiment_genes.csv`

One row per gene edit in an experiment; an experiment with several edited genes has several rows.

| Column | Meaning |
| --- | --- |
| `experiment_id` | Experiment in which the gene was edited. |
| `gene_id` | Stable identifier for the edited gene. |
| `gene_name` | Readable name or symbol for the edited gene. |
| `edit_type` | Kind of genetic change, such as deletion or overexpression. |
| `edit_detail` | Additional detail about how the gene was changed. |

### `outcomes.csv`

One row per measured result for one experimental arm or strain.

| Column | Meaning |
| --- | --- |
| `outcome_id` | Unique identifier for the outcome row. |
| `experiment_id` | Experiment that produced the outcome. |
| `arm` | Experimental or control group represented by the result. |
| `strain` | Specific strain or independent transformant measured. |
| `metric` | Quantity that was measured. |
| `value` | Reported numeric or textual result. |
| `unit` | Unit of the reported value. |
| `fold_vs_control` | Result expressed as a fold change relative to the control. |
| `day` | Culture or measurement day. |
| `method` | Method used to obtain the measurement. |
| `source_ref` | Figure, table, or section from which the value came; required for every outcome row. |
| `notes` | Relevant outcome details that do not fit another column. |

### Experiment grain

One experiment is one intervention × cargo × control × culture condition. Independent transformants of the same intervention are separate rows in `outcomes.csv`, distinguished by `strain`; they are never separate experiments.

### Data conventions

- `TODO` means the value has not yet been checked against the paper.
- `not_reported` means the paper was checked and does not provide the value.
- A blank value means the field genuinely does not apply.
- `notes` holds nuance that does not fit another column.
- `source_ref` identifies the figure, table, or section that supplied a value and is required on every outcome row.
- `conditions` is one human-readable string containing medium, pH, volume, temperature, inoculum, and duration; these details are deliberately not split into separate columns at this dataset's current size.
- `evidence_type` distinguishes production-validation experiments from supporting mechanistic experiments. Current values are `production` and `mechanism`.
