# A. oryzae secretion benchmark: curation rules

Use these when adding or revising a curated study.

Mechanical conventions (formats, vocabularies, referential integrity) are
enforced by `scripts/validate_data.py`, not restated here. This document
covers judgment only.

---

## Rule 0: read the files first

Do not write a row from memory, from a summary, or from a previous
session. Those have been wrong before and reached the dataset.

Before drafting anything, read and quote back:

- the header row of all four CSVs in `data/`
- every distinct value currently in `arm`, `host_effect`, `gene_role`,
  `edit_type`, `unit`, `measured_what`
- one complete worked example across all four tables

**If you cannot read the repo, stop and say so. Do not output rows.**

Where this document and the files disagree, the files win, including
about this document.

---

## Rule 1: does this paper belong here?

This is a small, trustworthy benchmark of how engineering *A. oryzae*
changes protein production. It is not a catalogue of every interesting
fungal result.

Before curating, answer in writing:

1. What production measurement does this paper report? Name the table or
   figure.
2. Is there a control to read it against?
3. How many rows will be production measurements, and how many will be
   something else?

If the answer to 1 is "none," the paper does not go in the dataset.

Prioritize introduced proteins such as chymosin and human lysozyme.
Native-protein and host measurements (growth, morphology, viscosity,
sporulation) belong in `outcomes` **when the paper also reports
production of an introduced protein**, because an edit that raises
production while impairing the host carries a real cost. They are
context for a production result, not a substitute for one.

Müller 2003 was excluded on that basis: its finding concerns morphology
and viscosity, and native alpha-amylase was roughly unchanged. That is a
scope decision about the paper, not a reason to drop unchanged results
from otherwise eligible experiments (see Rule 10).

---

## Rule 2: size sanity

Existing papers contribute roughly 4 to 11 outcome rows each.

If a draft is far outside that range, stop and explain why before
continuing. More rows is not more value. It usually means strains have
been crossed with conditions and measurements into a combinatorial pile,
or a control measured once has been duplicated.

---

## Rule 3: intervention scope

Host-gene disruptions and deletions are the present priority. The
dataset also contains promoter replacements; do not describe those as
deletions. A study changing only a signal peptide or expression
construct may need a scope decision before inclusion. Never invent a
host-gene edit to satisfy the validator.

---

## The four tables

Confirm column order against the files before editing. There is no
separate constructs table, no `conditions` column in `outcomes`, and no
gene-mapping provenance column.

A row in `studies.csv` does not mean the paper's experiments have been
curated. Check all four tables before adding anything.

---

## Rule 4: generated columns

`experiments.edited_genes_vs_control` is generated from
`experiment_genes.csv`. Never edit it by hand or treat it as a source of
truth. If it disagrees with the gene rows, the gene rows are right and
the column needs regenerating. If a source check shows the gene rows
themselves are wrong, fix those first.

It lists only edits that differ from that experiment's control, not the
strain's full genotype. Yoon 2009's quintuple disruptant shows three
genes because only three differ from its double-disruptant control.

---

## Rule 5: what counts as one experiment

One genetic change, tested with one cargo, against one measured control,
under one set of growth conditions. Change any of those four and it is a
separate experiment.

Two strains carrying the **same** edit are independent isolates, not two
experiments. They become separate `modified` outcome rows under one
experiment, named in the `strain` column. Where the paper gives them
different parent strains, record the actual names rather than
substituting a shared ancestor.

Keep combination edits together. A strain with five deletions is not
five experiments, and its combined effect must not be attributed to any
single deletion.

`experiment_genes` records the genetic differences the comparison
represents, not every deletion both arms inherit. Yoon 2011 compares P7,
P9 and P10 against P5, so its gene rows list only the deletions beyond
the shared P5 background. This is what makes `vs_control` attributable
to the listed genes. For a strain's full genotype, see the source
paper's strain table.

`edited_parent_strain` is the immediate strain the edited strain was
built from. `control_strain` is the strain actually measured against it.
They can differ. Never substitute a better-matched control the authors
did not measure. Note background differences that limit what can be
attributed to the edit.

