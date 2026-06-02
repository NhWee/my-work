"""Build a first jet R_AA proxy from PbPb and pp mini-analyzer outputs."""

import argparse
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a first jet R_AA proxy from PbPb and pp outputs."
    )
    parser.add_argument("--pbpb", type=Path, default=PBPB_PATH)
    parser.add_argument("--pp", type=Path, default=PP_PATH)
    parser.add_argument("--pt-low", type=float, default=30.0)
    parser.add_argument("--pt-high", type=float, default=300.0)
    parser.add_argument("--pt-bin-width", type=float, default=None)
    parser.add_argument("--output-prefix", default="raa_proxy")
    return parser.parse_args()


def make_bins(args: argparse.Namespace) -> np.ndarray:
    if args.pt_bin_width:
        return np.arange(
            args.pt_low,
            args.pt_high + args.pt_bin_width,
            args.pt_bin_width,
            dtype=float,
        )
    if args.pt_low == 30.0 and args.pt_high == 300.0:
        return np.array([30, 40, 50, 60, 80, 100, 140, 200, 300], dtype=float)
    return np.linspace(args.pt_low, args.pt_high, 26)


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
    args = parse_args()
    pbpb, pbpb_events = load_tree_arrays(args.pbpb)
    pp, pp_events = load_tree_arrays(args.pp)

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

    bins = make_bins(args)
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

    spectrum_output = Path("results") / f"{args.output_prefix}_spectra_per_event.png"
    ratio_output = Path("results") / f"{args.output_prefix}_ratio.png"
    summary_output = Path("results") / f"{args.output_prefix}_summary.csv"

    spectrum_output.parent.mkdir(parents=True, exist_ok=True)
    spectra_fig.savefig(spectrum_output, dpi=160, bbox_inches="tight")
    ratio_fig.savefig(ratio_output, dpi=160, bbox_inches="tight")
    plt.close(spectra_fig)
    plt.close(ratio_fig)

    summary = pd.DataFrame(rows)
    summary.to_csv(summary_output, index=False)

    print(f"PbPb events: {pbpb_events}")
    print(f"pp events: {pp_events}")
    print(f"PbPb file: {args.pbpb}")
    print(f"pp file: {args.pp}")
    print(f"pT range: {args.pt_low} to {args.pt_high} GeV")
    print(f"Peripheral-like HF <= {peripheral_cut:.3f}")
    print(f"Central-like HF >= {central_cut:.3f}")
    print(f"Saved plot: {spectrum_output}")
    print(f"Saved plot: {ratio_output}")
    print(f"Saved summary: {summary_output}")


if __name__ == "__main__":
    main()
