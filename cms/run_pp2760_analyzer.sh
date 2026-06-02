#!/usr/bin/env bash
set -euo pipefail

cd /work/CMSSW_4_4_7/src
eval "$(scramv1 runtime -sh)"
cd /work
mkdir -p results
export MAX_EVENTS="${1:-10}"
export OUTPUT_FILE="${2:-pp2760_jets.root}"
export INPUT_FILE="${3:-root://eospublic.cern.ch//eos/opendata/cms/Run2011A/AllPhysics2760/RECO/16Jul2011-v1/0000/00135ABC-6AB1-E011-B6C6-00E08178C0F7.root}"
export MIN_JET_PT="${4:-30.0}"
echo "Running pp cmsRun from $(pwd)"
echo "MAX_EVENTS=${MAX_EVENTS}"
echo "OUTPUT_FILE=${OUTPUT_FILE}"
echo "INPUT_FILE=${INPUT_FILE}"
echo "MIN_JET_PT=${MIN_JET_PT}"
cmsRun /work/cms/run_pp2760_analyzer_cfg.py
mv -f "${OUTPUT_FILE}" "results/${OUTPUT_FILE}"
