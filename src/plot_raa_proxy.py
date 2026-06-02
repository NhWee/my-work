"""Build a first jet R_AA proxy from PbPb and pp mini-analyzer outputs."""

from pathlib import Path

import awkward as ak
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import uproot


TREE_PATH = "hiJets/jets"
PBPB_PATH = Path("results/hihighpt_jets_inclusive_300.root")
PP_PATH = Path("results/pp2760_jets_2000.root")
SPECTRUM_OUTPUT = Path("results/raa_proxy_spectra_per_event.png")
RATIO_OUTPUT = Path("results/raa_proxy_ratio.png")
SUMMARY_OUTPUT = Path("results/raa_proxy_summary.csv")


def load_tree_arrays(path: Path):
    if not path.exists():
        raise SystemExit(f"Missing {path}")

    tree = uproot.open(path)[TREE_PATH]
    missing = [name for name in ["jet_pt"] if name not in tree.keys()]
    if missing:
        raise SystemExit(f"Missing branches in {path}: {', '.join(missing)}")

    branches = ["jet_pt"]
    if "hf_tower_sum" in tree.keys():
        branches.append("hf_tower_sum")
    return tree.arrays(branches, library="ak"), tree.num_entries


def flatten_jets(arrays, mask=None) -> np.ndarray:
    jets = arrays["jet_pt"] if mask is None else arrays["jet_pt"][mask]
    return ak.to_numpy(ak.flatten(jets))


def histogram_per_event(jets: np.ndarray, bins: np.ndarray, events: int) -> np.ndarray:
    counts, _ = np.histogram(jets, bins=bins)
    return counts / events


def ratio_with_empty_bins(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    ratio = np.full_like(numerator, np.nan, dtype=float)
    np.divide(numerator, denominator, out=ratio, where=denominator > 0)
    return ratio


def step(ax, centers: np.ndarray, values: np.ndarray, label: str) -> None:
    ax.step(centers, values, where="mid", linewidth=2, label=label)


def decorate(ax, ylabel: str, title: str) -> None:
    ax.set_xlabel("Selected jet pT [GeV]")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)


def main() -> None:
    pbpb, pbpb_events = load_tree_arrays(PBPB_PATH)
    pp, pp_events = load_tree_arrays(PP_PATH)

    hf = pbpb["hf_tower_sum"]
    valid_hf = hf >= 0
    central_cut = np.quantile(ak.to_numpy(hf[valid_hf]), 0.75)
    peripheral_cut = np.quantile(ak.to_numpy(hf[valid_hf]), 0.25)
    central_mask = valid_hf & (hf >= central_cut)
    peripheral_mask = valid_hf & (hf <= peripheral_cut)

    samples = {
        "PbPb all": (flatten_jets(pbpb), pbpb_events),
        "PbPb peripheral-like": (
            flatten_jets(pbpb, peripheral_mask),
            int(ak.sum(peripheral_mask)),
        ),
        "PbPb central-like": (
            flatten_jets(pbpb, central_mask),
            int(ak.sum(central_mask)),
        ),
        "pp": (flatten_jets(pp), pp_events),
    }

    bins = np.array([30, 40, 50, 60, 80, 100, 140, 200, 300], dtype=float)
    centers = 0.5 * (bins[:-1] + bins[1:])
    pp_yield = histogram_per_event(samples["pp"][0], bins, samples["pp"][1])

    rows = []
    spectra_fig, spectra_ax = plt.subplots(figsize=(7.2, 4.7))
    ratio_fig, ratio_ax = plt.subplots(figsize=(7.2, 4.7))

    for label, (jets, events) in samples.items():
        yield_per_event = histogram_per_event(jets, bins, events)
        step(
            spectra_ax,
            centers,
            yield_per_event,
            f"{label} (events={events}, jets={len(jets)})",
        )

        if label.startswith("PbPb"):
            proxy = ratio_with_empty_bins(yield_per_event, pp_yield)
            step(ratio_ax, centers, proxy, label)
        else:
            proxy = np.full_like(yield_per_event, np.nan, dtype=float)

        counts, _ = np.histogram(jets, bins=bins)
        for i, center in enumerate(centers):
            rows.append(
                {
                    "sample": label,
                    "pt_low": bins[i],
                    "pt_high": bins[i + 1],
                    "pt_center": center,
                    "events": events,
                    "jet_count": int(counts[i]),
                    "yield_per_event": yield_per_event[i],
                    "raa_proxy_vs_pp": proxy[i],
                }
            )

    decorate(spectra_ax, "Jets per event", "PbPb and pp selected-jet pT spectra")
    ratio_ax.axhline(1.0, color="black", linewidth=1, linestyle="--")
    decorate(ratio_ax, "R_AA proxy vs pp", "First jet R_AA proxy")
    ratio_ax.set_ylim(0.0, 12.0)

    SPECTRUM_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    spectra_fig.savefig(SPECTRUM_OUTPUT, dpi=160, bbox_inches="tight")
    ratio_fig.savefig(RATIO_OUTPUT, dpi=160, bbox_inches="tight")
    plt.close(spectra_fig)
    plt.close(ratio_fig)

    summary = pd.DataFrame(rows)
    summary.to_csv(SUMMARY_OUTPUT, index=False)

    print(f"PbPb events: {pbpb_events}")
    print(f"pp events: {pp_events}")
    print(f"Peripheral-like HF <= {peripheral_cut:.3f}")
    print(f"Central-like HF >= {central_cut:.3f}")
    print(f"Saved plot: {SPECTRUM_OUTPUT}")
    print(f"Saved plot: {RATIO_OUTPUT}")
    print(f"Saved summary: {SUMMARY_OUTPUT}")


if __name__ == "__main__":
    main()
