# Reproduce

The historical runtime and inputs are delivered under evidence_files/runtime and evidence_files/inputs. SOURCE_MANIFEST.json maps every snapshot to the original hash. The completed runs are under evidence_files/managed_runs with request bindings, raw logs and status.

1. Verify SOURCE_MANIFEST.json / DELIVERY_MANIFEST.json.
2. Use an isolated WSL lane and the original Python 3.10+ interpreter with jsonschema.
3. For the original lane, validate and start T0_REQUEST.json once with the D:/lunwen/tools/wsl-experiment-runner/Invoke-WslExperiment.ps1 managed runner; inspect terminal status.
4. After T0 PASS, validate/start RUN_REQUEST.json once and inspect the final state.
5. Running a fresh reproduction requires new lane/run IDs and corresponding path binding; never overwrite the original lane or infer submission readiness from SUCCEEDED.

Schema failures are engineering controls. Inventory rejection makes a policy ineligible for execution; it is not a deny decision or business correctness.