---

## Rule 6: controlled vocabularies

`arm`, `host_effect`, `gene_role` and `edit_type` use short tokens from
existing vocabularies. **Never prose.**

Use an existing value wherever one fits. If none does, propose a new
one, flag it explicitly in your output, and note that the README
vocabulary table needs a matching line. Add one term rather than
several. A new term is a decision for the maintainer, not something to
slip in.

Two `host_effect` values are easy to confuse:

- `not_reported` — the paper reports no relevant host phenotype. Host
  effects are never inferred.
- `no_reported_defect` — the paper reports normal growth, morphology, or
  another relevant lack of impairment. It does not mean every phenotype
  was tested.

Explanation goes in `experiments.notes`. A numeric host phenotype gets
its own `outcomes` row.

`edit_type`: use `disruption` when a marker cassette is inserted into
the gene, `deletion` only when the coding sequence is removed. A paper's
title saying "deletion" does not settle this; the Methods do. A
repressible gene is still present.

`gene_role` is our interpretation, not necessarily the authors' term.

---

## Rule 7: filling experiments

`cargo` names the produced protein. Do not assume an effect on one cargo
applies to another. A fluorescent reporter is evidence about that
reporter unless another protein was tested too.

`construct` records the reported DNA design: promoter, signal peptide or
carrier, cleavage site, terminator, marker, and whatever else the paper
establishes.

`conditions` follows the existing order: medium, pH, volume,
temperature, inoculum, duration, plus relevant additions such as
thiamine. Keep details already present. Never fill an unreported
condition from a different experiment in the same paper.

---

## Rule 8: gene identifiers

`gene_id` uses a verified *A. oryzae* RIB40 AO090... locus identifier.
Never substitute a protein accession, an ID from another genome, or a
plausible-looking match. Use `TODO` when unresolved; locus tags are
filled in one batch by the maintainer.

`gene_name` and `edit_notation` follow the paper.

Some Yoon 2011 mappings, especially AopepAd, were inferred by matching
published primers rather than stated by the authors. Check those and
make the inference discoverable. There is no provenance column.

---

## Rule 9: recording outcomes

One outcome row is one measurement, for one named strain, at one
timepoint. `measured_what` distinguishes production from growth,
morphology, or other effects.

The core outcome is production of the named protein in the culture
liquid. Preserve what the assay measured. mg/L is a concentration.
FAU/mL is enzyme activity. A fluorescent signal or immunoblot band is
something else again. An activity-derived mg/L is acceptable only when
the authors report it or give the calibration needed to calculate it.
Keep the assay name. **Never invent a conversion to mg/L.**

Format multiples as `1.0x`, `2.4x`. Keep an author-reported fold change
distinct from one calculated off estimated bars. If a reported fold
disagrees with the bars, keep the reported fold and note the
discrepancy. (Yoon 2013 Fig. 4A Aoatg8: reported 2.4x against roughly
2.08x implied by the stored estimates.)

A value read from a figure is an estimate. Check axis, legend, strain,
bar colour, condition and day. Note it, for example "read from Fig. 2,
day-4 bar, not stated in text". Do not call a single day-4 measurement a
maximum across time unless the paper establishes that it is one.

If a value is back-calculated or derived from a stated percentage, say
so briefly in `outcomes.notes` and keep the original location in
`source_ref`. Never present a calculated number as one the authors
printed.

---

## Rule 10: unchanged and negative results

Keep negative, unchanged, mixed and non-significant results wherever
there is a usable measurement. Never label a small numerical difference
an established improvement when the authors describe production as
unchanged. If the authors only say "no significant increase" without a
number, do not invent a measured `1.0x`.

---

## Rule 11: blank versus TODO in outcomes.value

- **`TODO`** — the number is recoverable from the paper but has not been
  extracted yet, such as a figure bar that could be digitized.
- **blank** — the paper gives no actual amount and no valid conversion
  can establish one. Relative band intensity alone does not establish a
  concentration. Add one short note saying so.

