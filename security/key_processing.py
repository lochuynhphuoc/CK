import numpy as np


def _validated_bits(values, name):
    try:
        bits = np.asarray(values)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a one-dimensional binary sequence.") from exc

    if bits.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional binary sequence.")

    if not np.all(np.isin(bits, [0, 1])):
        raise ValueError(f"{name} must contain only 0 and 1.")

    return bits.astype(np.uint8, copy=True)


def _parity(bits):
    return int(np.sum(bits) % 2)


def _reconcile_block(alice_key, bob_key, indices):
    alice_parity = _parity(alice_key[indices])
    bob_parity = _parity(bob_key[indices])
    disclosed_bits = 1

    if alice_parity == bob_parity:
        return False, disclosed_bits

    left = indices.copy()

    while len(left) > 1:
        middle = len(left) // 2
        left_half = left[:middle]
        alice_parity = _parity(alice_key[left_half])
        bob_parity = _parity(bob_key[left_half])
        disclosed_bits += 1

        if alice_parity != bob_parity:
            left = left_half
        else:
            left = left[middle:]

    bob_key[left[0]] ^= 1
    return True, disclosed_bits


def information_reconciliation(
    alice_key,
    bob_key,
    seed=None,
    block_sizes=(8, 16, 32, 64),
    passes=4
):
    alice = _validated_bits(alice_key, "Alice key")
    bob = _validated_bits(bob_key, "Bob key")

    if len(alice) != len(bob):
        raise ValueError("Alice and Bob keys must have the same length.")

    if len(alice) == 0:
        raise ValueError("Input keys must not be empty.")

    if passes < 1:
        raise ValueError("Passes must be at least 1.")

    if not block_sizes or any(size < 2 for size in block_sizes):
        raise ValueError("Block sizes must be at least 2.")

    rng = np.random.default_rng(seed)
    disclosed_bits = 0
    corrected_errors = 0

    for pass_index in range(passes):
        block_size = block_sizes[min(pass_index, len(block_sizes) - 1)]
        permutation = rng.permutation(len(alice))

        for start in range(0, len(alice), block_size):
            indices = permutation[start:start + block_size]
            if len(indices) < 2:
                continue

            corrected, disclosed = _reconcile_block(alice, bob, indices)
            disclosed_bits += disclosed
            corrected_errors += int(corrected)

    remaining_errors = int(np.count_nonzero(alice != bob))

    return {
        "success": remaining_errors == 0,
        "alice_key": alice.tolist(),
        "bob_key": bob.tolist(),
        "corrected_errors": corrected_errors,
        "remaining_errors": remaining_errors,
        "disclosed_bits": disclosed_bits,
        "key_length": len(alice)
    }


def toeplitz_privacy_amplification(
    key,
    output_length=256,
    seed=None
):
    input_bits = _validated_bits(key, "Key")

    if output_length < 1:
        raise ValueError("Output length must be positive.")

    if len(input_bits) < output_length:
        raise ValueError(
            "Input key is too short for the requested output length."
        )

    input_length = len(input_bits)
    rng = np.random.default_rng(seed)
    toeplitz_seed = rng.integers(
        0,
        2,
        size=input_length + output_length - 1,
        dtype=np.uint8
    )

    row_indices = np.arange(output_length)[:, None]
    column_indices = np.arange(input_length)[None, :]
    matrix_indices = row_indices - column_indices + input_length - 1
    toeplitz_matrix = toeplitz_seed[matrix_indices]
    output_key = (toeplitz_matrix @ input_bits) % 2

    return {
        "key": output_key.astype(np.uint8).tolist(),
        "input_length": input_length,
        "output_length": output_length,
        "toeplitz_seed": toeplitz_seed.tolist()
    }


def process_key(
    alice_key,
    bob_key,
    output_length=256,
    seed=None
):
    reconciliation = information_reconciliation(
        alice_key,
        bob_key,
        seed=seed
    )

    if not reconciliation["success"]:
        return {
            "success": False,
            "reason": "Information reconciliation failed.",
            "reconciliation": reconciliation
        }

    amplification = toeplitz_privacy_amplification(
        reconciliation["alice_key"],
        output_length=output_length,
        seed=None if seed is None else seed + 1
    )
    bob_amplification = toeplitz_privacy_amplification(
        reconciliation["bob_key"],
        output_length=output_length,
        seed=None if seed is None else seed + 1
    )

    alice_final_key = amplification["key"]
    bob_final_key = bob_amplification["key"]
    keys_match = alice_final_key == bob_final_key

    return {
        "success": keys_match,
        "reason": None if keys_match else "Final keys do not match.",
        "alice_key": alice_final_key,
        "bob_key": bob_final_key,
        "key_length": len(alice_final_key),
        "reconciliation": reconciliation,
        "privacy_amplification": {
            "input_length": amplification["input_length"],
            "output_length": amplification["output_length"],
            "toeplitz_seed": amplification["toeplitz_seed"]
        }
    }
