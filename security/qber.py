import numpy as np


def _validate_binary_key(key, name):
    try:
        values = np.asarray(key)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a one-dimensional binary sequence.") from exc

    if values.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional binary sequence.")

    if not np.all(np.isin(values, [0, 1])):
        raise ValueError(f"{name} must contain only 0 and 1.")

    return values.astype(np.uint8, copy=False)


def estimate_qber(
    alice_key,
    bob_key,
    sample_rate=0.20,
    threshold=0.11,
    seed=None
):
    alice = _validate_binary_key(alice_key, "Alice key")
    bob = _validate_binary_key(bob_key, "Bob key")

    if len(alice) != len(bob):
        raise ValueError("Alice and Bob keys must have the same length.")

    if not 0.0 < sample_rate <= 1.0:
        raise ValueError("Sample rate must be greater than 0 and at most 1.")

    if not 0.0 <= threshold <= 1.0:
        raise ValueError("Threshold must be between 0 and 1.")

    key_length = len(alice)

    if key_length == 0:
        raise ValueError("Sifted keys must not be empty.")

    rng = np.random.default_rng(seed)

    sample_size = max(1, int(np.ceil(key_length * sample_rate)))
    sample_size = min(sample_size, key_length)

    sample_indices = np.sort(
        rng.choice(key_length, size=sample_size, replace=False)
    )

    sample_index_set = set(sample_indices.tolist())
    error_count = int(np.count_nonzero(alice[sample_indices] != bob[sample_indices]))
    qber = error_count / sample_size

    remaining_indices = [
        index for index in range(key_length)
        if index not in sample_index_set
    ]

    alice_remaining_key = alice[remaining_indices].tolist()
    bob_remaining_key = bob[remaining_indices].tolist()
    accepted = qber <= threshold

    return {
        "key_length": key_length,
        "sample_size": sample_size,
        "error_count": error_count,
        "qber": qber,
        "threshold": threshold,
        "accepted": accepted,
        "alice_remaining_key": alice_remaining_key,
        "bob_remaining_key": bob_remaining_key,
        "remaining_length": len(remaining_indices)
    }
