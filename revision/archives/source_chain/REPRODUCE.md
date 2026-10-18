# Reproduction scope

This is a source-function and adapter interpretation experiment on one exposed historical case. It is not a production Frappe test or a model-generation benchmark.

1. Inspect TASK_CONTRACT_CN.md, PROTOCOL_CN.md, source reports, INPUT_MANIFEST.json, SOURCE_MANIFEST.json and the pinned inputs.
2. Read the existing managed run receipts for source-rule-chain-t0-v1 and source-rule-chain-main-v1. Query their status; do not start them again.
3. A fresh reproduction requires a new independent WSL lane and run IDs, rebinding paths/hashes and the normal experiment gates. Use source_chain_probe.py prepare, managed T0, the actual scoped gate, make-request and managed run in that order. After a successful scoped T0, preserve the project's previous T0_EVIDENCE.json and bind its pointer to this scope's actual receipt using a project-relative receipt_path; the current gate resolves that pointer and otherwise reports T0_EVIDENCE_MISSING. Preserve the blocked receipt rather than treating pointer failure as a scientific result.
4. The two source functions are extracted unchanged from their AST; stubs cover only one supplier object, translations, date access and blocking exceptions. A source `allow` means only that this hold check did not block.
5. Compare RESULTS.json with all raw WSL captures and the independently frozen oracle. effective_manual is a human-authored adapter control shared by all methods, not a generated ECAS result.
6. build_chain_report.py reads old seven-case evidence and the completed local results; it performs no model or policy execution. Preserve all original R1-R3 reports and scientific ledgers.
