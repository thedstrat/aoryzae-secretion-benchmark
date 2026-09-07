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
| `edited_parent_strain` | The immediate parental strain from which the modified production strain was constructed. |
| `control_strain` | The strain the modified one was measured against. |
| `cargo` | The protein the fungus was engineered to produce and secrete ("cargo" is standard usage for anything moved through the secretory pathway). |
| `construct` | The DNA design used to express the cargo — promoter, carrier fusion, cleavage site, terminator, marker. |
| `conditions` | Culture setup as one readable string; format defined below. |
| `notes` | Two things: caveats a reader needs to interpret the numbers correctly, and any reported effect on the organism itself (growth, spore formation, shape). The second matters because an intervention that raises yield while harming the organism is not a free win. |

### `experiment_genes.csv`

One row per gene edit in an experiment; an experiment with several edited genes has several rows.

| Column | Meaning |
| --- | --- |
| `experiment_id` | Experiment in which the gene was edited. |
| `gene_id` | Stable identifier for the edited gene. |
| `gene_name` | Readable name or symbol for the edited gene. |
| `gene_role` | Why the researchers touched this gene — the strategy the edit belongs to. Values below. |
| `edit_type` | The kind of edit, using the paper's own term. Values so far: `disruption`, `promoter_replacement` — the gene is left intact but its native promoter is swapped for another, so expression can be controlled rather than removed. Others (`deletion`, `knockdown`, `overexpression`) will be added as papers require them. |
| `edit_notation` | The genetic change written exactly as the paper reported it, e.g. `ΔAosedD::pyrG`. |

The `gene_role` values:

| Value | Meaning |
| --- | --- |
| `remove_protease` | Delete enzymes that chew up the product. |
| `fix_misrouting` | Stop the product being sent to the vacuole for disposal. |
| `block_autophagy` | Shut down autophagy, the cell's bulk recycling route, which delivers misfolded secretory proteins from the ER to the vacuole for destruction. |
| `reduce_competition` | Make less of the fungus's own secreted protein, so more capacity is free for the product. |
| `improve_folding` | Help the cell fold the extra protein correctly, or handle the stress when it can't. |
| `change_shape` | Alter hyphal shape, branching, cell wall, or broth thickness. |
| `target_regulator` | Hit one controller gene that turns many genes up or down at once, instead of editing them individually. |
| `design_the_construct` | Change how the product gene is expressed — promoter, signal peptide, carrier fusion, insertion site — rather than editing a host gene. |
| `unknown` | Found by screening or mutagenesis; the mechanism is not established. |

`block_autophagy` is distinct from `fix_misrouting`: that value covers receptor-mediated sorting of correctly folded cargo, while this one covers bulk degradation of protein the cell has judged defective. Different mechanism, different genes, different tradeoffs — losing autophagy impairs conidiation.

`gene_role` is the one field in this dataset that is our judgment rather than a transcription from the paper. The papers do not label their work this way. The categories exist so the dataset can be grouped by what kind of thing was tried, which is what makes it possible to see what the field has and has not attempted.

Categories can overlap, so the tiebreak is: classify by what was changed, not by the downstream effect. Deleting a regulator that controls many protease genes is `target_regulator`, not `remove_protease`, because the strategy is to hit one controller rather than the proteases themselves.

`design_the_construct` is the odd one out: those experiments change the product's own DNA design rather than editing a host gene, so some may have no rows in this file at all.

Anyone who disagrees with a classification can ignore this column without affecting anything else in the dataset. New values will be added as papers require them.

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

Both are activity assays, so a yield in `mg/L` is derived from measured activity rather than weighed directly. `JIN2007` assayed lysozyme activity against *M. lysodeikticus* and converted to `mg/L` using the specific activity of authentic human lysozyme (100,000 U/mg). Conversion details belong here, not repeated in every row's `assay` value.

### Scope rule: outcomes vs. experiment notes

`outcomes.csv` holds **paired measurements**: a value produced by a named strain, with a control to compare against. Yield, activity, spore counts, and other quantified results belong here.

Unquantified observations form no rows. "Grew normally", "impaired sporulation with no counts given", and similar statements have no value, no unit, and no control measurement, so there is nothing to put in a row. Where such an observation reports an effect on the organism itself, it goes in the relevant experiment's `notes` instead.

The test is whether the paper measured something against a control, not whether the finding matters.

An **experiment note** (the `notes` column in `experiments.csv`) covers two things. The first is what a reader needs in order to interpret those numbers correctly: what a value can and cannot be compared against, unverified aspects of the strain or construct, inconsistencies in the source paper, and evidence bearing on how an outcome should be read — an enzyme activity assay that explains why a yield rose or fell, for instance. The second is any reported effect on the organism itself — growth, spore formation, shape — whether or not the paper attached a number to it. Facts already carried by another column stay out, and so does general background such as replication counts.

Among rows that do qualify for `outcomes.csv`, there is no separate column distinguishing benchmarkable outcomes from side effects. `measured_what` already does that: a computational user filters to the metrics their model predicts, while a human reads the full set and sees both what an edit gained and what it cost.

### Experiment grain

One experiment is one intervention × cargo × control × culture condition. Independent transformants of the same intervention are separate rows in `outcomes.csv`, distinguished by `strain`; they are never separate experiments.

### ID conventions

| ID | Format | Example |
| --- | --- | --- |
| `study_id` | `{FIRSTAUTHOR}{YEAR}`, uppercase | `ZHU2012` |
| `experiment_id` | `{study_id}_{SHORTLABEL}` | `ZHU2012_CHY` |
| `outcome_id` | `{study_id}_{3-digit sequence}` | `ZHU2012_001` |

`SHORTLABEL` names whatever distinguishes the experiments within one study, so it varies by study rather than drawing on a fixed vocabulary. `ZHU2012` and `YOON2010` each test one gene against two cargoes, so the label is the cargo (`ZHU2012_CHY`, `ZHU2012_HLY`). `JIN2007` tests one cargo against several genes, so the label is the gene (`JIN2007_PEPA`), with both genes joined for a double disruptant (`JIN2007_TPPA_PEPE`). `YOON2013` varies gene and intervention together — four of its genes are both disrupted and placed under a repressible promoter — so the gene alone is not unique and the label carries both (`YOON2013_AOATG1_DEL`, `YOON2013_AOATG1_REPRESS`).

A label is therefore only meaningful within its own study. Like `outcome_id`, an `experiment_id` is a key rather than a description; `experiments.csv` holds the authoritative account of what an experiment is.

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

### What earns a place in the experiment's notes

The `notes` field on the experiment holds two kinds of thing: caveats a reader needs in order to interpret the numbers correctly, and any reported effect on the organism itself.

- **What a value can be compared against** — an unverified cargo copy number, or a control strain carrying none of the deletions the fold-change is being credited to.
- **Problems in the source** — a figure that names its own control strain two different ways.
- **Evidence that changes how an outcome reads** — a protease assay explaining why a yield fell after day 5, or a condition under which a negative result does not hold.
- **Effects on the organism** — growth, spore formation, shape, whether or not the paper quantified them. "Grew normally" belongs here. An intervention that raises yield while harming the organism is not a free win, so a reader needs to see the cost next to the gain.

Facts already carried by another column stay out, and so does general background such as replication counts. See the scope rule above.

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
