"""Summarize selected-jet counts in one or more mini-analyzer ROOT files."""

from pathlib import Path
import sys

import awkward as ak
import uproot


TREE_PATH = "hiJets/jets"


def summarize(path: Path) -> dict[str, object]:
    tree = uproot.open(path)[TREE_PATH]
    branches = ["nJet", "jet_pt"]
    arrays = tree.arrays(branches, library="ak")
    jets = ak.flatten(arrays["jet_pt"])
    return {
        "file": str(path),
        "events": tree.num_entries,
        "events_njet_ge_1": int(ak.sum(arrays["nJet"] >= 1)),
        "events_njet_ge_2": int(ak.sum(arrays["nJet"] >= 2)),
        "selected_jets": len(jets),
        "jets_pt_gt_50": int(ak.sum(jets > 50)),
        "jets_pt_gt_100": int(ak.sum(jets > 100)),
        "mean_pt": float(ak.mean(jets)) if len(jets) else 0.0,
        "max_pt": float(ak.max(jets)) if len(jets) else 0.0,
    }


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python src/summarize_jet_outputs.py results/*.root")

    rows = [summarize(Path(arg)) for arg in sys.argv[1:]]
    headers = [
        "file",
        "events",
        "events_njet_ge_1",
        "events_njet_ge_2",
        "selected_jets",
        "jets_pt_gt_50",
        "jets_pt_gt_100",
        "mean_pt",
        "max_pt",
    ]
    print("\t".join(headers))
    for row in rows:
        print(
            "\t".join(
                f"{row[key]:.3f}" if isinstance(row[key], float) else str(row[key])
                for key in headers
            )
        )


if __name__ == "__main__":
    main()
