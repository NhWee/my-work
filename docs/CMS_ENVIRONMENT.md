# CMS Environment Setup

This document records the machine-level setup needed to reproduce the CMS Open
Data environment used by this workspace.

The repository stores analysis code and documentation, but it does not store
WSL, Docker Desktop, Docker images, `.venv`, downloaded data, or generated
results.

## 1. Install WSL2 and Ubuntu

In Windows PowerShell:

```powershell
wsl --install -d Ubuntu
```

After Ubuntu is installed, check:

```powershell
wsl -l -v
```

Ubuntu should be version 2.

If the default distro is accidentally `docker-desktop`, set Ubuntu as default:

```powershell
wsl --set-default Ubuntu
```

## 2. Install Docker Desktop

Install Docker Desktop for Windows:

https://www.docker.com/products/docker-desktop/

Use the Windows AMD64 build for this machine.

In Docker Desktop:

1. Open Settings.
2. Go to Resources > WSL Integration.
3. Enable integration with Ubuntu.
4. Apply and restart Docker Desktop.

Check from Windows PowerShell:

```powershell
docker run hello-world
```

Check from Ubuntu:

```bash
docker run hello-world
```

If Ubuntu reports permission denied for Docker:

```bash
sudo usermod -aG docker $USER
```

Then close Ubuntu and restart WSL:

```powershell
wsl --shutdown
```

Open Ubuntu again and retry:

```bash
docker run hello-world
```

## 3. Enable vsyscall for old CMS images

Old Scientific Linux based CMS Open Data images can exit immediately with code
139 unless WSL2 emulates `vsyscall`.

In Windows PowerShell:

```powershell
notepad $env:USERPROFILE\.wslconfig
```

Add:

```ini
[wsl2]
kernelCommandLine = vsyscall=emulate
```

Then restart WSL and Docker Desktop:

```powershell
wsl --shutdown
```

Confirm:

```powershell
wsl -d Ubuntu -- cat /proc/cmdline
```

The output should include:

```text
vsyscall=emulate
```

## 4. Pull the CMS Open Data image

For 2011 PbPb heavy-ion data such as `HIHighPt`, use CMSSW 4.4.7:

```bash
docker pull gitlab-registry.cern.ch/cms-cloud/cmssw-docker-opendata/cmssw_4_4_7-slc5_amd64_gcc434:latest
```

The image is large.

## 5. Enter the CMS container

Open Ubuntu, then:

```bash
cd /mnt/c/Users/Administrator/Documents/my-work/my-work
```

Run:

```bash
docker run -it --rm \
  -v "$PWD":/work \
  -w /work \
  gitlab-registry.cern.ch/cms-cloud/cmssw-docker-opendata/cmssw_4_4_7-slc5_amd64_gcc434:latest \
  /bin/bash
```

Inside the container, check:

```bash
pwd
ls
which cmsRun
echo $CMSSW_BASE
```

If `cmsRun` is available, the CMS runtime is ready.

## 6. Verify CMSSW in the container

Expected checks inside the container:

```bash
which cmsRun
echo $CMSSW_BASE
scramv1 runtime -sh
```

For this workspace, a successful setup looked like:

```text
/opt/cms/slc5_amd64_gcc434/cms/cmssw/CMSSW_4_4_7/bin/slc5_amd64_gcc434/cmsRun
/work/CMSSW_4_4_7
```

## 7. HIHighPt PbPb Data Starting Point

For first jet-quenching-oriented checks, start with CMS 2011 PbPb HIHighPt:

- Portal record: https://opendata.cern.ch/record/14013
- Dataset: `/HIHighPt/HIRun2011-15Apr2013-v1/RECO`
- Collision system: PbPb at 2.76 TeV
- Recommended release: `CMSSW_4_4_7`
- Recommended global tag: `GR_R_44_V15::All`
- Dataset size: 648 files, about 1.5 TiB total

List remote file locations from Windows PowerShell:

```powershell
$env:PYTHONUTF8='1'
.\.venv\Scripts\cernopendata-client.exe get-file-locations --recid 14013 --protocol xrootd
```

First XRootD file found during setup:

```text
root://eospublic.cern.ch//eos/opendata/cms/hidata/HIRun2011/HIHighPt/RECO/15Apr2013-v1/10000/0056B4D7-E8A5-E211-935E-003048F316C4.root
```

