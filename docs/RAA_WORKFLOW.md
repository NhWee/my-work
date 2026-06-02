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
