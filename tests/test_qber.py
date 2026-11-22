import pytest

from security.qber import estimate_qber


def test_qber_zero_errors_accepts_session():
    result = estimate_qber(
        [0, 1, 0, 1], [0, 1, 0, 1],
        sample_rate=1.0, threshold=0.11, seed=1
    )
    assert result["sample_size"] == 4
    assert result["error_count"] == 0
    assert result["qber"] == 0.0
    assert result["accepted"] is True
    assert result["remaining_length"] == 0


def test_qber_detects_errors_and_aborts():
    result = estimate_qber(
        [0, 0, 0, 0], [1, 1, 0, 0],
        sample_rate=1.0, threshold=0.11, seed=1
    )
    assert result["error_count"] == 2
    assert result["qber"] == 0.5
    assert result["accepted"] is False


def test_qber_removes_sampled_bits_from_remaining_key():
    result = estimate_qber(
        [0, 1, 0, 1, 0], [0, 1, 0, 1, 0],
        sample_rate=0.4, threshold=0.11, seed=2
    )
    assert result["sample_size"] == 2
    assert result["remaining_length"] == 3


@pytest.mark.parametrize(
    "alice,bob,rate,threshold",
    [
        ([0], [0, 1], 0.2, 0.11),
        ([0], [0], 0.0, 0.11),
        ([0], [0], 1.1, 0.11),
        ([0], [0], 0.2, -0.1),
        ([0], [0], 0.2, 1.1),
        ([], [], 0.2, 0.11),
        ([256], [0], 0.2, 0.11),
        ([-1], [0], 0.2, 0.11),
        ([0.5], [0], 0.2, 0.11),
        ([0, 2], [0, 1], 0.2, 0.11),
        ([[0, 1]], [[0, 1]], 0.2, 0.11)
    ]
)
def test_qber_rejects_invalid_inputs(alice, bob, rate, threshold):
    with pytest.raises(ValueError):
        estimate_qber(alice, bob, sample_rate=rate, threshold=threshold)
