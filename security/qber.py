import numpy as np


def estimate_qber(
    alice_key,
    bob_key,
    sample_rate=0.20,
    threshold=0.11,
    seed=None
):
    if len(alice_key) != len(bob_key):
        raise ValueError("Alice and Bob keys must have the same length.")

    if not 0.0 < sample_rate <= 1.0:
        raise ValueError("Sample rate must be greater than 0 and at most 1.")

    if not 0.0 <= threshold <= 1.0:
        raise ValueError("Threshold must be between 0 and 1.")

    key_length = len(alice_key)

    if key_length == 0:
        raise ValueError("Sifted keys must not be empty.")

    rng = np.random.default_rng(seed)

    sample_size = max(1, int(np.ceil(key_length * sample_rate)))
    sample_size = min(sample_size, key_length)

    sample_indices = np.sort(
        rng.choice(key_length, size=sample_size, replace=False)
    )

    sample_index_set = set(sample_indices.tolist())

    error_count = sum(
        int(alice_key[index]) != int(bob_key[index])
        for index in sample_indices
    )

    qber = error_count / sample_size

    remaining_indices = [
        index
        for index in range(key_length)
        if index not in sample_index_set
    ]

    alice_remaining_key = [
        int(alice_key[index])
        for index in remaining_indices
    ]

    bob_remaining_key = [
        int(bob_key[index])
        for index in remaining_indices
    ]

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
