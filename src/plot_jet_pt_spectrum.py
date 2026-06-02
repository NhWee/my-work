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
COUNT_OUTPUT = Path("results/jet_pt_spectrum_compare.png")
PER_EVENT_OUTPUT = Path("results/jet_pt_spectrum_per_event_compare.png")


def read_jet_pt(path: Path) -> tuple[np.ndarray, int]:
    tree = uproot.open(path)[TREE_PATH]
    if "jet_pt" not in tree.keys():
        raise SystemExit(
            f"{path} does not contain jet_pt. Re-run the CMSSW analyzer after "
            "the inclusive jet branch update."
        )
    jet_pt = tree.arrays(["jet_pt"], library="ak")["jet_pt"]
    return ak.to_numpy(ak.flatten(jet_pt)), tree.num_entries


def decorate_axes(ax, ylabel: str, title: str) -> None:
    ax.set_xlabel("Selected jet pT [GeV]")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)


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

    count_fig, count_ax = plt.subplots(figsize=(7.2, 4.7))
    per_event_fig, per_event_ax = plt.subplots(figsize=(7.2, 4.7))
    for path in input_paths:
        jet_pt, entries = read_jet_pt(path)
        if len(jet_pt) == 0:
            print(f"{path}: no selected jets")
            continue
        label = f"{label_for(path)} (events={entries}, jets={len(jet_pt)})"
        count_ax.hist(
            jet_pt,
            bins=bins,
            histtype="step",
            linewidth=2,
            label=label,
        )
        counts, edges = np.histogram(jet_pt, bins=bins)
        centers = 0.5 * (edges[:-1] + edges[1:])
        per_event_ax.step(
            centers,
            counts / entries,
            where="mid",
            linewidth=2,
            label=label,
        )
        print(
            f"{path}: events={entries}, selected jets={len(jet_pt)}, "
            f"mean pT={jet_pt.mean():.3f} GeV"
        )

    decorate_axes(count_ax, "Jets", "Inclusive selected-jet pT spectrum")
    decorate_axes(
        per_event_ax,
        "Jets per event",
        "Inclusive selected-jet pT spectrum per event",
    )
    COUNT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    count_fig.savefig(COUNT_OUTPUT, dpi=160, bbox_inches="tight")
    per_event_fig.savefig(PER_EVENT_OUTPUT, dpi=160, bbox_inches="tight")
    plt.close(count_fig)
    plt.close(per_event_fig)
    print(f"Saved plot: {COUNT_OUTPUT}")
    print(f"Saved plot: {PER_EVENT_OUTPUT}")


if __name__ == "__main__":
    main()
