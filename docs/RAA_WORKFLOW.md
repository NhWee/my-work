# Centrality-dependent RAA Workflow

This note records the workflow for building a centrality-dependent nuclear
modification factor with CMS 2011 heavy-ion open data.

## Goal

For jets, the nuclear modification factor is schematically:

```text
R_AA(pT, centrality) =
  (1 / T_AA(centrality)) *
  (dN_AA / dpT) /
  (dSigma_pp / dpT)
```

An equivalent event-count form often used for a first workflow check is:

```text
R_AA(pT, centrality) =
  (1 / N_coll(centrality)) *
  (yield per PbPb event) /
  (yield per pp event)
```

The second form is useful for learning the analysis flow, but a final physics
result needs calibrated centrality, luminosity or cross-section normalization,
trigger corrections, jet energy corrections, and systematic uncertainties.

## Data Inputs

PbPb signal sample:

```text
Record: 14013
Dataset: /HIHighPt/HIRun2011-15Apr2013-v1/RECO
Collision: PbPb at 2.76 TeV
CMSSW: CMSSW_4_4_7
```

pp reference candidates:

```text
Record: 14016
Dataset: /AllPhysics2760/Run2011A-16Jul2011-v1/RECO
Collision: pp at 2.76 TeV
CMSSW: CMSSW_4_4_7
```

```text
Record: 14017
Dataset: /AllPhysics2760/Nov2011_HI-SD_JetHI-276TeV_ppRereco/RECO
Collision: pp at 2.76 TeV
CMSSW: CMSSW_4_4_7
```

The pp reference must use validated luminosity sections. CERN provides the
2011 pp 2.76 TeV validation JSON in record 14208.

## Minimum Analysis Steps

1. Build PbPb jet spectra by centrality proxy.

   Current starting point:

   ```text
   hf_tower_sum
   lead_pt
   sublead_pt
   dphi
   aj
   ```

   The current `hf_tower_sum` centrality split is only a proxy. A calibrated
   CMS centrality binning is needed later.

2. Build pp jet spectra with a matching analyzer.

   The pp analyzer should produce the same jet variables, but without PbPb
   centrality branches:

   ```text
   run
   lumi
   event
   nJet
   lead_pt
   sublead_pt
   dphi
   aj
   ```

3. Apply the same jet selection to both samples.

   First dijet-oriented selection:

   ```text
   lead_pt > 120 GeV
   sublead_pt > 50 GeV
   dphi > 2*pi/3
   abs(eta) < 2.0
   ```

4. Histogram jet pT.

   For RAA, use a pT spectrum, not only A_J:

   ```text
   PbPb: jet yield per event in each centrality bin
   pp: jet yield per event or cross-section reference
   ```

5. Normalize.

   For a first proxy:

   ```text
   R_AA_proxy = (PbPb yield per event) / (pp yield per event)
   ```

   For a physics RAA:

   ```text
   R_AA = (1 / T_AA) * (PbPb yield per event) / (pp cross section)
   ```

6. Add centrality calibration.

   Needed external quantities:

   ```text
   centrality percentiles
   N_coll or T_AA per centrality bin
   ```

## Next Practical Task

The next code step is to add a pp input configuration and run the same mini
analyzer on the 2.76 TeV pp reference data. After that, build matched PbPb and
pp jet-pT histograms.

## Current pp Reference Test

A first accessible pp reference file was found in record 14016:

```text
root://eospublic.cern.ch//eos/opendata/cms/Run2011A/AllPhysics2760/RECO/16Jul2011-v1/0000/00135ABC-6AB1-E011-B6C6-00E08178C0F7.root
```

Its event content includes:

```text
vector<reco::PFJet> "ak5PFJets" "" "RECO"
```

The pp analyzer configuration is:

```text
cms/run_pp2760_analyzer_cfg.py
```

Run a small pp test inside the CMS container:

```bash
cd /work
bash cms/install_hijet_analyzer.sh
bash cms/run_pp2760_analyzer.sh 10 pp2760_jets.root
```

To test a different pp input file, pass it as the third argument:

```bash
bash cms/run_pp2760_analyzer.sh 300 pp2760_test.root root://eospublic.cern.ch//path/to/file.root
```

