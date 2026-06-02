"""Compare PbPb selected-jet pT spectra by HF-activity centrality proxy."""

from pathlib import Path
import sys

import awkward as ak
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import uproot


DEFAULT_INPUT_PATH = Path("results/hihighpt_jets_inclusive_300.root")
TREE_PATH = "hiJets/jets"
COUNT_OUTPUT = Path("results/pbpb_centrality_jet_pt_compare.png")
PER_EVENT_OUTPUT = Path("results/pbpb_centrality_jet_pt_per_event_compare.png")
SUMMARY_OUTPUT = Path("results/pbpb_centrality_jet_pt_summary.txt")


def load_arrays(path: Path):
    if not path.exists():
        raise SystemExit(f"Missing {path}")
    tree = uproot.open(path)[TREE_PATH]
    required = ["hf_tower_sum", "jet_pt"]
    missing = [column for column in required if column not in tree.keys()]
    if missing:
        raise SystemExit(f"Missing branches in {path}: {', '.join(missing)}")
    arrays = tree.arrays(required, library="ak")
    return arrays, tree.num_entries


def selected_jets(arrays, mask) -> np.ndarray:
    return ak.to_numpy(ak.flatten(arrays["jet_pt"][mask]))


def draw_step(ax, values: np.ndarray, bins, denominator: int, label: str) -> None:
    counts, edges = np.histogram(values, bins=bins)
    centers = 0.5 * (edges[:-1] + edges[1:])
    ax.step(centers, counts / denominator, where="mid", linewidth=2, label=label)


def decorate(ax, ylabel: str, title: str) -> None:
    ax.set_xlabel("Selected jet pT [GeV]")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)


def main() -> None:
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT_PATH
    arrays, total_events = load_arrays(input_path)

    hf = arrays["hf_tower_sum"]
    valid = hf >= 0
    valid_hf = ak.to_numpy(hf[valid])
    central_cut = np.quantile(valid_hf, 0.75)
    peripheral_cut = np.quantile(valid_hf, 0.25)

    central_mask = valid & (hf >= central_cut)
    peripheral_mask = valid & (hf <= peripheral_cut)
    central_jets = selected_jets(arrays, central_mask)
    peripheral_jets = selected_jets(arrays, peripheral_mask)
    central_events = int(ak.sum(central_mask))
    peripheral_events = int(ak.sum(peripheral_mask))

    bins = np.linspace(30.0, 300.0, 55)
    COUNT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    count_fig, count_ax = plt.subplots(figsize=(7.2, 4.7))
    count_ax.hist(
        peripheral_jets,
        bins=bins,
        histtype="step",
        linewidth=2,
        label=f"Peripheral-like (events={peripheral_events}, jets={len(peripheral_jets)})",
    )
    count_ax.hist(
        central_jets,
        bins=bins,
        histtype="step",
        linewidth=2,
        label=f"Central-like (events={central_events}, jets={len(central_jets)})",
    )
    decorate(count_ax, "Jets", "PbPb selected-jet pT by HF activity")
    count_fig.savefig(COUNT_OUTPUT, dpi=160, bbox_inches="tight")
    plt.close(count_fig)

    per_event_fig, per_event_ax = plt.subplots(figsize=(7.2, 4.7))
    draw_step(
        per_event_ax,
        peripheral_jets,
        bins,
        peripheral_events,
        f"Peripheral-like, HF <= {peripheral_cut:.1f}",
    )
    draw_step(
        per_event_ax,
        central_jets,
        bins,
        central_events,
        f"Central-like, HF >= {central_cut:.1f}",
    )
    decorate(
        per_event_ax,
        "Jets per event",
        "PbPb selected-jet pT per event by HF activity",
    )
    per_event_fig.savefig(PER_EVENT_OUTPUT, dpi=160, bbox_inches="tight")
    plt.close(per_event_fig)

    lines = [
        "PbPb centrality-proxy selected-jet pT comparison",
        f"Input: {input_path}",
        f"Total events: {total_events}",
        f"Peripheral-like cut: hf_tower_sum <= {peripheral_cut:.3f}",
        f"Central-like cut: hf_tower_sum >= {central_cut:.3f}",
        f"Peripheral-like events: {peripheral_events}",
        f"Central-like events: {central_events}",
        f"Peripheral-like jets: {len(peripheral_jets)}",
        f"Central-like jets: {len(central_jets)}",
        f"Peripheral-like mean jet pT: {peripheral_jets.mean():.3f} GeV",
        f"Central-like mean jet pT: {central_jets.mean():.3f} GeV",
        f"Saved plot: {COUNT_OUTPUT}",
        f"Saved plot: {PER_EVENT_OUTPUT}",
    ]
    SUMMARY_OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
