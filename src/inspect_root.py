"""Inspect ROOT files with uproot.

Usage:
    python src/inspect_root.py results/example.root
"""

import argparse
from pathlib import Path

import awkward as ak
import uproot


def print_tree_preview(
    tree: uproot.behaviors.TTree.TTree,
    limit: int,
    branches: list[str] | None,
) -> None:
    print(f"  entries: {tree.num_entries}")
    print("  branches:")
    for branch_name, branch in tree.items():
        print(f"    - {branch_name}: {branch.typename}")

    if tree.num_entries == 0:
        return

    stop = min(limit, tree.num_entries)
    arrays = tree.arrays(expressions=branches, entry_stop=stop, library="ak")
    print(f"  preview: first {stop} entries")
    for index, row in enumerate(ak.to_list(arrays), start=1):
        print(f"    {index}: {row}")


def is_url(path: str) -> bool:
    return path.startswith(("http://", "https://", "root://"))


def inspect_root_file(
    path: str,
    limit: int,
    tree_filter: str | None,
    branches: list[str] | None,
) -> None:
    if not is_url(path) and not Path(path).exists():
        raise FileNotFoundError(f"ROOT file not found: {path}")

    with uproot.open(path) as root_file:
        keys = root_file.keys()
        print(f"file: {path}")
        print("keys:")
        for key in keys:
            print(f"- {key}")

        for key in keys:
            if tree_filter is not None and key.split(";")[0] != tree_filter:
                continue

            obj = root_file[key]
            class_name = obj.classname
            print()
            print(f"{key} ({class_name})")

            if hasattr(obj, "num_entries") and hasattr(obj, "arrays"):
                try:
                    print_tree_preview(obj, limit, branches)
                except Exception as error:
                    print(f"  preview failed: {error}")
            else:
                print("  preview: unsupported object type")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect a ROOT file.")
    parser.add_argument("path", help="Path or URL to a .root file")
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of entries to preview for each tree",
    )
    parser.add_argument("--tree", help="Only inspect one tree, for example Events")
    parser.add_argument(
        "--branches",
        nargs="+",
        help="Only preview selected branches, for example Jet_pt Jet_eta",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inspect_root_file(args.path, args.limit, args.tree, args.branches)


if __name__ == "__main__":
    main()
