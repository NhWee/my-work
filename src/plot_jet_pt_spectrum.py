"""Plot inclusive selected-jet pT spectra from mini-analyzer outputs."""

from pathlib import Path
import sys

import awkward as ak
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import uproot


TREE_PATH = "hiJets/jets"
DEFAULT_OUTPUT = Path("results/jet_pt_spectrum_compare.png")


def read_jet_pt(path: Path) -> np.ndarray:
    tree = uproot.open(path)[TREE_PATH]
    if "jet_pt" not in tree.keys():
        raise SystemExit(
            f"{path} does not contain jet_pt. Re-run the CMSSW analyzer after "
            "the inclusive jet branch update."
        )
    jet_pt = tree.arrays(["jet_pt"], library="ak")["jet_pt"]
    return ak.to_numpy(ak.flatten(jet_pt))


def label_for(path: Path) -> str:
    name = path.stem
    if "pp" in name.lower():
        return f"pp {name}"
    if "hi" in name.lower() or "pbpb" in name.lower():
        return f"PbPb {name}"
    return name


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: python src/plot_jet_pt_spectrum.py "
            "results/pbpb.root [results/pp.root]"
        )

    input_paths = [Path(arg) for arg in sys.argv[1:]]
    bins = np.linspace(30.0, 300.0, 55)

    fig, ax = plt.subplots(figsize=(7.2, 4.7))
    for path in input_paths:
        jet_pt = read_jet_pt(path)
        if len(jet_pt) == 0:
            print(f"{path}: no selected jets")
            continue
        ax.hist(
            jet_pt,
            bins=bins,
            histtype="step",
            linewidth=2,
            label=f"{label_for(path)} (jets={len(jet_pt)})",
        )
        print(f"{path}: selected jets={len(jet_pt)}, mean pT={jet_pt.mean():.3f} GeV")

    ax.set_xlabel("Selected jet pT [GeV]")
    ax.set_ylabel("Jets")
    ax.set_title("Inclusive selected-jet pT spectrum")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(DEFAULT_OUTPUT, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved plot: {DEFAULT_OUTPUT}")


if __name__ == "__main__":
    main()