The files are large, usually several GB each, so prefer remote access first.

`edmFileUtil -d` may segfault in this old CMSSW/container combination. Use
`edmDumpEventContent` for the first access check instead:

```bash
edmDumpEventContent root://eospublic.cern.ch//eos/opendata/cms/hidata/HIRun2011/HIHighPt/RECO/15Apr2013-v1/10000/0056B4D7-E8A5-E211-935E-003048F316C4.root
```

To focus on jet-quenching-relevant products:

```bash
edmDumpEventContent root://eospublic.cern.ch//eos/opendata/cms/hidata/HIRun2011/HIHighPt/RECO/15Apr2013-v1/10000/0056B4D7-E8A5-E211-935E-003048F316C4.root | grep -E 'Centrality|ak.*Jet|TriggerResults|hiEvtPlane'
```

Or run the helper script from inside the CMS container:

```bash
cd /work
bash cms/check_hihighpt_content.sh
```

Useful products seen in the first file include:

```text
reco::Centrality                      "hiCentrality"      ""           "RECO"
vector<reco::EvtPlane>                "hiEvtPlane"        "recoLevel"  "RECO"
edm::TriggerResults                   "TriggerResults"    ""           "HLT"
vector<reco::CaloJet>                 "ak5CaloJets"       ""           "ppRECO"
vector<reco::PFJet>                   "ak5PFJets"         ""           "ppRECO"
vector<reco::CaloJet>                 "ak7CaloJets"       ""           "ppRECO"
vector<reco::PFJet>                   "ak7PFJets"         ""           "ppRECO"
```

An initial `cmsRun` inspection config is stored at:

```text
cms/inspect_hihighpt_cfg.py
```

## 8. First Mini Analyzer

The first CMSSW analyzer is stored in:

```text
cms/HiJetAnalysis/JetAnalyzer/plugins/HiJetAnalyzer.cc
```

It reads:

```text
vector<reco::PFJet> "ak5PFJets" "" "ppRECO"
```

and writes a compact output tree with:

```text
run, lumi, event, nJet,
lead_pt, lead_eta, lead_phi,
sublead_pt, sublead_eta, sublead_phi,
dphi, aj
```

Install and build the analyzer inside the CMS container:

```bash
cd /work
bash cms/install_hijet_analyzer.sh
```

Run the analyzer. The optional number controls `maxEvents`:

```bash
cd /work
bash cms/run_hijet_analyzer.sh 10
```

The optional second argument changes the output ROOT file name:

```bash
bash cms/run_hijet_analyzer.sh 10 hihighpt_jets_with_centrality.root
```

Output:

```text
results/hihighpt_jets.root
```

New analyzer output includes centrality activity branches after rebuilding the
analyzer:

```text
centrality_raw
hf_tower_sum
```

Remote RECO files can be slow. For quick checks, start with a small number:

```bash
bash cms/run_hijet_analyzer.sh 1
bash cms/run_hijet_analyzer.sh 3
```

After the ROOT output exists, leave the CMS container and plot from Windows
PowerShell:

```powershell
.\.venv\Scripts\python.exe src\plot_hijet_aj.py
```

Plot output:

```text
results/hihighpt_aj_hist.png
```

The first successful test read one remote HIHighPt event:

```text
run=181969
lumi=91
event=1180008
nJet=2
lead_pt=55.019
sublead_pt=31.783
dphi=3.082
aj=0.268
```

Important triggers listed for this dataset include:

```text
HLT_HIDiJet55
HLT_HIJet55
HLT_HIJet65
HLT_HIJet65_Jet55
HLT_HIJet80
HLT_HIJet95
```

## 9. Common pitfall

Do not run CMS work from the `docker-desktop` WSL distro. Its prompt looks like:

```text
docker-desktop:/tmp/...
```

Use Ubuntu instead:

```powershell
wsl -d Ubuntu
```

The expected Ubuntu prompt looks similar to:

```text
uno@hnoh:/mnt/c/Users/Administrator/Documents/my-work/my-work$
```

## 10. Repository setup on a new machine

After cloning this repository:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Then follow the WSL/Docker/CMS steps above.
