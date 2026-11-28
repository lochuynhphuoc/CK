import pytest

from experiments.results import summarize_results


def _trial(attack_probability, sample_qber, actual_qber, threshold=0.11):
    return {
        "attack_probability": attack_probability,
        "sample_qber": sample_qber,
        "actual_sifted_qber": actual_qber,
        "accepted": sample_qber is not None and sample_qber <= threshold,
        "actual_attack_rate": attack_probability,
        "sample_size": 0 if sample_qber is None else 10,
        "threshold": threshold
    }


def test_summary_handles_trials_with_empty_sifted_keys():
    rows = [
        _trial(0.0, None, None),
        _trial(0.0, 0.05, 0.04),
        _trial(0.0, 0.10, 0.08)
    ]

    summary = summarize_results(rows)[0]

    assert summary["trials"] == 3
    assert summary["sample_qber_valid_trials"] == 2
    assert summary["actual_qber_valid_trials"] == 2
    assert summary["mean_sample_qber"] == pytest.approx(0.075)
    assert summary["std_sample_qber"] == pytest.approx(0.035355339)
    assert summary["accepted_sessions"] == 2
    assert summary["aborted_sessions"] == 1
    assert summary["abort_rate"] == pytest.approx(1 / 3)


def test_summary_preserves_all_aborted_group_without_qber_values():
    summary = summarize_results([
        _trial(0.5, None, None),
        _trial(0.5, None, None)
    ])[0]

    assert summary["mean_sample_qber"] is None
    assert summary["std_sample_qber"] is None
    assert summary["mean_actual_sifted_qber"] is None
    assert summary["sample_qber_valid_trials"] == 0
    assert summary["aborted_sessions"] == 2
    assert summary["abort_rate"] == 1.0


def test_summary_rejects_mixed_thresholds():
    with pytest.raises(ValueError, match="same QBER threshold"):
        summarize_results([
            _trial(0.0, 0.0, 0.0, threshold=0.11),
            _trial(0.0, 0.0, 0.0, threshold=0.05)
        ])
