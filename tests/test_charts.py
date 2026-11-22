import csv

import matplotlib
matplotlib.use("Agg")

from visualization.charts import (
    generate_abort_chart,
    generate_qber_chart,
    load_summary
)


def test_qber_chart_uses_threshold_from_summary_and_handles_missing_qber(tmp_path):
    rows = [
        {
            "attack_probability": "0.0",
            "threshold": "0.05",
            "mean_sample_qber": "0.0",
            "std_sample_qber": "0.0"
        },
        {
            "attack_probability": "0.5",
            "threshold": "0.05",
            "mean_sample_qber": "",
            "std_sample_qber": ""
        }
    ]

    output = generate_qber_chart(rows, tmp_path / "qber.png")

    assert output.is_file()


def test_abort_chart_uses_numeric_positions_for_close_attack_rates(tmp_path):
    rows = [
        {"attack_probability": "0.10", "abort_rate": "0.2"},
        {"attack_probability": "0.101", "abort_rate": "0.3"}
    ]

    output = generate_abort_chart(rows, tmp_path / "abort.png")

    assert output.is_file()


def test_load_summary_requires_existing_summary(tmp_path):
    path = tmp_path / "summary.csv"
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "attack_probability", "mean_sample_qber",
                "std_sample_qber", "abort_rate", "trials"
            ]
        )
        writer.writeheader()
        writer.writerow({
            "attack_probability": 0,
            "mean_sample_qber": 0,
            "std_sample_qber": 0,
            "abort_rate": 0,
            "trials": 10
        })

    assert len(load_summary(path)) == 1
