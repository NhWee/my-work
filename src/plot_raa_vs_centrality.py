"""Plot an integrated jet R_AA proxy versus HF-activity centrality bins."""

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
PBPB_PATH = Path("results/hihighpt_jets_min1_100.root")
PP_PATH = Path("results/pp2760_jets_min1_1000.root")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot an integrated jet R_AA proxy versus centrality proxy."
    )
    parser.add_argument("--pbpb", type=Path, default=PBPB_PATH)
    parser.add_argument("--pp", type=Path, default=PP_PATH)
    parser.add_argument("--pt-low", type=float, default=1.0)
    parser.add_argument("--pt-high", type=float, default=30.0)
    parser.add_argument("--centrality-bins", type=int, default=5)
    parser.add_argument("--output-prefix", default=None)
    return parser.parse_args()


def load_arrays(path: Path, required: list[str]):
    if not path.exists():
        raise SystemExit(f"Missing {path}")
    tree = uproot.open(path)[TREE_PATH]
    missing = [branch for branch in required if branch not in tree.keys()]
    if missing:
        raise SystemExit(f"Missing branches in {path}: {', '.join(missing)}")
    return tree.arrays(required, library="ak"), tree.num_entries


def count_jets_in_range(jet_pt, pt_low: float, pt_high: float, mask=None) -> int:
    jets = jet_pt if mask is None else jet_pt[mask]
    flat = ak.flatten(jets)
    return int(ak.sum((flat > pt_low) & (flat < pt_high)))


def main() -> None:
    args = parse_args()
    output_prefix = args.output_prefix
    if output_prefix is None:
        output_prefix = f"raa_proxy_vs_centrality_pt{args.pt_low:g}_{args.pt_high:g}"
    output_path = Path("results") / f"{output_prefix}.png"
    summary_path = Path("results") / f"{output_prefix}.csv"

    pbpb, _ = load_arrays(args.pbpb, ["hf_tower_sum", "jet_pt"])
    pp, pp_events = load_arrays(args.pp, ["jet_pt"])

    pp_count = count_jets_in_range(pp["jet_pt"], args.pt_low, args.pt_high)
    pp_yield = pp_count / pp_events
    if pp_yield == 0:
        raise SystemExit(
            f"No pp jets found in {args.pt_low:g} < pT < {args.pt_high:g} GeV"
        )

    hf = pbpb["hf_tower_sum"]
    valid = hf >= 0
    valid_hf = ak.to_numpy(hf[valid])
    edges = np.quantile(valid_hf, np.linspace(0.0, 1.0, args.centrality_bins + 1))

    rows = []
    labels = []
    values = []
    errors = []

    # HF activity grows with centrality, while the conventional centrality
    # label runs from 0% most central to 100% most peripheral.
    for plot_index, edge_index in enumerate(reversed(range(len(edges) - 1))):
        low = edges[edge_index]
        high = edges[edge_index + 1]
        if edge_index == len(edges) - 2:
            mask = valid & (hf >= low) & (hf <= high)
        else:
            mask = valid & (hf >= low) & (hf < high)

        events = int(ak.sum(mask))
        pbpb_count = count_jets_in_range(
            pbpb["jet_pt"], args.pt_low, args.pt_high, mask
        )
        pbpb_yield = pbpb_count / events if events else np.nan
        raa_proxy = pbpb_yield / pp_yield if pp_yield else np.nan
        # Poisson counting uncertainty for a first visual guide.
        rel_pbpb = 1.0 / np.sqrt(pbpb_count) if pbpb_count else 0.0
        rel_pp = 1.0 / np.sqrt(pp_count) if pp_count else 0.0
        error = raa_proxy * np.sqrt(rel_pbpb**2 + rel_pp**2)

        centrality_low = plot_index * 100 / args.centrality_bins
        centrality_high = (plot_index + 1) * 100 / args.centrality_bins
        label = f"{centrality_low:.0f}-{centrality_high:.0f}%"
        labels.append(label)
        values.append(raa_proxy)
        errors.append(error)
        rows.append(
            {
                "centrality_percent_low": centrality_low,
                "centrality_percent_high": centrality_high,
                "hf_low": low,
                "hf_high": high,
                "pbpb_events": events,
                "pt_low": args.pt_low,
                "pt_high": args.pt_high,
                "pbpb_jet_count": pbpb_count,
                "pbpb_yield_per_event": pbpb_yield,
                "pp_events": pp_events,
                "pp_jet_count": pp_count,
                "pp_yield_per_event": pp_yield,
                "raa_proxy": raa_proxy,
                "raa_proxy_stat_error": error,
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    x = np.arange(len(values))
    fig, ax = plt.subplots(figsize=(7.2, 4.7))
    ax.errorbar(x, values, yerr=errors, fmt="o-", linewidth=2, capsize=4)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Centrality proxy percentile, 0% = most central")
    ax.set_ylabel(
        f"R_AA proxy, {args.pt_low:g} < jet pT < {args.pt_high:g} GeV"
    )
    ax.set_title("Integrated jet R_AA proxy vs centrality proxy")
    ax.grid(alpha=0.25)
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    pd.DataFrame(rows).to_csv(summary_path, index=False)
    print(f"PbPb file: {args.pbpb}")
    print(f"pp file: {args.pp}")
    print(f"pp jets in {args.pt_low:g}-{args.pt_high:g} GeV: {pp_count}")
    print(f"Saved plot: {output_path}")
    print(f"Saved summary: {summary_path}")


if __name__ == "__main__":
    main()