To lower the analyzer jet threshold, pass `MIN_JET_PT` as the last argument.
For example, create outputs for a 1-50 GeV study:

```bash
bash cms/run_hijet_analyzer.sh 100 hihighpt_jets_min1_100.root 1.0
bash cms/run_pp2760_analyzer.sh 1000 pp2760_jets_min1_1000.root root://eospublic.cern.ch//eos/opendata/cms/Run2011A/AllPhysics2760/RECO/16Jul2011-v1/0000/00135ABC-6AB1-E011-B6C6-00E08178C0F7.root 1.0
```

Output:

```text
results/pp2760_jets.root
```

The mini analyzer now stores inclusive selected-jet arrays:

```text
jet_pt
jet_eta
jet_phi
```

Plot a selected-jet pT spectrum from any output file that contains `jet_pt`:

```powershell
.\.venv\Scripts\python.exe src\plot_jet_pt_spectrum.py results\pp2760_jets.root
```

To compare PbPb and pp, first re-run the PbPb analyzer after this inclusive
jet branch update, then pass both output files:

```powershell
.\.venv\Scripts\python.exe src\plot_jet_pt_spectrum.py results\pbpb.root results\pp2760_jets.root
```

## First RAA Proxy

After producing inclusive jet outputs for PbPb and pp, run:

```powershell
.\.venv\Scripts\python.exe src\plot_raa_proxy.py
```

For a 1 GeV binning over 1-50 GeV:

```powershell
.\.venv\Scripts\python.exe src\plot_raa_proxy.py --pbpb results\hihighpt_jets_min1_100.root --pp results\pp2760_jets_min1_1000.root --pt-low 1 --pt-high 50 --pt-bin-width 1 --output-prefix raa_proxy_pt1_50_min1
```

Outputs:

```text
results/raa_proxy_pt1_50_min1_spectra_per_event.png
results/raa_proxy_pt1_50_min1_ratio.png
results/raa_proxy_pt1_50_min1_summary.csv
```

To plot integrated `R_AA_proxy` versus centrality proxy for
`1 < jet pT < 30 GeV`, run:

```powershell
.\.venv\Scripts\python.exe src\plot_raa_vs_centrality.py
```

Outputs:

```text
results/raa_proxy_vs_centrality_pt1_30.png
results/raa_proxy_vs_centrality_pt1_30.csv
```

The x-axis uses HF activity quantile bins, ordered from peripheral-like to
central-like. This is not yet calibrated CMS centrality.

Current default inputs:

```text
PbPb: results/hihighpt_jets_inclusive_300.root
pp:   results/pp2760_jets_2000.root
```

Outputs:

```text
results/raa_proxy_spectra_per_event.png
results/raa_proxy_ratio.png
results/raa_proxy_summary.csv
```

This is only a first proxy:

```text
R_AA_proxy = PbPb jets-per-event / pp jets-per-event
```

It does not yet include:

```text
T_AA or N_coll
integrated luminosity
trigger efficiency and prescales
jet energy corrections
centrality calibration
```

Bins with zero pp jets are left empty in the ratio. More pp statistics or a
more jet-rich pp reference selection is needed before interpreting high-pT bins.

Summarize jet counts in analyzer outputs:

```powershell
.\.venv\Scripts\python.exe src\summarize_jet_outputs.py results\pp2760_jets_2000.root
```

## pp File Scan Notes

Initial 14016 pp file scan using 300 events per candidate:

```text
file label   selected jets   jets pT > 50   jets pT > 100   max pT
try2         13              0              0               45.055
try3         17              4              0               67.323
try4         20              10             0               95.998
try5         7               1              0               97.254
try6         6               2              0               56.744
try7         10              2              0               50.978
```

Current best short-scan candidate for moderate-pT jets:

```text
try4
root://eospublic.cern.ch//eos/opendata/cms/Run2011A/AllPhysics2760/RECO/16Jul2011-v1/0000/28C3A8C2-65B1-E011-A15F-00304867402A.root
```

The original first pp file remains useful for longer statistics:

```text
2000 events
137 selected jets
29 jets with pT > 50 GeV
1 jet with pT > 100 GeV
```
