# aoryzae-secretion-benchmark

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22288125.svg)](https://doi.org/10.5281/zenodo.22288125)

A curated dataset of published *Aspergillus oryzae* secretion-engineering experiments, pairing genetic interventions with measured protein-production outcomes for benchmarking secretion-aware and strain-engineering models.

## What this is, for anyone arriving cold

*Aspergillus oryzae* is a filamentous fungus, the mold used for centuries to make sake, soy sauce, and miso. Industrially it matters because it is very good at **secretion**: pushing proteins it makes out through its cell wall into the surrounding liquid, where they can simply be collected. That makes it a host for producing useful proteins (enzymes, or a drug protein) by inserting the gene for a foreign protein and letting the fungus manufacture and export it.

The catch is that the fungus is good at secreting *its own* proteins, not yours. A foreign protein moving through the secretory pathway can be chewed up by the fungus's proteases, misrouted to the vacuole (the cell's waste compartment) and destroyed, or stall because the cell cannot fold that much of it correctly. So researchers **engineer the host**: delete a protease, shut off a disposal route, alter how the product gene is expressed, then measure whether more protein comes out.

This dataset collects those experiments from the published literature. Each one pairs a genetic change with the production number it produced, and with the unmodified strain that number should be compared against. Two things make it usable as a benchmark: every number is traceable to the exact figure or table it came from, and the costs are recorded alongside the gains, because an edit that doubles yield while crippling the fungus is not a win.

A few terms used throughout:

- **Cargo**: the protein you are trying to produce and secrete. Standard usage for anything moved through the secretory pathway. Chymosin (the milk-clotting enzyme in cheesemaking) and human lysozyme are the cargoes here.
- **Strain**: one specific fungal line with a specific set of genetic changes, with a name given by the lab that built it (`SlD-AKC1`).
- **Control strain**: the comparison strain, carrying the cargo but not the genetic change being tested. Without it a production number means nothing.
- **Disruption / deletion**: breaking a gene so it no longer works.
- **Promoter**: the DNA switch in front of a gene that controls when and how much it is expressed. Swapping in a different promoter leaves the gene intact but puts it under new control, which is how researchers turn a gene down without removing it.
- **Conidia**: the fungus's spores. They matter commercially because they are how a large culture is inoculated, so an edit that ruins spore formation is expensive even if yield rises.

### How the four tables fit together

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

One row per experiment, where an experiment is **one intervention × one cargo × one control × one growth condition**. Change any of the four and it is a different experiment. Building the same strain twice is not a second experiment: labs often make several independent transformants of the identical edit to check the result is not an artifact of where the DNA landed, and those are extra rows in `outcomes.csv`, told apart by `strain`.

| Column | Meaning |
| --- | --- |
| `experiment_id` | Unique identifier for the experiment. |
| `study_id` | Study that reports the experiment. |
| `edited_parent_strain` | The strain that the modified production strain was built directly from. Strains are constructed in lineages, each edit made on top of an earlier strain, so this records the immediate predecessor rather than the original wild isolate. |
| `control_strain` | The strain the modified one was measured against. |
| `cargo` | The protein the fungus was engineered to produce and secrete ("cargo" is standard usage for anything moved through the secretory pathway). |
| `construct` | The DNA design used to express the cargo, written as the paper writes it. It names the parts stitched together: the promoter driving expression, any carrier protein the cargo is fused to (a trick that improves secretion), the cleavage site where the cargo is cut free from that carrier, the terminator ending transcription, and the marker used to select successful transformants. Typically identical across every experiment in one study, since only the host genes are varied. |
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

Where categories overlap, classify by what was changed, not the downstream effect: deleting a regulator that controls many protease genes is `target_regulator`, not `remove_protease`. New values get added as papers require them.

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

In any cell, across all four files: `TODO` means not yet checked against the paper, `not_reported` means checked and the paper does not give it, and blank means the field does not apply.

Strain names repeat across studies from the same lab (`SlD-AKC1` appears in both `ZHU2012` and `YOON2010` with different values), so group by `experiment_id`, never by `strain` alone.

Both assays so far (`milk-clotting assay` for chymosin, `lysozyme activity assay` for lysozyme) measure what the protein *does* and convert that to a concentration. Activity counts only protein that folded correctly, so a `mg/L` from activity is not interchangeable with one measured by mass, so check `assay` before comparing across studies. (`JIN2007` converted using the activity of pure human lysozyme, 100,000 U/mg.)

### IDs

| ID | Format | Example |
| --- | --- | --- |
| `study_id` | `{FIRSTAUTHOR}{YEAR}`, uppercase | `ZHU2012` |
| `experiment_id` | `{study_id}_{SHORTLABEL}` | `ZHU2012_CHY` |
| `outcome_id` | `{study_id}_{3-digit sequence}` | `ZHU2012_001` |

IDs are lookup keys, not descriptions. `experiments.csv` holds the real account of what an experiment was. `SHORTLABEL` names whatever a given study varies, so it means nothing outside that study: the cargo in `ZHU2012_CHY`, the gene in `JIN2007_PEPA` (both genes joined for a double knockout, `JIN2007_TPPA_PEPE`), and gene plus edit type in `YOON2013`, which tests four genes both deleted and switchable (`YOON2013_AOATG1_DELETED`, `YOON2013_AOATG1_REPRESSIBLE`).

Two studies sharing first author and year get a suffix (`NEMOTO2009RNAI` vs. `NEMOTO2009AUT`). A `study_id` may be a placeholder until the citation is confirmed; renaming one means updating every dependent row in the other three files.

## Adding a paper

- **Record what is on the page**, not what the authors seem to mean. If a paper contradicts itself, record both versions and note the conflict rather than picking one.
- **Every outcome row needs a `source_ref`**: the figure, table, or section the number came from, so anyone can check it.
- **A row needs something to compare against.** A number from a named strain plus a control to read it against. Unquantified observations ("grew normally", sporulation with no counts) have no value, unit, or control, so they form no row. If they report an effect on the organism, they go in the experiment's `notes`. The test is whether the paper measured against a control, not whether the finding matters.
- **`notes` holds two things:** what a reader needs to interpret the numbers (what a value can and cannot be compared against, unverified strain or construct details, contradictions in the source, evidence bearing on why a yield moved) and any reported effect on the organism, quantified or not. Facts already in another column stay out.
- **Results the paper cites from elsewhere** get no row. Curate from the original paper or skip it.

## Exploring the data

`notebooks/explore.ipynb` is a read-only tour of the four tables: what the field has tried, whether a gene has been knocked out before, experiments that changed more than one gene, and effect sizes by strategy. It also spells out what the dataset cannot answer yet. Needs pandas.

## Validating the data

`python scripts/validate_data.py` checks that:

- IDs are unique within each file
- references between files point at rows that exist
- `source_ref` and `arm` are filled in on every outcome row
- every experiment has at least one gene row and one outcome row

## License

The data is released under [CC0 1.0 Universal](LICENSE): it is factual information taken from published papers, free for anyone to use for any purpose. Please cite the original papers, which are all listed in `studies.csv`.
