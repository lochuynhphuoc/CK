import numpy as np
import pytest
from qiskit import QuantumCircuit

from attack.eve import generate_eve_bases, intercept_resend


def _circuits(count):
    circuits = []
    for index in range(count):
        circuit = QuantumCircuit(1, 1)
        if index % 2:
            circuit.x(0)
        circuits.append(circuit)
    return circuits


def test_eve_does_not_attack_when_probability_is_zero():
    circuits = _circuits(16)
    output, bases, flags = intercept_resend(
        circuits,
        attack_probability=0.0,
        seed=100
    )

    assert len(output) == len(circuits)
    assert len(bases) == len(circuits)
    assert not np.any(flags)
    assert all(
        original == received
        for original, received in zip(circuits, output)
    )


def test_eve_attacks_every_qubit_when_probability_is_one():
    output, bases, flags = intercept_resend(
        _circuits(16),
        attack_probability=1.0,
        seed=200
    )

    assert len(output) == 16
    assert len(bases) == 16
    assert np.all(flags)


def test_eve_random_streams_are_reproducible_and_independent():
    _, bases, flags = intercept_resend(
        _circuits(512),
        attack_probability=0.5,
        seed=300
    )
    _, repeated_bases, repeated_flags = intercept_resend(
        _circuits(512),
        attack_probability=0.5,
        seed=300
    )

    assert np.array_equal(bases, repeated_bases)
    assert np.array_equal(flags, repeated_flags)
    assert not np.array_equal(bases == "X", flags)


def test_eve_rejects_invalid_attack_probability():
    with pytest.raises(ValueError):
        intercept_resend(_circuits(2), attack_probability=1.1, seed=1)

    with pytest.raises(ValueError):
        intercept_resend(_circuits(2), attack_probability=-0.1, seed=1)


def test_generate_eve_bases_rejects_negative_length():
    with pytest.raises(ValueError):
        generate_eve_bases(-1, seed=1)
