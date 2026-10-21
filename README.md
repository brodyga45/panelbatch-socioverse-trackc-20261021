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
speedup is claimed. See the5page working report and full raw evidence under
`PanelBatch/`. These are local measurements, not independent replication.

## Linux compatibility check

The workflow uses a standard Ubuntu GitHub-hosted runner and Python3.12. It runs
four meaningful compatibility checks and a new actual128-agent baseline/bulk
study, comparing every stored panel value, metrics and events. It does not rerun
large speed benchmarks, upload artifacts, use a cache, access paid APIs, or
establish an independent human review. The exact implementation commit `ce0a12e5f52f9dbe2aa6728fee94e9d11fb8f81d`
passed [run39592649924](https://github.com/brodyga45/panelbatch-socioverse-trackc-20261021/actions/runs/39592649924)
on21Oct2026:4tests passed and both actual128-agent studies retained896rows each
with exact panel/metrics/events parity. This automated hosted-runner check is not
an independent scientific replication or a Linux speed benchmark. Later
documentation-only commits preserve the tested implementation unchanged.

For local one-command performance reproduction, follow `PanelBatch/README.md`.
The study-only archive has a separate `run.py` entrypoint and uses this full project
as its companion dependency.

Implementation, experiments and report were AI-assisted. No human code review,
contest acceptance, award, business-bank receipt or empirical claim about real
people is asserted. Team registration and source publication are not revenue.

## When the opt-in writer may help

The5page report now distinguishes absolute saved time, a clearly labelled arithmetic sensitivity to additional work, the higher RSS, integration/maintenance cost and the simpler upstream-patch alternative. Existing measurements were not rerun or replaced. A separate agent also reproduced the exactv4 study entrypoint locally; that is a scoped operational check, not human or scientific replication. See `PanelBatch/adoption-analysis.json` and `PanelBatch/independent-agent-entrypoint-check.json`.
