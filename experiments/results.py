import csv
import statistics
from collections import defaultdict
from pathlib import Path


def _mean_or_none(values):
    return statistics.mean(values) if values else None


def _stdev_or_none(values):
    return statistics.stdev(values) if len(values) > 1 else (
        0.0 if values else None
    )


def summarize_results(rows):
    if not rows:
        raise ValueError("Cannot summarize an empty result set.")

    grouped = defaultdict(list)

    for row in rows:
        grouped[float(row["attack_probability"])].append(row)

    thresholds = {float(row["threshold"]) for row in rows}
    if len(thresholds) != 1:
        raise ValueError("All trials in one experiment must use the same QBER threshold.")
    experiment_threshold = thresholds.pop()

    summaries = []

    for attack_probability in sorted(grouped):
        group = grouped[attack_probability]

        qber_values = [
            float(row["sample_qber"])
            for row in group
            if row["sample_qber"] is not None
        ]
        actual_qber_values = [
            float(row["actual_sifted_qber"])
            for row in group
            if row["actual_sifted_qber"] is not None
        ]

        accepted_count = sum(bool(row["accepted"]) for row in group)
        aborted_count = len(group) - accepted_count

        summaries.append({
            "attack_probability": attack_probability,
            "threshold": experiment_threshold,
            "trials": len(group),
            "mean_actual_attack_rate": statistics.mean(
                float(row["actual_attack_rate"]) for row in group
            ),
            "mean_sample_qber": _mean_or_none(qber_values),
            "std_sample_qber": _stdev_or_none(qber_values),
            "sample_qber_valid_trials": len(qber_values),
            "mean_actual_sifted_qber": _mean_or_none(actual_qber_values),
            "actual_qber_valid_trials": len(actual_qber_values),
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
