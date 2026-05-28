"""Inspect ROOT files with uproot.

Usage:
    python src/inspect_root.py results/example.root
"""

import argparse
from pathlib import Path

import awkward as ak
import uproot


def print_tree_preview(tree: uproot.behaviors.TTree.TTree, limit: int) -> None:
    print(f"  entries: {tree.num_entries}")
    print("  branches:")
    for branch_name, branch in tree.items():
        print(f"    - {branch_name}: {branch.typename}")

    if tree.num_entries == 0:
        return

    stop = min(limit, tree.num_entries)
    arrays = tree.arrays(entry_stop=stop, library="ak")
    print(f"  preview: first {stop} entries")
    for index, row in enumerate(ak.to_list(arrays), start=1):
        print(f"    {index}: {row}")


def inspect_root_file(path: Path, limit: int) -> None:
    if not path.exists():
        raise FileNotFoundError(f"ROOT file not found: {path}")

    with uproot.open(path) as root_file:
        keys = root_file.keys()
        print(f"file: {path}")
        print("keys:")
        for key in keys:
            print(f"- {key}")

        for key in keys:
            obj = root_file[key]
            class_name = obj.classname
            print()
            print(f"{key} ({class_name})")

            if hasattr(obj, "num_entries") and hasattr(obj, "arrays"):
                print_tree_preview(obj, limit)
            else:
                print("  preview: unsupported object type")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect a ROOT file.")
    parser.add_argument("path", type=Path, help="Path to a .root file")
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of entries to preview for each tree",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inspect_root_file(args.path, args.limit)


if __name__ == "__main__":
    main()
