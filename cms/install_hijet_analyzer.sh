#!/usr/bin/env bash
set -euo pipefail

CMSSW_SRC="/work/CMSSW_4_4_7/src"
PACKAGE_DIR="${CMSSW_SRC}/HiJetAnalysis"

rm -rf "${PACKAGE_DIR}"
mkdir -p "${CMSSW_SRC}"
cp -R /work/cms/HiJetAnalysis "${PACKAGE_DIR}"

cd "${CMSSW_SRC}"
eval "$(scramv1 runtime -sh)"
scram b -j 2
