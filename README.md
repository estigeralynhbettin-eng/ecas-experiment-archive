# ECAS Experiment Data and Offline Replay

**Companion article:** ECAS: Evidence Contracts for API Security Rule Construction and Evaluation

**Journal:** Automated Software Engineering

**Authors:** Yi Lv and Cheng Wang

**Corresponding author:** Yi Lv, School of Computer Science and Technology, Tongji University, Shanghai 201804, China; lvyi@tongji.edu.cn.

Public archive version 1.0.0, 18 October 2026.
This release accompanies Online Resource 3 of the revised article.
Companion article: *ECAS: Evidence Contracts for API Security Rule Construction and Evaluation*.

This archive contains the fixed experiments used in the revised article.
It separates the original 30-task evaluation from later comparisons and controls.

| Location | Contents |
|---|---|
| `original_r12/ESM_1_ORIGINAL_UNCHANGED.zip` | Unchanged original 30-task archive: 21 policy tasks, nine deficient-evidence controls, local and hosted configurations |
| `revision/archives/` | Seven-case comparisons with adapted P2P and AutoPAC workflows, original prompts/outputs, policies, results, failures and related controls |
| `revision/offline/replay.py` | Credential-free replay of selected stored policies and evidence checks |
| `revision/verification_observed/` | Previously observed replay records, retained with their historical identity |
| `CURATION_REPORT.json` | Removed files and provider-field transformations, with original and curated-file digests |

Start with `REPRODUCE.md`, then verify the files with `python3 verify_release.py`.
The 673-check matrices form a separate archive and are not experimental tasks.

## Reading the results

The two comparison batches have different protocols. Their 21 method traces
include 17 executed traces and four unexecuted traces. Unexecuted traces are
not request denials. The 95 related control records come from 11 parent
candidates; 51 deliberately invalid evidence/binding variants were refused
execution eligibility. These controls are not 95 independent business cases.
Failed business judgments and admitted locator/hash changes are retained.

The supported replay uses stored outputs, a fixed ECAS interpreter and a local
OPA binary. It does not regenerate rules or reproduce the native P2P/AutoPAC
systems. No model weights, API credentials, application server, database or GPU
is needed for that replay. See `revision/EXPERIMENT_INDEX.json` for scopes.

## Curation and rights

Provider reasoning fields and duplicate transport stdout were removed from the
supplementary package. Internal dispatch approvals, process locks and unused
transport tooling were excluded. Scientific setup history, first-candidate
freezes, failures, inputs and parsed outputs are preserved; every retained or transformed file is mapped in the curation
report. Some historical provenance records contain old machine locations;
they are not working paths for reproduction. Historical nested manifests
describe the original evidence set; the new root manifests describe this
release. See `LICENSE_STATUS.md` before reuse.

## License and citation

Original author software is licensed under Apache-2.0. Original author data, documentation and checklist material are licensed under CC BY-SA 4.0. Original R12 material and third-party material retain their existing terms. See `LICENSE_STATUS.md` and `LICENSE_SCOPE.csv` for the exact scope.

Use `CITATION.cff` to cite version 1.0.0. Zenodo DOI: https://doi.org/10.5281/zenodo.23444761.

## Funding

This work was supported by the Discipline Breakthrough Pioneer Program of the Ministry of Education of China (Grant No. JYB2025XDXM122).

Related ECAS resource: https://doi.org/10.5281/zenodo.23444774
