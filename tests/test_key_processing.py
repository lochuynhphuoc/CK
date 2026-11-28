import pytest

from security.key_processing import (
    information_reconciliation,
    toeplitz_privacy_amplification
)


@pytest.mark.parametrize("invalid", [[256], [-1], [2], [0.5], ["0"], [[0, 1]]])
def test_information_reconciliation_rejects_invalid_bits(invalid):
    with pytest.raises(ValueError):
        information_reconciliation(invalid, [0] * len(invalid))


@pytest.mark.parametrize("invalid", [[256], [-1], [2], [0.5], ["1"], [[0, 1]]])
def test_toeplitz_rejects_invalid_bits_before_uint8_conversion(invalid):
    with pytest.raises(ValueError):
        toeplitz_privacy_amplification(invalid, output_length=1)


def test_information_reconciliation_accepts_numpy_arrays():
    import numpy as np

    result = information_reconciliation(
        np.zeros(16, dtype=np.uint8),
        np.zeros(16, dtype=np.uint8),
        seed=7
    )
    assert result["success"] is True
