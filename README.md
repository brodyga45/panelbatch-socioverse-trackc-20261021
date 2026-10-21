# PanelBatch: compatible trajectory persistence for SocioVerse2

A Track C research candidate: use a typed Arrow relation for bulk panel insertion,
while retaining the current store schema, transaction boundaries, other record
methods and finalization. This applies an established DuckDB ingestion mechanism;
it is not a new database algorithm.

The full local reproduction project is in `PanelBatch/`. The official SocioVerse2
source is pinned to commit `9c3ac774816511c121184ca11f539dc398ba1544`, with its
Apache-2.0 licence and original notices. Original PanelBatch code is Apache-2.0.
All experimental agents/data in this repository are synthetic. No credentials,
private correspondence, identity documents or competition-licensed NFL data are
included.

On one macOS ARM64 host, an archived three-seed six-step confirmation experiment
with2048agents measured an8.14x median full-run ratio. All raw timings and data are
retained, alongside a different preliminary series. A separate fresh-process
resource check found about19.5MB higher peak RSS; no memory/energy or model-bound
speedup is claimed. See the4page working report and full raw evidence under
`PanelBatch/`. These are local measurements, not independent replication.

## Linux compatibility check

The workflow uses a standard Ubuntu GitHub-hosted runner and Python3.12. It runs
four meaningful compatibility checks and a new actual128-agent baseline/bulk
study, comparing every stored panel value, metrics and events. It does not rerun
large speed benchmarks, upload artifacts, use a cache, access paid APIs, or
establish an independent human review. Until a concrete successful run is linked,
Linux compatibility is unverified.

For local one-command performance reproduction, follow `PanelBatch/README.md`.
The study-only archive has a separate `run.py` entrypoint and uses this full project
as its companion dependency.

Implementation, experiments and report were AI-assisted. No human code review,
contest acceptance, award, business-bank receipt or empirical claim about real
people is asserted. Team registration and source publication are not revenue.
