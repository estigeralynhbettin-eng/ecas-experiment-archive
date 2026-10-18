# Reproduction guide

## Verify the download

Run `python3 verify_release.py` from this directory. This uses the Python
standard library to check the manifest, file sizes and SHA-256 digests.
It does not execute models or security policies.

## Original 30-task experiment

Extract `original_r12/ESM_1_ORIGINAL_UNCHANGED.zip` into a separate directory.
Follow its `README.md`, `verify_artifact.py` and recorded protocols. Its
identity is unchanged. Hosted model generation is not required to inspect
the retained tasks, candidate outputs and results.

## Later archived-output replay

Use Linux x86-64 and Python 3.10 or later. Install the dependencies listed in
`revision/requirements.txt` before disconnecting the replay environment.
Before entering the offline environment, run `python3 revision/prepare_tools.py`
from the archive root. It downloads the exact official OPA v1.19.0 Linux
x86-64 static asset and verifies the historical SHA-256 before installation.
An equivalent manual download is described in `revision/TOOLS.md`.
The public archive does not redistribute the binary. Allow at least 500 MB
free space plus space for output logs.

From `revision/`, use a new output directory outside that directory:

```sh
sudo unshare --net -- python3 offline/replay.py t0 --output ../../ecas_replay_output
sudo unshare --net -- python3 offline/replay.py replay --output ../../ecas_replay_output
```

T0 must report `PASS`. It checks inputs, the engine, OPA, a small engineering
fixture and network isolation. Replay checks selected trace qualifications,
34 stored request decisions, and the 95 evidence/schema controls with their
available request fixtures. Inspect `REPLAY_SUMMARY.json` and per-record logs.
A mismatch exits with an error. Outputs must never overwrite archive inputs.

The E17 model Judge, E18 source reading, full E19 missing-state probe and E21
source-function probe are retained as historical evidence; this replay entry
does not rerun them. No new model call is made. The original failures,
out-of-scope outcomes and rejected compilation results remain distinguishable.

## Verification identity

`revision/verification_observed/` records the earlier observed replay. The
release preserves the runtime, candidate policies, contracts, fixtures and
adapter bytes used to produce its decisions. Documentation, packaging and
redacted provider envelopes have a new identity. The earlier verification
identity described a preliminary package: README.md, requirements.txt and
SOURCE_MAP.json later changed. It is not a clean-extraction execution receipt
for this public release. Current static checks and their exact scope
are summarized in the separate author delivery report.
