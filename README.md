# TCM-BO: Traditional Chinese Medicine Body-structure Ontology

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![OWL 2 DL](https://img.shields.io/badge/OWL%202%20DL-verified-brightgreen.svg)](measure_1917.json)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22638644.svg)](https://doi.org/10.5281/zenodo.22638644)

**TCM-BO** is a bilingual (Chinese–English) OWL 2 DL ontology of traditional Chinese medicine (TCM) body structures, systematically aligned with **ICD-11**, **FMA** and **SNOMED CT**. It formalises TCM-specific structural relations that have no biomedical analogue (e.g. 开窍于 *opens into*, 相表里 *exterior–interior pairing*, 在体合 *body-tissue correspondence*, 志藏于 *emotion stored in*), supplies an auditable cross-terminology mapping layer, and documents a reproducible quality-control and mapping-audit methodology.

- **Ontology IRI:** `http://OntoTCM.org.cn/ontologies/TCM_TO`
- **Current release:** `1.9.17` (2026-09-03) — strict OWL 2 DL, zero profile violations
- **Repository:** https://github.com/Pinellia7ternata/TCM-BO
- **Licence:** [CC-BY 4.0](LICENSE)

## Release 1.9.17 at a glance

| Metric | Value |
|---|---|
| Classes | 3,683 |
| Named individuals | 612 |
| Object properties | 29 |
| Datatype properties | 17 |
| Annotation properties | 19 |
| ICD-11 coverage | 3,172 classes (86.1%) |
| FMA coverage | 2,637 classes (71.6%) |
| SNOMED CT coverage | 588 classes (16.0%) |
| skos mappings | 16 exact / 3,101 close (3,117 total) |
| Textual definitions | 561 classes (15.2%) |
| Max hierarchy depth | 17 (88.5% of classes at depth ≥ 10) |

## Logical consistency (verified 2026-09-03/04)

- **HermiT** (sound & complete for OWL 2 DL / SROIQ(D)): full classification, exit code 0, 18 h 54 m 52 s wall-clock, no inconsistency — **decisive verdict**;
- **ELK** (OWL 2 EL): pass in 7 s (independent necessary condition);
- **JFact**: attempted four times (releases 1.9.16/1.9.17); all runs were terminated by the host environment before completion — reported as a verification-infrastructure limitation, not as evidence of a defect.

Raw logs (`elk_1917_verdict.log`, `hermit_1917_verdict.log`, `jfact_1917_verdict.log`), ROBOT `measure` outputs (`measure_1916.json`, `measure_1917.json`) and the full evidence packs (推理机终判证据包) are in this repository.

## Repository layout

```
TCM_BO_1.9.17.owl            the release ontology (RDF/XML, open in Protégé)
*_verdict.log                ELK / HermiT / JFact reasoner verdict logs
measure_1916.json, measure_1917.json   ROBOT measure outputs
推理机终判证据包_1.9.16.md / _1.9.17.md  full consistency-verdict evidence packs
metrics_1917.py, qc_verify_1916.py, make_figures.py   metric / QC / figure scripts used for the paper
TCM_BO_1.8.0_诊断与完善建议报告.md   full diagnostic & curation report (Chinese)
.htaccess                    w3id redirect rules (to be submitted to perma-id/w3id.org)
```

## Reproduce the metrics

```bash
python metrics_1917.py        # per-IRI aggregated content statistics
python qc_verify_1916.py      # static QC: type conflicts / asymmetry / sameAs
```

## Citation

A manuscript describing TCM-BO is under preparation for journal submission. In the meantime, please cite this repository:

> Chen C, Chen Z, Hao Y-L, Han Z, Hou W, Lei L. TCM-BO: a bilingual ontology of traditional Chinese medicine body structures aligned with ICD-11, FMA and SNOMED CT, release 1.9.17. Zenodo. 2026. https://doi.org/10.5281/zenodo.22638644 (CC-BY 4.0).

See [CITATION.cff](CITATION.cff).

## Contact

Maintainer: Chao Chen (chenchao_0727@163.com), Institute of Information on Traditional Chinese Medicine, China Academy of Chinese Medical Sciences, Beijing 100700, China.

Corresponding authors: Weixin Hou (hwx0111@163.com); Lei Lei (leilei@mail.cintcm.ac.cn).
