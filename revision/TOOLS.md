# Prepare the fixed replay tool

The public archive keeps code and evidence separate from the OPA binary.
Before network isolation, run `python3 prepare_tools.py` in this directory.
The download must match SHA-256 `1dd5c5591ff856f5e20a1d66bafae9511ddf3c5552ed3b5070c70b2b6580ee3f`.

The official source is [https://github.com/open-policy-agent/opa/releases/download/v1.19.0/opa_linux_amd64_static](https://github.com/open-policy-agent/opa/releases/download/v1.19.0/opa_linux_amd64_static). This is the same static asset
used in the archived observations. Its embedded `+dirty` marker is present
in that official asset; the official release digest matches the historical
binary. The binary is not redistributed in this archive.

For manual preparation, save that asset as `runtime/bin/opa`, check the digest
with `sha256sum runtime/bin/opa`, then run `chmod +x runtime/bin/opa`.
Only then enter the offline T0/replay environment. The revision manifest
includes the expected binary digest as an external prerequisite, so T0
requires those exact bytes. These instructions do not download or invoke
any model or provider API.
