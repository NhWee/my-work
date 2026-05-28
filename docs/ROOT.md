# ROOT Setup Notes

This workspace supports ROOT-file analysis on Windows through `uproot`.

## Current Windows Setup

Use this when you need to read, write, inspect, and analyze `.root` files from
Python:

```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
python src\root_example.py
```

Plot a branch from a ROOT file:

```powershell
python src\plot_root.py results\example.root
```

Included packages:

- `uproot`: read and write ROOT files without a full CERN ROOT installation
- `awkward`: jagged array support
- `hist`: histogram utilities

## Full CERN ROOT

Use full CERN ROOT when you specifically need PyROOT, ROOT C++ macros,
`TCanvas`, `RDataFrame`, or interactive ROOT tools.

For full CERN ROOT on this Windows machine, prefer WSL/Ubuntu with conda:

```bash
conda create -c conda-forge --name cernroot root python
conda activate cernroot
python -c "import ROOT; print(ROOT.gROOT.GetVersion())"
```

Native Windows builds are possible but are more fragile because they require a
matching compiler and build toolchain.

## Practice Data Sources

- Start with generated toy data from `src/root_example.py`.
- Use CERN Open Data when you want real particle-physics ROOT files.
- Prefer smaller education/outreach examples first; full CMS AOD files are large
  and need experiment-specific software knowledge.

## CMS Open Data Quick Start

The CMS Open Data Guide recommends NanoAOD/NanoAOD-like files for plain ROOT or
Python analysis because they are stored as ROOT `TTree` objects with standard
types.

Example dataset:

- Portal record: https://opendata.cern.ch/record/31104
- Dataset: `Run2010A_Mu` in Run1 NanoAOD-like format
- Example file:
  `http://opendata.cern.ch/eos/opendata/cms/derived-data/NanoAODRun1/01-Jul-22/Run2010A_Mu/0E1203D1-AEA1-4ED6-B1FF-1F2F72FEE6D9.root`

List files from the record:

```powershell
$env:PYTHONUTF8='1'
.\.venv\Scripts\cernopendata-client.exe get-file-locations --recid 31104 --protocol http
```

Inspect the remote ROOT file without downloading it:

```powershell
.\.venv\Scripts\python.exe src\inspect_root.py "http://opendata.cern.ch/eos/opendata/cms/derived-data/NanoAODRun1/01-Jul-22/Run2010A_Mu/0E1203D1-AEA1-4ED6-B1FF-1F2F72FEE6D9.root" --limit 1
```

Plot real CMS branches from the remote file:

```powershell
.\.venv\Scripts\python.exe src\plot_root.py "http://opendata.cern.ch/eos/opendata/cms/derived-data/NanoAODRun1/01-Jul-22/Run2010A_Mu/0E1203D1-AEA1-4ED6-B1FF-1F2F72FEE6D9.root" --tree Events --branch nMuon --output results\cms_nMuon_hist.png --bins 8

.\.venv\Scripts\python.exe src\plot_root.py "http://opendata.cern.ch/eos/opendata/cms/derived-data/NanoAODRun1/01-Jul-22/Run2010A_Mu/0E1203D1-AEA1-4ED6-B1FF-1F2F72FEE6D9.root" --tree Events --branch Muon_pt --output results\cms_muon_pt_hist.png --bins 50
```
