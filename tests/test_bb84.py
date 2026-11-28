import numpy as np

from bb84.alice import generate_bits, generate_bases, prepare_qubits
from bb84.bob import measure_qubits
from bb84.key_sifting import sift_keys


def test_random_generation_is_reproducible():
    assert np.array_equal(
        generate_bits(32, seed=123),
        generate_bits(32, seed=123)
    )
    assert np.array_equal(
        generate_bases(32, seed=456),
        generate_bases(32, seed=456)
    )


def test_prepare_and_measure_matching_bases_without_eve():
    bits = np.array([0, 1, 1, 0, 1, 0, 0, 1], dtype=np.int8)
    bases = np.array(["Z", "X", "Z", "X", "X", "Z", "X", "Z"])

    circuits = prepare_qubits(bits, bases)
    measured = measure_qubits(circuits, bases, seed=789)

    assert measured == bits.tolist()


def test_key_sifting_keeps_only_matching_bases():
    alice_bits = [0, 1, 1, 0, 1]
    alice_bases = ["Z", "X", "Z", "X", "Z"]
    bob_bits = [0, 0, 1, 1, 1]
    bob_bases = ["Z", "Z", "Z", "X", "X"]

    indices, alice_key, bob_key = sift_keys(
        alice_bits,
        alice_bases,
        bob_bits,
        bob_bases
    )

    assert indices == [0, 2, 3]
    assert alice_key == [0, 1, 0]
    assert bob_key == [0, 1, 1]


def test_key_sifting_rejects_different_lengths():
    try:
        sift_keys([0], ["Z"], [0, 1], ["Z", "X"])
    except ValueError as error:
        assert "same length" in str(error)
    else:
        raise AssertionError("Different input lengths were accepted.")
