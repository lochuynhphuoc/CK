import argparse
import csv
import time
from pathlib import Path

from file_transfer.transfer import transfer_file


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "data" / "benchmark" / "manifest.csv"
OUTPUT_DIR = PROJECT_ROOT / "results" / "file_benchmark"

FIELDNAMES = [
    "trial", "file_name", "file_type", "size_label", "file_size_bytes",
    "attacked_count", "attack_rate_percent", "qber_percent",
    "qber_threshold_percent", "bb84_status", "encryption_time_seconds",
    "decryption_time_seconds", "encryption_throughput_mib_s",
    "decryption_throughput_mib_s", "encrypted_size_bytes", "sha256_verified",
    "total_time_seconds", "status", "reason"
]


def calculate_throughput(size_bytes, elapsed_seconds):
    if elapsed_seconds <= 0:
        return 0.0
    return size_bytes / (1024 * 1024) / elapsed_seconds


def benchmark_file(manifest_row, trial=1):
    source_path = PROJECT_ROOT / manifest_row["file_path"]
    output_name = (
        f'{manifest_row["file_type"].replace(".", "")}_'
        f'{manifest_row["size_label"]}'
    )
    output_folder = OUTPUT_DIR / f"trial_{trial}" / output_name
    encrypted_path = output_folder / f"{source_path.name}.enc"
    decrypted_path = (
        output_folder / f"{source_path.stem}_decrypted{source_path.suffix}"
    )

    start_time = time.perf_counter()
    result = transfer_file(source_path, encrypted_path, decrypted_path)
    total_time = time.perf_counter() - start_time

    bb84 = result.get("bb84_metrics", {})
    encryption = result.get("encryption_metrics", {})
    decryption = result.get("decryption_metrics", {})
    integrity = result.get("integrity", {})
    file_size = result["file_size"]
    encryption_time = encryption.get("encryption_time", 0.0)
    decryption_time = decryption.get("decryption_time", 0.0)
    bb84_status = (
        "CONTINUE" if bb84.get("final_key_length") == 256 else "ABORT"
    )

    return {
        "trial": trial,
        "file_name": result["file_name"],
        "file_type": result["file_type"],
        "size_label": manifest_row["size_label"],
        "file_size_bytes": file_size,
        "attacked_count": bb84.get("attacked_count", 0),
        "attack_rate_percent": round(bb84.get("actual_attack_rate", 0.0) * 100, 2),
        "qber_percent": round(bb84.get("qber", 0.0) * 100, 2),
        "qber_threshold_percent": round(bb84.get("qber_threshold", 0.0) * 100, 2),
        "bb84_status": bb84_status,
        "encryption_time_seconds": round(encryption_time, 6),
        "decryption_time_seconds": round(decryption_time, 6),
        "encryption_throughput_mib_s": round(
            calculate_throughput(file_size, encryption_time), 4
        ),
        "decryption_throughput_mib_s": round(
            calculate_throughput(file_size, decryption_time), 4
        ),
        "encrypted_size_bytes": encryption.get("encrypted_size", 0),
        "sha256_verified": integrity.get("verified", False),
        "total_time_seconds": round(total_time, 6),
        "status": result["status"],
        "reason": result.get("reason") or ""
    }


def main():
    parser = argparse.ArgumentParser(
        description="BB84 and AES-256-GCM file benchmark"
    )
    parser.add_argument("--trials", type=int, default=1)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--output",
        type=str,
        default="results/file_benchmark/file_benchmark.csv"
    )
    args = parser.parse_args()

    if args.trials < 1:
        parser.error("--trials must be at least 1")
    if args.limit < 0:
        parser.error("--limit cannot be negative")
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}")

    with MANIFEST_PATH.open("r", newline="", encoding="utf-8-sig") as file:
        manifest = list(csv.DictReader(file))
    if not manifest:
        raise ValueError("Manifest contains no test files.")
    if args.limit > 0:
        manifest = manifest[:args.limit]

    output_path = Path(args.output).expanduser()
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("BB84 + AES-256-GCM FILE BENCHMARK")
    print("=" * 65)
    print("Files to process:", len(manifest))
    print("Trials per file:", args.trials)
    print("Eve attack: Disabled (expected)")
    print("Output:", output_path)

    total_runs = len(manifest) * args.trials
    completed_runs = 0
    with output_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        csv_file.flush()

        for trial in range(1, args.trials + 1):
            print("\n" + "=" * 65)
            print(f"TRIAL {trial}/{args.trials}")
            print("=" * 65)
            for index, row in enumerate(manifest, start=1):
                completed_runs += 1
                print(
                    f"\n[{completed_runs}/{total_runs}] "
                    f"Trial {trial} | File {index}/{len(manifest)}"
                )
                print("File:", row["file_name"])
                result = benchmark_file(row, trial=trial)
                writer.writerow(result)
                csv_file.flush()
                print("Size:", result["file_size_bytes"], "bytes")
                print("QBER:", result["qber_percent"], "%")
                print("BB84:", result["bb84_status"])
                print("Encryption:", result["encryption_time_seconds"], "seconds")
                print("Decryption:", result["decryption_time_seconds"], "seconds")
                print("SHA-256:", result["sha256_verified"])
                print("Status:", result["status"])

    print("\n" + "=" * 65)
    print("REPEATED BENCHMARK COMPLETED")
    print("=" * 65)
    print("Trials per file:", args.trials)
    print("Files per trial:", len(manifest))
    print("Total runs:", total_runs)
    print("CSV:", output_path)


if __name__ == "__main__":
    main()
