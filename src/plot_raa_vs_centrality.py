"""Plot an integrated jet R_AA proxy versus HF-activity centrality bins."""

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
PT_LOW = 1.0
PT_HIGH = 30.0
OUTPUT_PATH = Path("results/raa_proxy_vs_centrality_pt1_30.png")
SUMMARY_PATH = Path("results/raa_proxy_vs_centrality_pt1_30.csv")


def load_arrays(path: Path, required: list[str]):
    if not path.exists():
        raise SystemExit(f"Missing {path}")
    tree = uproot.open(path)[TREE_PATH]
    missing = [branch for branch in required if branch not in tree.keys()]
    if missing:
        raise SystemExit(f"Missing branches in {path}: {', '.join(missing)}")
    return tree.arrays(required, library="ak"), tree.num_entries


def count_jets_in_range(jet_pt, mask=None) -> int:
    jets = jet_pt if mask is None else jet_pt[mask]
    flat = ak.flatten(jets)
    return int(ak.sum((flat > PT_LOW) & (flat < PT_HIGH)))


def main() -> None:
    pbpb, _ = load_arrays(PBPB_PATH, ["hf_tower_sum", "jet_pt"])
    pp, pp_events = load_arrays(PP_PATH, ["jet_pt"])

    pp_count = count_jets_in_range(pp["jet_pt"])
    pp_yield = pp_count / pp_events
    if pp_yield == 0:
        raise SystemExit(f"No pp jets found in {PT_LOW} < pT < {PT_HIGH} GeV")

    hf = pbpb["hf_tower_sum"]
    valid = hf >= 0
    valid_hf = ak.to_numpy(hf[valid])
    edges = np.quantile(valid_hf, np.linspace(0.0, 1.0, 6))

    rows = []
    labels = []
    values = []
    errors = []

    for i in range(len(edges) - 1):
        low = edges[i]
        high = edges[i + 1]
        if i == len(edges) - 2:
            mask = valid & (hf >= low) & (hf <= high)
        else:
            mask = valid & (hf >= low) & (hf < high)

        events = int(ak.sum(mask))
        pbpb_count = count_jets_in_range(pbpb["jet_pt"], mask)
        pbpb_yield = pbpb_count / events if events else np.nan
        raa_proxy = pbpb_yield / pp_yield if pp_yield else np.nan
        # Poisson counting uncertainty for a first visual guide.
        rel_pbpb = 1.0 / np.sqrt(pbpb_count) if pbpb_count else 0.0
        rel_pp = 1.0 / np.sqrt(pp_count) if pp_count else 0.0
        error = raa_proxy * np.sqrt(rel_pbpb**2 + rel_pp**2)

        label = f"{i + 1}\n{low:.0f}-{high:.0f}"
        labels.append(label)
        values.append(raa_proxy)
        errors.append(error)
        rows.append(
            {
                "centrality_proxy_bin": i + 1,
                "hf_low": low,
                "hf_high": high,
                "pbpb_events": events,
                "pbpb_jet_count_1_30": pbpb_count,
                "pbpb_yield_per_event": pbpb_yield,
                "pp_events": pp_events,
                "pp_jet_count_1_30": pp_count,
                "pp_yield_per_event": pp_yield,
                "raa_proxy": raa_proxy,
                "raa_proxy_stat_error": error,
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    x = np.arange(len(values))
    fig, ax = plt.subplots(figsize=(7.2, 4.7))
    ax.errorbar(x, values, yerr=errors, fmt="o-", linewidth=2, capsize=4)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("HF activity quantile bin, peripheral-like to central-like")
    ax.set_ylabel(f"R_AA proxy, {PT_LOW:g} < jet pT < {PT_HIGH:g} GeV")
    ax.set_title("Integrated jet R_AA proxy vs centrality proxy")
    ax.grid(alpha=0.25)
    fig.savefig(OUTPUT_PATH, dpi=160, bbox_inches="tight")
    plt.close(fig)

    pd.DataFrame(rows).to_csv(SUMMARY_PATH, index=False)
    print(f"PbPb file: {PBPB_PATH}")
    print(f"pp file: {PP_PATH}")
    print(f"pp jets in {PT_LOW:g}-{PT_HIGH:g} GeV: {pp_count}")
    print(f"Saved plot: {OUTPUT_PATH}")
    print(f"Saved summary: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
