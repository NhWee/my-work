# CMS Open Data: Jet Spectra and Dijet Asymmetry

A collider-analysis learning project using **CMS 2011 Pb–Pb and pp data at √sNN = 2.76 TeV**. The aim is to follow how reconstructed event collections become jet observables: inspect the data, extract a compact analysis tree, select jets, and compare distributions.

The repository includes a CMSSW analyzer and Python tools for **jet transverse-momentum spectra, dijet imbalance AJ, and centrality-proxy comparisons**. An exploratory RAA-like ratio is included to study the analysis workflow.

## What is implemented

| Stage | Implementation |
| --- | --- |
| Inspect reconstructed data | CMSSW event-content helpers and ROOT inspection scripts |
| Extract jet variables | [`HiJetAnalyzer.cc`](cms/HiJetAnalysis/JetAnalyzer/plugins/HiJetAnalyzer.cc) with Pb–Pb and pp configurations |
| Analyze dijets | Leading/subleading jet kinematics, angular separation, and AJ |
| Compare event activity | HF-activity groups used as a centrality proxy |
| Compare spectra | Inclusive selected-jet pT spectra and per-event Pb–Pb/pp comparisons |
| Explore nuclear modification | RAA-proxy plotting scripts with documented normalization limitations |

**Current status:** analysis code and small-run checks are recorded in the repository. This is not a completed, corrected CMS measurement. Generated ROOT files and result plots are excluded from Git; reproduce them locally using the steps below.

## Analysis flow

```text
CMS RECO files
    → CMSSW jet analyzer
    → compact ROOT tree
    → Python / uproot selection and histograms
    → jet pT spectra and AJ
    → event-activity comparisons and exploratory RAA proxy
```

The dijet asymmetry is `AJ = (pT,leading − pT,subleading) / (pT,leading + pT,subleading)`.

## Data and software

| Input | Source |
| --- | --- |
| Pb–Pb HIHighPt, 2011, 2.76 TeV | [CERN Open Data record 14013](https://opendata.cern.ch/record/14013) |
| pp reference candidates, 2011, 2.76 TeV | [Record 14016](https://opendata.cern.ch/record/14016), [record 14017](https://opendata.cern.ch/record/14017) |
| pp validated luminosity sections | [Record 14208](https://opendata.cern.ch/record/14208) |

The extraction scripts use **CMSSW 4.4.7** inside a CMS container. Python plotting uses `uproot`, `awkward`, NumPy, pandas, and matplotlib. Installing the Python requirements alone does not provide the CMSSW runtime.

## First reproduction

### 1. Set up Python plotting

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Set up the CMS runtime

Follow [`docs/CMS_ENVIRONMENT.md`](docs/CMS_ENVIRONMENT.md) for WSL2, Docker, the CMS image, and runtime checks. Replace the example host path with your own checkout and mount the repository at `/work` as described there.

### 3. Extract a small Pb–Pb sample

Inside the configured CMS container:

```bash
cd /work
bash cms/install_hijet_analyzer.sh
bash cms/run_hijet_analyzer.sh 10 hihighpt_jets.root
```

This processes up to 10 events from the configured remote input and writes `results/hihighpt_jets.root`. It is a connectivity and analysis-chain check, not a statistically meaningful sample. Remote RECO access can be slow.

### 4. Inspect the first distribution

Back in Windows PowerShell, from the repository root:

```powershell
.\.venv\Scripts\python.exe src\plot_hijet_aj.py
```

Expected plot location: `results/hihighpt_aj_hist.png`. Very small samples or samples failing the selection may not populate the histogram.

For pp processing, centrality-proxy selections, spectra, and ratio commands, continue with [`docs/RAA_WORKFLOW.md`](docs/RAA_WORKFLOW.md).

## Code guide

| Location | Purpose |
| --- | --- |
| `cms/HiJetAnalysis/JetAnalyzer/plugins/` | C++ analyzer and CMSSW build configuration |
| `cms/run_*analyzer*.sh`, `cms/run_*analyzer_cfg.py` | Runtime wrappers and Pb–Pb/pp input settings |
| `src/inspect_root.py`, `src/inspect_hijet_events.py` | Inspect ROOT structure and extracted events |
| `src/plot_hijet_aj.py`, `src/plot_hijet_centrality_aj.py` | Dijet imbalance and event-activity comparisons |
| `src/plot_jet_pt_spectrum.py`, `src/plot_pbpb_centrality_jet_spectrum.py` | Jet spectra |
| `src/plot_raa_proxy.py`, `src/plot_raa_vs_centrality.py` | Exploratory ratios |
| `src/summarize_hijet_sample.py`, `src/summarize_jet_outputs.py` | Sample and output summaries |
| `notebooks/` | Starter and exploratory notebooks |

## How to interpret the outputs

- `hf_tower_sum` groups are **centrality proxies**, not calibrated CMS centrality percentiles. Conventional percentile labels in exploratory plots do not establish calibration.
- A Pb–Pb/pp ratio is not automatically a physical RAA measurement. Trigger/selection effects, jet calibration, luminosity or cross-section normalization, TAA/Ncoll, and systematic uncertainties must be addressed.
- The current analyzer reads reconstructed jet collections; this repository does not claim to reconstruct tracks or jets from detector raw signals.
- Recorded small-run results in the documentation demonstrate workflow progress, not validation of the full physics measurement.

## Next steps

1. Fix a reproducible sample list and matched Pb–Pb/pp selections.
2. Document trigger treatment, luminosity selection, and jet-collection compatibility.
3. Replace HF-activity proxies with a validated centrality treatment.
4. Add the corrections, normalization, and uncertainties needed for quantitative interpretation.
5. Publish a compact, reproducible set of representative figures with sample sizes and cuts.

See [`CHANGELOG.md`](CHANGELOG.md) for the recorded progression, [`docs/ROOT.md`](docs/ROOT.md) for ROOT basics, and [`docs/RAA_WORKFLOW.md`](docs/RAA_WORKFLOW.md) for analysis details.
