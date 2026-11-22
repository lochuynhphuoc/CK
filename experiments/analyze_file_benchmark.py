import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = (
    PROJECT_ROOT / "results" / "file_benchmark" / "repeated"
    / "file_benchmark_repeated.csv"
)
SIZE_ORDER = ["1KB", "100KB", "1MB", "10MB", "50MB"]
FILE_TYPE_ORDER = [".txt", ".docx", ".png", ".jpg", ".wav", ".mp3", ".mp4"]
EXPECTED_TRIALS = 10

NUMERIC_METRICS = [
    "encryption_time_seconds", "decryption_time_seconds",
    "encryption_throughput_mib_s", "decryption_throughput_mib_s",
    "total_time_seconds", "qber_percent"
]
REQUIRED_COLUMNS = [
    "trial", "file_name", "file_type", "size_label", "file_size_bytes",
    "sha256_verified", "status", *NUMERIC_METRICS
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze repeated BB84 + AES-256-GCM file benchmark results."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def load_data(input_path):
    if not input_path.is_file():
        raise FileNotFoundError(
            f"Benchmark CSV not found: {input_path}\n"
            "Run experiments.file_benchmark first or pass --input."
        )

    df = pd.read_csv(input_path)
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(
            "CSV is missing required columns: " + ", ".join(missing_columns)
        )

    for column in NUMERIC_METRICS + ["trial", "file_size_bytes"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["sha256_verified"] = (
        df["sha256_verified"].astype(str).str.strip().str.lower()
        .map({
            "true": True, "1": True, "yes": True,
            "false": False, "0": False, "no": False
        })
    )
    df["file_type"] = df["file_type"].astype(str).str.lower()
    df["size_label"] = df["size_label"].astype(str)
    df["status"] = df["status"].astype(str).str.upper()
    return df


def validate_data(df):
    print("\n========== DATA VALIDATION ==========")
    print(f"Total records: {len(df)}")
    if df.empty:
        raise ValueError("The input CSV contains no benchmark records.")

    duplicate_mask = df.duplicated(subset=["trial", "file_name"], keep=False)
    print(f"Duplicate trial/file rows: {int(duplicate_mask.sum())}")

    group_sizes = df.groupby(["file_type", "size_label"])["trial"].nunique()
    print(f"File type × size groups: {len(group_sizes)}")
    if len(group_sizes):
        print(
            "Unique trials per group: "
            f"min={int(group_sizes.min())}, max={int(group_sizes.max())}"
        )

    missing_metrics = int(df[NUMERIC_METRICS].isna().sum().sum())
    print(f"Missing numeric metric values: {missing_metrics}")
    print("\nStatus counts:")
    print(df["status"].value_counts(dropna=False).to_string())
    print("\nSHA-256 verification:")
    print(df["sha256_verified"].value_counts(dropna=False).to_string())

    expected_pairs = {
        (file_type, size_label)
        for file_type in FILE_TYPE_ORDER
        for size_label in SIZE_ORDER
    }
    actual_pairs = set(zip(df["file_type"], df["size_label"]))
    if duplicate_mask.any():
        raise ValueError("Duplicate trial/file records were found.")
    if missing_metrics:
        raise ValueError("Missing or invalid numeric metric values were found.")
    if df["sha256_verified"].isna().any():
        raise ValueError("Some SHA-256 verification values could not be interpreted.")
    if not np.isfinite(df[["trial", "file_size_bytes", *NUMERIC_METRICS]].to_numpy(dtype=float)).all():
        raise ValueError("Benchmark numeric fields must contain finite values.")
    if (df["trial"] < 1).any() or not np.equal(df["trial"], np.floor(df["trial"])).all():
        raise ValueError("Trial numbers must be positive integers.")
    if (df["file_size_bytes"] <= 0).any():
        raise ValueError("File sizes must be positive.")
    if set(df["status"]) - {"SUCCESS"}:
        raise ValueError("Benchmark contains non-SUCCESS records.")
    if actual_pairs != expected_pairs:
        raise ValueError(
            "Benchmark must contain exactly the configured 7 file types × 5 sizes."
        )

    counts = df.groupby(["file_type", "size_label"])["trial"].agg(
        rows="size", unique_trials="nunique"
    )
    invalid_groups = counts[
        (counts["rows"] != EXPECTED_TRIALS)
        | (counts["unique_trials"] != EXPECTED_TRIALS)
    ]
    if not invalid_groups.empty:
        raise ValueError(
            f"Every file type × size group must contain exactly "
            f"{EXPECTED_TRIALS} unique trials."
        )

    if not df["sha256_verified"].all():
        raise ValueError("At least one benchmark record failed SHA-256 verification.")


def build_summary(df, output_dir):
    metric_aggregations = {}
    for metric in NUMERIC_METRICS:
        metric_aggregations[f"{metric}_mean"] = (metric, "mean")
        metric_aggregations[f"{metric}_sd"] = (metric, "std")
        metric_aggregations[f"{metric}_min"] = (metric, "min")
        metric_aggregations[f"{metric}_max"] = (metric, "max")

    by_type_size = (
        df.groupby(["file_type", "size_label"], observed=True)
        .agg(n=("trial", "count"), **metric_aggregations)
        .reset_index()
    )
    by_type_size["file_type"] = pd.Categorical(
        by_type_size["file_type"], FILE_TYPE_ORDER, ordered=True
    )
    by_type_size["size_label"] = pd.Categorical(
        by_type_size["size_label"], SIZE_ORDER, ordered=True
    )
    by_type_size = by_type_size.sort_values(["file_type", "size_label"])
    by_type_size.to_csv(
        output_dir / "benchmark_summary_by_type_size.csv",
        index=False, encoding="utf-8-sig"
    )

    by_size = (
        df.groupby("size_label", observed=True)
        .agg(
            n=("trial", "count"),
            encryption_mean=("encryption_time_seconds", "mean"),
            encryption_sd=("encryption_time_seconds", "std"),
            decryption_mean=("decryption_time_seconds", "mean"),
            decryption_sd=("decryption_time_seconds", "std"),
            enc_throughput_mean=("encryption_throughput_mib_s", "mean"),
            enc_throughput_sd=("encryption_throughput_mib_s", "std"),
            dec_throughput_mean=("decryption_throughput_mib_s", "mean"),
            dec_throughput_sd=("decryption_throughput_mib_s", "std"),
            total_mean=("total_time_seconds", "mean"),
            total_sd=("total_time_seconds", "std"),
            qber_mean=("qber_percent", "mean"),
            qber_sd=("qber_percent", "std")
        )
        .reset_index()
    )
    by_size["size_label"] = pd.Categorical(
        by_size["size_label"], SIZE_ORDER, ordered=True
    )
    by_size = by_size.sort_values("size_label")
    by_size.to_csv(
        output_dir / "benchmark_summary_by_size.csv",
        index=False, encoding="utf-8-sig"
    )

    by_type_size[by_type_size["size_label"].astype(str).eq("50MB")].to_csv(
        output_dir / "benchmark_summary_by_file_type_50MB.csv",
        index=False, encoding="utf-8-sig"
    )

    group_trial_counts = df.groupby(
        ["file_type", "size_label"], observed=True
    )["trial"].nunique()
    quality = pd.DataFrame([{
        "total_records": len(df),
        "unique_file_type_size_groups": len(group_trial_counts),
        "trials_per_group_min": int(group_trial_counts.min()),
        "trials_per_group_max": int(group_trial_counts.max()),
        "success_count": int((df["status"] == "SUCCESS").sum()),
        "abort_count": int((df["status"] == "ABORT").sum()),
        "error_count": int((df["status"] == "ERROR").sum()),
        "sha256_verified_count": int(df["sha256_verified"].eq(True).sum()),
        "sha256_failed_count": int(df["sha256_verified"].eq(False).sum()),
        "mean_qber_percent": float(df["qber_percent"].mean()),
        "mean_total_pipeline_seconds": float(df["total_time_seconds"].mean())
    }])
    quality.to_csv(
        output_dir / "benchmark_quality_check.csv",
        index=False, encoding="utf-8-sig"
    )
    return by_size, by_type_size


def save_charts(df, by_size, by_type_size, output_dir):
    sizes = by_size["size_label"].astype(str).tolist()
    x = np.arange(len(sizes))

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.errorbar(x, by_size["encryption_mean"],
                yerr=by_size["encryption_sd"].fillna(0),
                marker="o", capsize=4, label="Encryption")
    ax.errorbar(x, by_size["decryption_mean"],
                yerr=by_size["decryption_sd"].fillna(0),
                marker="s", capsize=4, label="Decryption")
    ax.set_xticks(x, sizes)
    ax.set_xlabel("File size")
    ax.set_ylabel("AES time (seconds)")
    ax.set_title("AES-256-GCM time by file size (mean ± SD)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "aes_time_vs_size_mean_sd.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.errorbar(x, by_size["enc_throughput_mean"],
                yerr=by_size["enc_throughput_sd"].fillna(0),
                marker="o", capsize=4, label="Encryption throughput")
    ax.errorbar(x, by_size["dec_throughput_mean"],
                yerr=by_size["dec_throughput_sd"].fillna(0),
                marker="s", capsize=4, label="Decryption throughput")
    ax.set_xticks(x, sizes)
    ax.set_xlabel("File size")
    ax.set_ylabel("Throughput (MiB/s)")
    ax.set_title("AES-256-GCM throughput by file size (mean ± SD)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "throughput_vs_size_mean_sd.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.errorbar(x, by_size["total_mean"],
                yerr=by_size["total_sd"].fillna(0),
                marker="o", capsize=4)
    ax.set_xticks(x, sizes)
    ax.set_xlabel("File size")
    ax.set_ylabel("Total pipeline time (seconds)")
    ax.set_title("BB84 + AES + integrity pipeline time (mean ± SD)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "total_pipeline_time_vs_size_mean_sd.png", dpi=180)
    plt.close(fig)

    for size_label in SIZE_ORDER:
        size_data = by_type_size[
            by_type_size["size_label"].astype(str).eq(size_label)
        ].copy()
        size_data["file_type"] = size_data["file_type"].astype(str)
        size_data = (
            size_data.set_index("file_type")
            .reindex(FILE_TYPE_ORDER)
            .reset_index()
        )
        x_type = np.arange(len(FILE_TYPE_ORDER))
        width = 0.36
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.bar(
            x_type - width / 2,
            size_data["encryption_time_seconds_mean"], width,
            yerr=size_data["encryption_time_seconds_sd"].fillna(0),
            capsize=3, label="Encryption"
        )
        ax.bar(
            x_type + width / 2,
            size_data["decryption_time_seconds_mean"], width,
            yerr=size_data["decryption_time_seconds_sd"].fillna(0),
            capsize=3, label="Decryption"
        )
        ax.set_xticks(x_type, FILE_TYPE_ORDER)
        ax.set_xlabel("File extension")
        ax.set_ylabel("Average AES time (seconds)")
        ax.set_title(
            f"AES-256-GCM time by file type at {size_label} (mean ± SD)"
        )
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend()
        fig.tight_layout()
        output_name = (
            "aes_time_by_file_type.png"
            if size_label == "50MB"
            else f"aes_time_by_file_type_{size_label}.png"
        )
        fig.savefig(output_dir / output_name, dpi=180)
        plt.close(fig)


def main():
    args = parse_args()
    input_path = args.input.expanduser().resolve()
    output_dir = (
        args.output.expanduser().resolve()
        if args.output else input_path.parent / "analysis"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    stale_summary = output_dir / "benchmark_summary_by_file_type.csv"
    if stale_summary.exists():
        stale_summary.unlink()

    df = load_data(input_path)
    validate_data(df)
    by_size, by_type_size = build_summary(df, output_dir)
    save_charts(df, by_size, by_type_size, output_dir)

    print("\n========== ANALYSIS COMPLETED ==========")
    print(f"Input CSV: {input_path}")
    print(f"Output directory: {output_dir}")
    print(f"Total records: {len(df)}")
    print("\nGenerated files:")
    for path in sorted(output_dir.iterdir()):
        if path.is_file():
            print(f"- {path.name}")
    print("\nSummary by size:")
    print(
        by_size[[
            "size_label", "n", "encryption_mean", "decryption_mean",
            "enc_throughput_mean", "dec_throughput_mean", "total_mean"
        ]].round(6).to_string(index=False)
    )


if __name__ == "__main__":
    main()
