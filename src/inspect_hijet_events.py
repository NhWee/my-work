"""Print per-event rows from the HIHighPt mini-analyzer output."""

from pathlib import Path

import pandas as pd
import uproot


INPUT_PATH = Path("results/hihighpt_jets.root")
TREE_PATH = "hiJets/jets"


def main() -> None:
    if not INPUT_PATH.exists():
        raise SystemExit(
            f"Missing {INPUT_PATH}. Run the CMSSW analyzer first, for example: "
            "bash cms/run_hijet_analyzer.sh 10"
        )

    tree = uproot.open(INPUT_PATH)[TREE_PATH]
    columns = [
        "run",
        "lumi",
        "event",
    ]
    optional_columns = [
        "centrality_raw",
        "hf_tower_sum",
        "nJet",
        "lead_pt",
        "sublead_pt",
        "dphi",
        "aj",
    ]
    columns.extend(column for column in optional_columns if column in tree.keys())
    df = tree.arrays(columns, library="pd")

    print(f"File: {INPUT_PATH}")
    print(f"Tree: {TREE_PATH}")
    print(f"Entries: {len(df)}")
    print()
    print(df.to_string(index=False, float_format=lambda value: f"{value:.3f}"))


if __name__ == "__main__":
    main()
