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

## 6. Common pitfall

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

## 7. Repository setup on a new machine

After cloning this repository:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Then follow the WSL/Docker/CMS steps above.
