"""Example ROOT-file workflow using uproot.

This works in the local Windows .venv without installing the full CERN ROOT
framework.
"""

from pathlib import Path

import awkward as ak
import numpy as np
import uproot


OUTPUT_PATH = Path("results/example.root")


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    energy = np.array([12.4, 18.1, 24.7, 31.2, 45.0])
    detector_id = np.array([1, 1, 2, 2, 3])
    hits = ak.Array([[1, 2], [3], [4, 5, 6], [], [7, 8]])

    with uproot.recreate(OUTPUT_PATH) as root_file:
        root_file["events"] = {
            "energy": energy,
            "detector_id": detector_id,
            "hits": hits,
        }

    with uproot.open(OUTPUT_PATH) as root_file:
        events = root_file["events"].arrays(library="ak")

    print(f"Wrote and read {OUTPUT_PATH}")
    print(events)
    print(f"Mean energy: {ak.mean(events['energy']):.2f}")


if __name__ == "__main__":
    main()
