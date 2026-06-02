#!/usr/bin/env bash
set -euo pipefail

cd /work/CMSSW_4_4_7/src
eval "$(scramv1 runtime -sh)"
cd /work
mkdir -p results
export MAX_EVENTS="${1:-10}"
export OUTPUT_FILE="${2:-hihighpt_jets.root}"
echo "Running cmsRun from $(pwd)"
echo "MAX_EVENTS=${MAX_EVENTS}"
echo "OUTPUT_FILE=${OUTPUT_FILE}"
cmsRun /work/cms/run_hijet_analyzer_cfg.py
mv -f "${OUTPUT_FILE}" "results/${OUTPUT_FILE}"
