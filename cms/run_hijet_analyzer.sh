#!/usr/bin/env bash
set -euo pipefail

cd /work/CMSSW_4_4_7/src
eval "$(scramv1 runtime -sh)"
cd /work
mkdir -p results
echo "Running cmsRun from $(pwd)"
ls -ld results
cmsRun /work/cms/run_hijet_analyzer_cfg.py
mv -f hihighpt_jets.root results/hihighpt_jets.root
