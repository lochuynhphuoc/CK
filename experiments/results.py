import csv
import statistics
from collections import defaultdict
from pathlib import Path


def summarize_results(rows):
    grouped = defaultdict(list)

    for row in rows:
        grouped[float(row["attack_probability"])].append(row)

    summaries = []

    for attack_probability in sorted(grouped):
        group = grouped[attack_probability]

        qber_values = [float(row["sample_qber"]) for row in group]
        actual_qber_values = [
            float(row["actual_sifted_qber"])
            for row in group
        ]

        accepted_count = sum(bool(row["accepted"]) for row in group)
        aborted_count = len(group) - accepted_count

        summaries.append({
            "attack_probability": attack_probability,
            "trials": len(group),
            "mean_actual_attack_rate": statistics.mean(
                float(row["actual_attack_rate"]) for row in group
            ),
            "mean_sample_qber": statistics.mean(qber_values),
            "std_sample_qber": (
                statistics.stdev(qber_values)
                if len(qber_values) > 1 else 0.0
            ),
            "mean_actual_sifted_qber": statistics.mean(
                actual_qber_values
            ),
            "accepted_sessions": accepted_count,
            "aborted_sessions": aborted_count,
            "abort_rate": aborted_count / len(group),
            "mean_sample_size": statistics.mean(
                int(row["sample_size"]) for row in group
            )
        })

    return summaries


def _write_csv(path, rows):
    if not rows:
        raise ValueError("Cannot write an empty result set.")

    fieldnames = list(rows[0].keys())

    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_experiment_results(rows, output_dir="results"):
    if not rows:
        raise ValueError("Cannot save an empty result set.")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    summary_rows = summarize_results(rows)

    raw_path = output_path / "qber_trials.csv"
    summary_path = output_path / "qber_summary.csv"

    _write_csv(raw_path, rows)
    _write_csv(summary_path, summary_rows)

    return raw_path, summary_path
