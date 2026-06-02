#!/usr/bin/env bash
set -euo pipefail

FILE_URL="${1:-root://eospublic.cern.ch//eos/opendata/cms/Nov2011_HI/AllPhysics2760/RECO/SD_JetHI-276TeV_ppRereco/0000/02B6053F-061A-E111-9D86-003048F2E688.root}"

cd /work/CMSSW_4_4_7/src
eval "$(scramv1 runtime -sh)"

echo "Checking pp 2.76 TeV event content:"
echo "${FILE_URL}"
echo

edmDumpEventContent "${FILE_URL}" \
  | grep -E 'ak.*Jet|TriggerResults|Centrality' \
  | head -80
