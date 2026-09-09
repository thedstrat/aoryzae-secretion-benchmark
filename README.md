# aoryzae-secretion-benchmark

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22288125.svg)](https://doi.org/10.5281/zenodo.22288125)

A curated dataset of published *Aspergillus oryzae* secretion-engineering experiments, pairing genetic interventions with measured protein-production outcomes for benchmarking secretion-aware and strain-engineering models.

## Background

*Aspergillus oryzae* is a filamentous fungus, long used to make sake, soy sauce, and miso. It is an industrial host for protein production because it secretes efficiently, exporting proteins through its cell wall into the culture liquid where they can be recovered. Inserting the gene for a foreign protein makes the fungus manufacture and export it.

The difficulty is that the pathway is tuned for the fungus's own proteins. A foreign protein can be degraded by native proteases, misrouted to the vacuole for disposal, or limited by the cell's capacity to fold it. Host engineering addresses this: delete a protease, shut off a degradation route, change how the product gene is expressed, then measure the effect on yield.

This dataset collects those experiments from the literature, pairing each genetic change with its measured production outcome and the control strain that outcome should be read against. The protein being produced is referred to throughout as the **cargo**, standard usage for anything moved through the secretory pathway; the cargoes here are chymosin and human lysozyme. Every value is traceable to the figure or table it came from, and effects on the organism are recorded alongside yield, since an edit that raises production while impairing growth or sporulation carries a real cost.

### Table structure

```
studies.csv                 one row per published paper
└── experiments.csv         one row per experiment in that paper
    ├── experiment_genes.csv    which genes it changed, and how
    └── outcomes.csv            one row per measurement
```

Each level joins to the one above it by ID: an experiment names its `study_id`, and gene and outcome rows name their `experiment_id`.

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
| `pdf_url` | Direct link to the article PDF, where a stable official publisher or repository link exists. |

### `experiments.csv`

One row per experiment. An experiment is one comparison: a genetic change, tested with one cargo, against one control strain, under one set of growth conditions. Change any of those four and it is a separate experiment.

Repeating the same comparison is not. Labs usually build several strains carrying the identical edit and measure each, to confirm a result is not an accident of where the DNA inserted. Those are multiple rows in `outcomes.csv` under one experiment, told apart by `strain`.

| Column | Meaning |
| --- | --- |
| `experiment_id` | Unique identifier for the experiment. |
| `study_id` | Study that reports the experiment. |
| `edited_parent_strain` | The strain that the modified production strain was built directly from. Strains are constructed in lineages, each edit made on top of an earlier strain, so this records the immediate predecessor rather than the original wild isolate. |
| `control_strain` | The strain the modified one was measured against. |
| `cargo` | The protein the fungus was engineered to produce and secrete ("cargo" is standard usage for anything moved through the secretory pathway). |
| `construct` | The DNA design used to express the cargo, written as the paper writes it: the promoter, any carrier protein the cargo is fused to, the cleavage site, the terminator, and the selection marker. |
| `conditions` | How the fungus was grown, one string in fixed order: medium, starting pH (with the pH it drifted to, if reported), volume, temperature, inoculum, duration. Production numbers only compare between strains grown the same way. `5x DPY, pH 5.5 (5.3 by d4), 20 mL, 30C, 2e5 conidia, 3-6 d` reads as: five-times-strength DPY broth, pH 5.5 falling to 5.3 by day 4, 20 mL, 30 degrees C, inoculated with 200,000 spores, sampled days 3-6. |
| `notes` | Two things: caveats a reader needs to interpret the numbers correctly, and any reported effect on the organism itself (growth, spore formation, shape). The second matters because an intervention that raises yield while harming the organism is not a free win. |

Reading one row: `JIN2007_TPPA_PEPE` expressed human lysozyme in strain `NA-2L-peE10`, measured against control `N-2L`. Both strains carry the same cargo construct and were grown the same way, so the difference between them is attributable to the gene edits, which are listed in `experiment_genes.csv`.

### `experiment_genes.csv`

One row per gene edit in an experiment; an experiment with several edited genes has several rows.

| Column | Meaning |
| --- | --- |
| `experiment_id` | Experiment in which the gene was edited. |
| `gene_id` | Stable database identifier for the gene, which stays valid even if naming conventions change. `TODO` where it has not been looked up yet. |
| `gene_name` | The name the paper uses for the gene, e.g. `Aoatg1`. |
| `gene_role` | Why the researchers touched this gene: the strategy the edit belongs to. Values below. |
| `edit_type` | The kind of edit, using the paper's own term. Values so far: `disruption`, the gene is broken so it no longer functions; `promoter_replacement`, the gene is left intact but its native promoter is swapped for another, so its expression can be controlled rather than removed. Others (`deletion`, `knockdown`, `overexpression`) will be added as papers require them. |
| `edit_notation` | The genetic change written exactly as the paper reported it, e.g. `ΔAosedD::pyrG`. By convention Δ means the gene was removed or broken, and `::` introduces what was put in its place, usually a marker gene used to confirm the edit worked. |

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
| `design_the_construct` | Change how the product gene is expressed (promoter, signal peptide, carrier fusion, insertion site) rather than editing a host gene. |
| `unknown` | Found by screening or mutagenesis; the mechanism is not established. |

Reading one row: `JIN2007_TPPA_PEPE | AO090011000235 | tppA | remove_protease | disruption | ΔtppA::argB` says that experiment broke the protease gene `tppA`, replacing it with the `argB` marker. That experiment has a second row for `pepE`, because both genes were disrupted in the same strain and measured together.

`gene_role` is the only field here that is our judgment rather than a transcription. The papers do not label their work this way. It exists so the dataset can be grouped by what kind of thing was tried, showing what the field has and has not attempted. Ignore the column if you disagree with a call; nothing else depends on it.

### `outcomes.csv`

One row per measured result for one experimental arm or strain.

| Column | Meaning |
| --- | --- |
| `outcome_id` | Unique per row, formatted `{study_id}_{3-digit sequence}`. |
| `experiment_id` | Which experiment this measurement belongs to. |
| `strain` | The exact strain that produced this measurement. |
| `arm` | Which side of the comparison this row is: `control` (the unedited reference strain) or `modified` (the strain carrying the edit). |
| `value` | The number reported. |
| `unit` | What the number is measured in. |
| `measured_what` | What this row measured: secreted yield, growth, broth viscosity, spore formation. Free text rather than a fixed vocabulary, because papers measure different things; it is also what you filter on to separate the production result from the side effects. |
| `vs_control` | How this value compares to its control, as a multiple. `2.9x` means 2.9 times what the control produced; the control's own row is `1.0x` by definition. This is the column most benchmarks care about, since fold-change over control survives differences in assay and culture setup better than raw values do. |
| `day` | Timepoint the value was taken at. |
| `assay` | The method used. Activity-based assays measure only correctly folded, functional protein, so a mg/L value derived from activity is not directly comparable to one measured by mass. |
| `source_ref` | The figure, table, or section the value came from. Required on every row. |
| `notes` | Caveats needed to read the value correctly. |

Reading one row: `78.0 | mg/L | Highest secreted CHY yield reported | 2.9x` means the strain reached a maximum chymosin yield of 78.0 mg/L, 2.9 times what its control produced.

One row = one measurement. A strain with both a yield and a growth measurement gets two rows, distinguished by `measured_what`, never one row holding two values. No column flags which rows are "the result" and which are side effects; `measured_what` already says what each measured.

Both assays so far (`milk-clotting assay` for chymosin, `lysozyme activity assay` for lysozyme) measure what the protein *does* and convert that to a concentration. Activity counts only protein that folded correctly, so a `mg/L` from activity is not interchangeable with one measured by mass. Check `assay` before comparing across studies. (`JIN2007` converted using the activity of pure human lysozyme, 100,000 U/mg.)

### IDs

| ID | Format | Example |
| --- | --- | --- |
| `study_id` | `{FIRSTAUTHOR}{YEAR}`, uppercase | `ZHU2012` |
| `experiment_id` | `{study_id}_{label}` | `ZHU2012_CHY` |
| `outcome_id` | `{study_id}_{3-digit sequence}` | `ZHU2012_001` |

An `experiment_id` is the study name plus a short label, as in `ZHU2012_CHY`. The label means different things in different studies:

| Example | The label names | Because that study varied |
| --- | --- | --- |
| `ZHU2012_CHY` | the cargo (chymosin) | one gene, two cargoes |
| `JIN2007_PEPA` | the gene (`pepA`) | one cargo, several genes |
| `JIN2007_TPPA_PEPE` | both genes, joined | two genes disrupted in one strain |
| `YOON2013_AOATG1_DELETED` | the gene and the edit | four genes, each edited two ways |

`YOON2013` needs both halves because it tested every gene twice. `_DELETED` is the gene removed outright. `_REPRESSIBLE` leaves the gene in place but swaps its promoter for one that shuts off when thiamine is added, so expression can be turned down instead of eliminated. The authors did this because deleting these genes raised chymosin yield but severely impaired spore formation; the switchable version was built to recover sporulation, which it did for some of the four genes better than others.

## Ingestion notes

The rules followed when curating a paper into these tables. They are worth reading before using the data, since they determine what is present and what is deliberately absent.

- **Record what the paper says**, not what the authors appear to mean. Where a paper contradicts itself, both versions are recorded and the conflict noted rather than resolved by guesswork.
- **Every number cites its source.** Each outcome row names the figure, table, or section it came from, so any value can be checked against the paper.
- **A measurement needs a comparison to earn a row.** A number from a named strain, plus a control to read it against. Statements with no number ("grew normally", impaired sporulation with no counts) cannot form a row, so where they describe an effect on the organism they go in the experiment's `notes` instead. The test is whether the paper measured against a control, not whether the finding is interesting.
- **`notes` carries the caveats.** What a value can and cannot be compared against, unverified strain or construct details, contradictions in the source, evidence explaining why a yield moved, and any reported effect on the organism. Facts already held in another column are not repeated here.
- **Results a paper cites from elsewhere get no row.** They are curated from the original publication or skipped, so that every value traces to the paper that reported it.

## Notebooks: explore the data

`notebooks/explore.ipynb` is a read-only tour of the four tables: what the field has tried, whether a gene has been knocked out before, experiments that changed more than one gene, and effect sizes by strategy. It also spells out what the dataset cannot answer yet. Needs pandas.

## Validating the data

`python scripts/validate_data.py` checks that:

- IDs are unique within each file
- references between files point at rows that exist
- `source_ref` and `arm` are filled in on every outcome row
- every experiment has at least one gene row and one outcome row

## Citation

If you use this dataset, please cite it:

> Delistraty, J. (2026). A. oryzae secretion-engineering benchmark (v0.2.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22288125

Please also cite the original papers the data comes from. They are listed with DOIs in `data/studies.csv`.

## License

The data is released under [CC0 1.0 Universal](LICENSE): it is factual information taken from published papers, free for anyone to use for any purpose. Please cite the original papers, which are all listed in `studies.csv`.
