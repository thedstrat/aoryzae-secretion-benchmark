# aoryzae-secretion-benchmark

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22288125.svg)](https://doi.org/10.5281/zenodo.22288125)

A curated dataset of published *Aspergillus oryzae* secretion-engineering experiments, pairing genetic interventions with measured protein-production outcomes for benchmarking secretion-aware and strain-engineering models.

## Background

*Aspergillus oryzae* is a filamentous fungus, long used to make sake, soy sauce, and miso. It is an industrial host for protein production because it secretes efficiently, exporting proteins through its cell wall into the culture liquid where they can be recovered. Inserting the gene for a foreign protein makes the fungus manufacture and export it.

The difficulty is that the pathway is tuned for the fungus's own proteins. A foreign protein can be degraded by native proteases, misrouted to the vacuole for disposal, or limited by the cell's capacity to fold it. Host engineering addresses this: delete a protease, shut off a degradation route, change how the product gene is expressed, then measure the effect on yield.

This dataset collects those experiments from the literature, pairing each genetic change with its measured production outcome and the control strain that outcome should be read against. Every value is traceable to the figure or table it came from, and effects on the organism are recorded alongside yield, since an edit that raises production while impairing growth or sporulation carries a real cost.

### Terminology

- **Cargo**: the protein being produced and secreted. Standard usage for anything moved through the secretory pathway. The cargoes here are chymosin (the milk-clotting enzyme used in cheesemaking) and human lysozyme.
- **Strain**: a specific fungal line carrying a specific set of genetic changes, named by the lab that built it (`SlD-AKC1`).
- **Control strain**: the reference strain, carrying the cargo but not the genetic change under test.
- **Disruption / deletion**: breaking a gene so it no longer functions.
- **Promoter**: the regulatory DNA in front of a gene controlling when and how much it is expressed. Replacing a promoter leaves the gene intact but under different control, which is how expression is reduced rather than removed.
- **Conidia**: the fungus's spores, and how large cultures are inoculated, so impaired conidiation is an industrial cost.

### Table structure

```
studies.csv          one row per published paper
    |
experiments.csv      one row per experiment in that paper
    |        |         (one gene change x one cargo x one control x one growth condition)
    |        |
    |   experiment_genes.csv   which gene(s) that experiment changed, and how
    |
outcomes.csv         the measured numbers, one row per measurement
```

Everything joins on IDs: an `experiments.csv` row names its `study_id`, and rows in `experiment_genes.csv` and `outcomes.csv` name their `experiment_id`. One experiment usually has several outcome rows: at minimum the modified strain and its control, sometimes more strains or more things measured.

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

One row per experiment, where an experiment is **one intervention × one cargo × one control × one growth condition**. Change any of the four and it is a different experiment. Building the same strain twice is not a second experiment: labs often make several independent transformants of the identical edit to check the result is not an artifact of where the DNA landed, and those are extra rows in `outcomes.csv`, told apart by `strain`.

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
| `experiment_id` | `{study_id}_{SHORTLABEL}` | `ZHU2012_CHY` |
| `outcome_id` | `{study_id}_{3-digit sequence}` | `ZHU2012_001` |

IDs are lookup keys, not descriptions. `experiments.csv` holds the real account of what an experiment was. `SHORTLABEL` names whatever a given study varies, so it means nothing outside that study: the cargo in `ZHU2012_CHY`, the gene in `JIN2007_PEPA` (both genes joined for a double knockout, `JIN2007_TPPA_PEPE`), and gene plus edit type in `YOON2013`, which tests four genes both deleted and switchable (`YOON2013_AOATG1_DELETED`, `YOON2013_AOATG1_REPRESSIBLE`).

Two studies sharing first author and year get a suffix (`NEMOTO2009RNAI` vs. `NEMOTO2009AUT`). A `study_id` may be a placeholder until the citation is confirmed; renaming one means updating every dependent row in the other three files.

## Exploring the data

`notebooks/explore.ipynb` is a read-only tour of the four tables: what the field has tried, whether a gene has been knocked out before, experiments that changed more than one gene, and effect sizes by strategy. It also spells out what the dataset cannot answer yet. Needs pandas.

## Adding a paper

- **Record what is on the page**, not what the authors seem to mean. If a paper contradicts itself, record both versions and note the conflict rather than picking one.
- **Every outcome row needs a `source_ref`**: the figure, table, or section the number came from, so anyone can check it.
- **A row needs something to compare against.** A number from a named strain plus a control to read it against. Unquantified observations ("grew normally", sporulation with no counts) have no value, unit, or control, so they form no row. If they report an effect on the organism, they go in the experiment's `notes`. The test is whether the paper measured against a control, not whether the finding matters.
- **`notes` holds two things:** what a reader needs to interpret the numbers (what a value can and cannot be compared against, unverified strain or construct details, contradictions in the source, evidence bearing on why a yield moved) and any reported effect on the organism, quantified or not. Facts already in another column stay out.
- **Results the paper cites from elsewhere** get no row. Curate from the original paper or skip it.

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
