#!/bin/sh
set -eu
cd "$(dirname "$0")"
: "${PANEL_BATCH_PYTHON:=python3}"
: "${PANEL_BATCH_RUN_DIR:=$(mktemp -d "${TMPDIR:-/tmp}/panelbatch-reproduction-XXXXXX")}"
"$PANEL_BATCH_PYTHON" -m pytest test_panel_batch_compatibility.py -q
"$PANEL_BATCH_PYTHON" bulk_panel_probe.py --output-json "$PANEL_BATCH_RUN_DIR/component-result.json"
"$PANEL_BATCH_PYTHON" bulk_study_probe.py --archive-to "$PANEL_BATCH_RUN_DIR/study-series"
"$PANEL_BATCH_PYTHON" demo_study.py --output "$PANEL_BATCH_RUN_DIR/demo-studies"
printf 'Reproduction outputs retained in %s\n' "$PANEL_BATCH_RUN_DIR"
