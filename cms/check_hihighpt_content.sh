#!/usr/bin/env bash
set -euo pipefail

INPUT_FILE="${1:-root://eospublic.cern.ch//eos/opendata/cms/hidata/HIRun2011/HIHighPt/RECO/15Apr2013-v1/10000/0056B4D7-E8A5-E211-935E-003048F316C4.root}"

if ! command -v edmDumpEventContent >/dev/null 2>&1; then
  cd /work/CMSSW_4_4_7/src
  eval "$(scramv1 runtime -sh)"
  cd /work
fi

echo "Input file:"
echo "${INPUT_FILE}"
echo

echo "Jet-quenching-relevant event products:"
edmDumpEventContent "${INPUT_FILE}" \
  | grep -E 'Centrality|ak.*Jet|TriggerResults|hiEvtPlane' \
  | head -120
