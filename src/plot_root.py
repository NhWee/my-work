"""Plot a branch from a ROOT file with uproot and matplotlib.

Usage:
    python src/plot_root.py results/example.root
"""

import argparse
from pathlib import Path
from urllib.parse import urlparse

import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
import uproot


def display_name(path_or_url: str) -> str:
    parsed = urlparse(path_or_url)
    if parsed.scheme:
        return Path(parsed.path).name
    return Path(path_or_url).name


def plot_branch(
    root_path: str,
    tree_name: str,
    branch_name: str,
    output_path: Path,
    bins: int,
) -> None:
    with uproot.open(root_path) as root_file:
        tree = root_file[tree_name]
        values = tree[branch_name].array(library="ak")

    values = np.asarray(ak.to_numpy(ak.flatten(values, axis=None)))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(values, bins=bins, color="#2f6fbb", edgecolor="white")
    ax.set_title(f"{branch_name} from {display_name(root_path)}")
    ax.set_xlabel(branch_name)
    ax.set_ylabel("Events")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)

    print(f"Saved plot: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot a ROOT tree branch.")
    parser.add_argument("root_path", help="Path or URL to a .root file")
    parser.add_argument("--tree", default="events", help="Tree name")
    parser.add_argument("--branch", default="energy", help="Branch name")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/energy_hist.png"),
        help="Output image path",
    )
    parser.add_argument("--bins", type=int, default=8, help="Histogram bins")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    plot_branch(args.root_path, args.tree, args.branch, args.output, args.bins)


if __name__ == "__main__":
    main()