Blank describes what the source provides, not a claim the quantity could
never be measured.

Keep `unit` and `vs_control` populated where supported. The unit
identifies the measurement type even when `value` is empty. Use `TODO`
for an unresolved fold change rather than inventing one.

A control's `vs_control` is `1.0x` by definition. Record its actual
value when the source provides one; a relative reporter control can have
a blank value and `1.0x`.

Do not enter `value=100` merely because the control defines 100%, or
`value=0.70` merely because the effect is 0.70x. If there is neither a
usable number nor an interpretable comparison, do not create the row.

---

## Rule 12: shared controls

Record each distinct control measurement once. Several experiments can
name the same `control_strain` and use fold changes against it without a
duplicate outcome row. Add a new control row only when the control was
actually measured again: different conditions, timepoint, or measured
quantity. Never count two records of one cultivation as independent
measurements.

---

## Rule 13: sources and contradictions

Every outcome names its source figure, table or text section in
`source_ref`. Check that the strain, result, timepoint and assay all
come from that source. Distinguish text-stated values from chart
estimates.

A result quoted from an older paper belongs to the original publication,
not the paper repeating it.

Record what the source says, contradictions included. Do not guess which
conflicting strain name, copy count, control or figure is right. Use
`TODO` and explain the conflict briefly in the right notes column. Never
quietly overwrite a non-missing value.

If a paper and a patent describe the same experiment, count it once. A
genuinely different strain, condition or result can be new evidence. A
patent claim, proposed construct or unquantified assertion is not a
measured outcome. `studies.csv` has no patent source type, so flag a
patent-only candidate for a schema decision rather than forcing it into
paper fields.

---

## Rule 14: notes

One short sentence, plain English, for a reader who is not a molecular
biologist. Prefer "actual amount" to "absolute value."

Paper-wide facts go in `studies.notes`. A caveat about one comparison
goes in `experiments.notes`, about one measurement in `outcomes.notes`.
Never repeat the same explanation on every row.

Never reference another row's ID. Never repeat a fact already held in
another column. Keep a note only if removing it would make the number
misleading.

Examples:

- Paper reports a 30% drop; no actual amount given.
- Measured relative to the control; no actual amount given.
- Read from Fig. 2, day-4 bar, not stated in text.

---

## Output format

Do not lead with raw CSV. Output in this order:

1. The Rule 0 read-back.
2. The Rule 1 scope answer.
3. A plain summary: N experiments, N outcome rows, of which N are
   production measurements.
4. Every judgment call made, and every proposed new vocabulary term.
5. Only then, the rows.

---

## Repository workflow

Before editing: inspect the README, all four CSVs, existing rows for the
study, and `git diff`. Preserve unrelated uncommitted work.

After editing: run `python scripts/validate_data.py`, inspect the
changed rows and the diff. A passing validator does not establish that
the science is right. Do not commit or push unless asked.

---

## Known items to review

Review leads from earlier curation. Not verified defects, and not
permission to change historical rows without checking the sources.

- `YOON2011_001` may have taken its control value from Yoon 2009. Check
  against Rule 13.
- Some YOON2013 Fig. 4A notes say "(max)", though that figure shows day
  4 rather than a demonstrated maximum across time.
- Some Hoang control outcomes appear to repeat one measurement under
  different experiment IDs. Check the paper before consolidating.

---

## Failure modes from real sessions

All of these happened, all passed a first review, all reached the repo:

- Wrong column names (`reported_value` for `value`, `edited` for
  `modified`, an invented `integration` column) from working off a chat
  summary instead of the files.
- Four-sentence paragraphs written into `host_effect`.
- `_E1`-style IDs that broke every note cross-reference.
- One control cultivation duplicated across four experiments.
- A paper whose only production result was a null result curated into 28
  rows, 20 of them morphology and viscosity.
- Three new `host_effect` terms invented where one would do.
- Eight `gene_role` values listed from memory when the file had four.

Every one traces to confident output built on a remembered schema.
Rules 0, 1 and 2 exist because of this.
