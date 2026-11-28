import pandas as pd
import pytest

from experiments.analyze_file_benchmark import (
    EXPECTED_TRIALS,
    FILE_TYPE_ORDER,
    SIZE_ORDER,
    validate_data,
    build_summary
)


def make_valid_benchmark():
    rows = []
    for file_type in FILE_TYPE_ORDER:
        for size_label in SIZE_ORDER:
            for trial in range(1, EXPECTED_TRIALS + 1):
                rows.append({
                    "trial": trial,
                    "file_name": f"{file_type[1:]}_{size_label}",
                    "file_type": file_type,
                    "size_label": size_label,
                    "file_size_bytes": 1024,
                    "sha256_verified": True,
                    "status": "SUCCESS",
                    "encryption_time_seconds": 0.01,
                    "decryption_time_seconds": 0.01,
                    "encryption_throughput_mib_s": 1.0,
                    "decryption_throughput_mib_s": 1.0,
                    "total_time_seconds": 0.1,
                    "qber_percent": 0.0
                })
    return pd.DataFrame(rows)


def test_benchmark_validation_accepts_complete_ten_trial_dataset():
    df = make_valid_benchmark()
    validate_data(df)
    assert df["performance_eligible"].all()


def test_benchmark_validation_rejects_missing_trial():
    df = make_valid_benchmark().iloc[:-1].copy()
    with pytest.raises(ValueError, match="exactly 10 unique trials"):
        validate_data(df)


def test_benchmark_validation_rejects_non_finite_metrics():
    df = make_valid_benchmark()
    df.loc[0, "total_time_seconds"] = float("inf")
    with pytest.raises(ValueError, match="finite"):
        validate_data(df)


def test_mixed_status_and_integrity_rows_are_preserved_but_excluded_from_performance(tmp_path):
    df = make_valid_benchmark()
    df.loc[0, "status"] = "ABORT"
    df.loc[1, "status"] = "ERROR"
    df.loc[2, "sha256_verified"] = False

    validate_data(df)
    assert len(df) == 350
    assert int(df["performance_eligible"].sum()) == 347

    by_size, _ = build_summary(df, tmp_path)
    one_kb = by_size[by_size["size_label"].astype(str) == "1KB"].iloc[0]
    assert one_kb["n"] == 67
    assert one_kb["total_mean"] == pytest.approx(0.1)


def test_group_without_valid_performance_records_does_not_get_zero_timings(tmp_path):
    df = make_valid_benchmark()
    mask = (df["file_type"] == ".txt") & (df["size_label"] == "1KB")
    df.loc[mask, "status"] = "ABORT"

    validate_data(df)
    _, by_type_size = build_summary(df, tmp_path)
    row = by_type_size[
        (by_type_size["file_type"].astype(str) == ".txt")
        & (by_type_size["size_label"].astype(str) == "1KB")
    ].iloc[0]
    assert row["n"] == 0
    assert pd.isna(row["total_time_seconds_mean"])
