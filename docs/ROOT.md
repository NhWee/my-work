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
