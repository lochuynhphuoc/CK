import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt

from config import QBER_THRESHOLD


def load_summary(path):
    csv_path = Path(path)

    if not csv_path.is_file():
        raise FileNotFoundError(
            f"Summary CSV not found: {csv_path}. "
            "Run the experiments before generating charts."
        )

    with csv_path.open("r", newline="", encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError("Summary CSV is empty.")

    required_columns = {
        "attack_probability",
        "mean_sample_qber",
        "std_sample_qber",
        "abort_rate",
        "trials"
    }

    missing = required_columns.difference(rows[0].keys())

    if missing:
        raise ValueError(
            "Summary CSV is missing columns: "
            + ", ".join(sorted(missing))
        )

    return rows


def generate_qber_chart(rows, output_path, threshold=QBER_THRESHOLD):
    attack_rates = [
        float(row["attack_probability"]) * 100
        for row in rows
    ]
    mean_qber = [
        float(row["mean_sample_qber"]) * 100
        for row in rows
    ]
    std_qber = [
        float(row["std_sample_qber"]) * 100
        for row in rows
    ]
    theoretical_qber = [
        float(row["attack_probability"]) * 25
        for row in rows
    ]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.errorbar(
        attack_rates,
        mean_qber,
        yerr=std_qber,
        marker="o",
        capsize=4,
        linewidth=2,
        label="Measured mean QBER ± standard deviation"
    )
    ax.plot(
        attack_rates,
        theoretical_qber,
        linestyle="--",
        marker="",
        linewidth=1.8,
        label="Theoretical QBER (25% × attack probability)"
    )
    ax.axhline(
        threshold * 100,
        linestyle=":",
        linewidth=2,
        label=f"Abort threshold ({threshold:.0%})"
    )

    ax.set(
        title="BB84: Eve Attack Probability vs QBER",
        xlabel="Eve attack probability (%)",
        ylabel="QBER (%)",
        xticks=attack_rates,
        xlim=(-2, 102),
        ylim(bottom=0)
    )
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path


def generate_abort_chart(rows, output_path):
    attack_rates = [
        float(row["attack_probability"]) * 100
        for row in rows
    ]
    abort_rates = [
        float(row["abort_rate"]) * 100
        for row in rows
    ]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(
        [f"{rate:.0f}%" for rate in attack_rates],
        abort_rates,
        width=0.65
    )

    ax.bar_label(
        bars,
        labels=[f"{rate:.0f}%" for rate in abort_rates],
        padding=3
    )

    ax.set(
        title="BB84: Session Abort Rate by Eve Attack Probability",
        xlabel="Eve attack probability",
        ylabel="Aborted sessions (%)",
        ylim=(0, 110)
    )
    ax.grid(axis="y", alpha=0.3)
    ax.set_axisbelow(True)
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path


def generate_charts(
    input_path="results/qber_summary.csv",
    output_dir="results"
):
    rows = load_summary(input_path)
    output_path = Path(output_dir)

    qber_chart = generate_qber_chart(
        rows,
        output_path / "qber_vs_attack.png"
    )
    abort_chart = generate_abort_chart(
        rows,
        output_path / "abort_rate_vs_attack.png"
    )

    print("Charts generated successfully.")
    print(f"QBER chart      : {qber_chart}")
    print(f"Abort rate chart: {abort_chart}")

    return qber_chart, abort_chart


def main():
    parser = argparse.ArgumentParser(
        description="Generate charts from BB84 experiment summary CSV."
    )
    parser.add_argument(
        "--input",
        default="results/qber_summary.csv",
        help="Path to qber_summary.csv"
    )
    parser.add_argument(
        "--output-dir",
        default="results",
        help="Directory for generated chart images"
    )

    args = parser.parse_args()

    generate_charts(
        input_path=args.input,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
