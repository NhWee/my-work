"""Compare A_J for central-like and peripheral-like HIHighPt events."""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import uproot


DEFAULT_INPUT_PATH = Path("results/hihighpt_jets_with_centrality.root")
TREE_PATH = "hiJets/jets"
OUTPUT_PATH = Path("results/hihighpt_centrality_aj_compare.png")
SUMMARY_PATH = Path("results/hihighpt_centrality_aj_summary.txt")


def load_events(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        raise SystemExit(f"Missing {input_path}")

    tree = uproot.open(input_path)[TREE_PATH]
    required = ["hf_tower_sum", "aj", "lead_pt", "sublead_pt", "dphi"]
    missing = [column for column in required if column not in tree.keys()]
    if missing:
        raise SystemExit(f"Missing branches in {input_path}: {', '.join(missing)}")

    return tree.arrays(required, library="pd")


def main() -> None:
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT_PATH
    df = load_events(input_path)

    dijets = df[df["aj"] >= 0.0].copy()
    if len(dijets) < 2:
        raise SystemExit("Not enough dijet events to compare centrality groups.")

    central_cut = dijets["hf_tower_sum"].quantile(0.75)
    peripheral_cut = dijets["hf_tower_sum"].quantile(0.25)
    central = dijets[dijets["hf_tower_sum"] >= central_cut]
    peripheral = dijets[dijets["hf_tower_sum"] <= peripheral_cut]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    bins = np.linspace(0.0, 1.0, 21)

    fig, ax = plt.subplots(figsize=(7.2, 4.7))
    ax.hist(
        peripheral["aj"],
        bins=bins,
        histtype="step",
        linewidth=2,
        density=True,
        color="#3565a8",
        label=f"Peripheral-like, HF <= {peripheral_cut:.1f} (n={len(peripheral)})",
    )
    ax.hist(
        central["aj"],
        bins=bins,
        histtype="step",
        linewidth=2,
        density=True,
        color="#b34539",
        label=f"Central-like, HF >= {central_cut:.1f} (n={len(central)})",
    )
    ax.set_xlabel("A_J = (pT1 - pT2) / (pT1 + pT2)")
    ax.set_ylabel("Normalized events")
    ax.set_title("HIHighPt A_J by HF activity quartile")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.savefig(OUTPUT_PATH, dpi=160, bbox_inches="tight")
    plt.close(fig)

    lines = [
        "HIHighPt centrality-proxy A_J comparison",
        f"Input: {input_path}",
        f"Total events: {len(df)}",
        f"Dijet events: {len(dijets)}",
        f"Peripheral-like cut: hf_tower_sum <= {peripheral_cut:.3f}",
        f"Central-like cut: hf_tower_sum >= {central_cut:.3f}",
        f"Peripheral-like events: {len(peripheral)}",
        f"Central-like events: {len(central)}",
        f"Peripheral-like mean A_J: {peripheral['aj'].mean():.3f}",
        f"Central-like mean A_J: {central['aj'].mean():.3f}",
        f"Saved plot: {OUTPUT_PATH}",
    ]
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
