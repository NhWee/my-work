"""Create quick summary plots and statistics for HIHighPt jet output."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import uproot


INPUT_PATH = Path("results/hihighpt_jets.root")
TREE_PATH = "hiJets/jets"
OUTPUT_DIR = Path("results")


def require_input() -> None:
    if not INPUT_PATH.exists():
        raise SystemExit(
            f"Missing {INPUT_PATH}. Run the CMSSW analyzer first, for example: "
            "bash cms/run_hijet_analyzer.sh 100"
        )


def save_hist(values, bins, xlabel: str, title: str, output_name: str) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(values, bins=bins, color="#3f6f73", edgecolor="white")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Events")
    ax.set_title(title)
    ax.grid(alpha=0.25)
    fig.savefig(OUTPUT_DIR / output_name, dpi=160, bbox_inches="tight")
    plt.close(fig)


def write_summary(df: pd.DataFrame, selected: pd.DataFrame) -> None:
    summary_path = OUTPUT_DIR / "hihighpt_summary.txt"
    lines = [
        "HIHighPt mini-analyzer summary",
        f"Input: {INPUT_PATH}",
        f"Total entries: {len(df)}",
        f"Events with nJet >= 2: {len(selected)}",
        f"Fraction with nJet >= 2: {len(selected) / len(df):.3f}" if len(df) else "",
        "",
    ]

    if len(selected):
        lines.extend(
            [
                "Selected events, nJet >= 2",
                f"mean lead_pt: {selected['lead_pt'].mean():.3f} GeV",
                f"mean sublead_pt: {selected['sublead_pt'].mean():.3f} GeV",
                f"mean dphi: {selected['dphi'].mean():.3f}",
                f"mean A_J: {selected['aj'].mean():.3f}",
                f"median A_J: {selected['aj'].median():.3f}",
                f"events with A_J > 0.3: {int((selected['aj'] > 0.3).sum())}",
                "",
                "Top 10 events by A_J",
                selected.sort_values("aj", ascending=False)
                .head(10)
                .to_string(index=False, float_format=lambda value: f"{value:.3f}"),
            ]
        )

    summary_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved summary: {summary_path}")


def main() -> None:
    require_input()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    columns = ["run", "lumi", "event", "nJet", "lead_pt", "sublead_pt", "dphi", "aj"]
    tree = uproot.open(INPUT_PATH)[TREE_PATH]
    df = tree.arrays(columns, library="pd")
    selected = df[df["aj"] >= 0.0].copy()

    save_hist(
        df["nJet"],
        bins=np.arange(-0.5, max(df["nJet"].max(), 1) + 1.5, 1),
        xlabel="Number of selected jets",
        title=f"HIHighPt jet multiplicity ({len(df)} events)",
        output_name="hihighpt_njet_hist.png",
    )

    if len(selected):
        save_hist(
            selected["lead_pt"],
            bins=np.linspace(0.0, max(selected["lead_pt"].max(), 250.0), 41),
            xlabel="Leading jet pT [GeV]",
            title=f"Leading jet pT ({len(selected)} dijet events)",
            output_name="hihighpt_lead_pt_hist.png",
        )
        save_hist(
            selected["sublead_pt"],
            bins=np.linspace(0.0, max(selected["sublead_pt"].max(), 160.0), 41),
            xlabel="Subleading jet pT [GeV]",
            title=f"Subleading jet pT ({len(selected)} dijet events)",
            output_name="hihighpt_sublead_pt_hist.png",
        )
        save_hist(
            selected["dphi"],
            bins=np.linspace(0.0, np.pi, 33),
            xlabel="Delta phi",
            title=f"Dijet delta phi ({len(selected)} dijet events)",
            output_name="hihighpt_dphi_hist.png",
        )
        save_hist(
            selected["aj"],
            bins=np.linspace(0.0, 1.0, 31),
            xlabel="A_J = (pT1 - pT2) / (pT1 + pT2)",
            title=f"Dijet imbalance ({len(selected)} dijet events)",
            output_name="hihighpt_aj_hist.png",
        )

    write_summary(df, selected)
    print(f"Read entries: {len(df)}")
    print(f"Selected entries with two jets: {len(selected)}")


if __name__ == "__main__":
    main()
