import pandas as pd
import pytest

from experiments.analyze_file_benchmark import (
    EXPECTED_TRIALS,
    FILE_TYPE_ORDER,
    SIZE_ORDER,
    validate_data
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
    validate_data(make_valid_benchmark())


def test_benchmark_validation_rejects_missing_trial():
    df = make_valid_benchmark().iloc[:-1].copy()
    with pytest.raises(ValueError, match="exactly 10 unique trials"):
        validate_data(df)


def test_benchmark_validation_rejects_non_success_or_failed_integrity():
    df = make_valid_benchmark()
    df.loc[0, "sha256_verified"] = False
    with pytest.raises(ValueError, match="SHA-256"):
        validate_data(df)


def test_benchmark_validation_rejects_non_finite_metrics():
    df = make_valid_benchmark()
    df.loc[0, "total_time_seconds"] = float("inf")
    with pytest.raises(ValueError, match="finite"):
        validate_data(df)
