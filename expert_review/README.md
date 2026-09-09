# Expert review data — double-blind mapping audit (TCM-BO 1.9.17)

This folder contains the **de-identified** primary records of the double-blind
expert review of TCM-BO cross-terminology mappings that is reported in the
accompanying Data Descriptor. It is published so that the inter-rater agreement
statistics reported in the paper can be independently recomputed.

## Contents

| File | Sheets | Rows | Description |
|---|---|---|---|
| `kappa_ratings_double_blind_318.xlsx` | `kappa评审表`, `填写说明`, `抽样框统计` | 318 | The two raters' independent verdicts for each sampled mapping. This is the sole input to the kappa computation. |
| `kappa_adjudication_58.xlsx` | `分歧裁决表`, `裁决指南`, `分歧统计` | 58 | Adjudication of every discordant pair, with the final disposition (retained / removed / downgraded to `closeMatch`). |
| `compute_kappa.py` | — | — | Recomputes Cohen's kappa, the linearly weighted kappa, both 95% CIs, observed agreement and the discordant-pair count from the rating sheet. |
| `README.md` | — | — | This file. |

Original internal filenames (not archived): `专家复核表_映射kappa双盲_已填写.xlsx`
and `裁决表_映射分歧58_已填裁决.xlsx`.

## Reproducing the reported statistics

```bash
pip install openpyxl
python compute_kappa.py
```

Expected output:

```
rated items                 : 318
discordant pairs            : 58
observed agreement (Po)     : 81.8%
expected agreement (Pe)     : 53.0%
Cohen's kappa               : 0.612  (95% CI 0.521-0.702)
linearly weighted kappa     : 0.676  (95% CI 0.585-0.767)
```

The script exits with status 0 only if all three published figures are
reproduced, so it doubles as a regression check.

## Rating scale and computation conventions

* Scale: **正确** (correct) → **存疑** (uncertain) → **错误** (incorrect), treated
  as ordinal with K = 3. Rater marginals: A = 219 / 17 / 82; B = 213 / 25 / 80.
* Linear weights: `w_ij = 1 − |i − j| / (K − 1)`. Using the complement
  `|i − j| / (K − 1)` would produce a weighted *disagreement* statistic
  (−0.466 here), not Cohen's weighted kappa.
* Confidence intervals are asymptotic:
  `SE(κ) = sqrt( Po (1 − Po) / ((1 − Pe)² · n) )`, CI = `κ ± 1.96 · SE`.
* `填写说明` records the rating rubric and `抽样框统计` the sampling frame
  (FMA / SNOMED CT × TCM branch / modern branch / other); both are shipped so
  the sampling design can be audited.

## De-identification statement

The two workbooks published here contain **no personal identifiers**: the rating
sheet records only the verdict and free-text correction suggestion of each rater,
labelled `专家A` / `专家B` (rater A / rater B), with no names, signatures,
dates, e-mail addresses or affiliations. Before release, the workbook document
properties were inspected and normalised — the internal originals carried the
project lead's name in the `lastModifiedBy` field and creation timestamps, both
of which have been cleared.

Four further review workbooks produced during curation are **not** published,
because they carry personal or adjudicator-attributable information:

| Workbook | Reason for exclusion |
|---|---|
| `专家复核表_英文标签消歧_已填写.xlsx` | contains three experts' signatures and per-row dates |
| `专家复核表_专家填写_1.9.5-1.9.7.xlsx` | contains per-expert style labels and signed opinions |
| `裁决表_标签遗留_PI.xlsx` / `_已填写.xlsx` | contains the principal investigator's case-by-case rulings |
| `回执表_5对冲突合并_PI复核.xlsx` / `_已填写.xlsx` | as above |

The exclusions do not affect reproducibility of any statistic reported in the
paper: kappa depends only on `kappa_ratings_double_blind_318.xlsx`.

## Licence

CC-BY 4.0, as for the rest of the release.
