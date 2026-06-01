"""Plot A_J from the HIHighPt mini-analyzer output."""

from pathlib import Path

import awkward as ak
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import uproot


INPUT_PATH = Path("results/hihighpt_jets.root")
OUTPUT_PATH = Path("results/hihighpt_aj_hist.png")


def main() -> None:
    if not INPUT_PATH.exists():
        raise SystemExit(
            f"Missing {INPUT_PATH}. Run the CMSSW analyzer first, for example: "
            "bash cms/run_hijet_analyzer.sh 10"
        )

    tree = uproot.open(INPUT_PATH)["hiJets/jets"]
    arrays = tree.arrays(["aj", "dphi", "lead_pt", "sublead_pt"], library="ak")

    aj = ak.to_numpy(arrays["aj"])
    selected = aj[aj >= 0.0]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(selected, bins=np.linspace(0.0, 1.0, 31), color="#4267ac", edgecolor="white")
    ax.set_xlabel("A_J = (pT1 - pT2) / (pT1 + pT2)")
    ax.set_ylabel("Events")
    ax.set_title(f"HIHighPt dijet imbalance ({len(selected)} selected events)")
    ax.grid(alpha=0.25)
    fig.savefig(OUTPUT_PATH, dpi=160, bbox_inches="tight")
    plt.close(fig)

    print(f"Read entries: {tree.num_entries}")
    print(f"Selected entries with two jets: {len(selected)}")
    print(f"Saved plot: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
