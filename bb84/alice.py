import numpy as np
from qiskit import QuantumCircuit


def generate_bits(num_bits, seed=None):
    rng = np.random.default_rng(seed)
    return rng.integers(0, 2, size=num_bits, dtype=np.int8)


def generate_bases(num_bits, seed=None):
    rng = np.random.default_rng(seed)
    return rng.choice(["Z", "X"], size=num_bits)


def prepare_qubit(bit, basis, index=0):
    if int(bit) not in (0, 1):
        raise ValueError("Bit must be 0 or 1.")
    if basis not in ("Z", "X"):
        raise ValueError(f"Invalid basis: {basis}")

    circuit = QuantumCircuit(1, 1)
    circuit.name = f"qubit_{index}"

    if int(bit) == 1:
        circuit.x(0)

    if basis == "X":
        circuit.h(0)

    return circuit


def prepare_qubits(bits, bases):
    if len(bits) != len(bases):
        raise ValueError("Bits and bases must have the same length.")

    return [
        prepare_qubit(bit, basis, index)
        for index, (bit, basis) in enumerate(zip(bits, bases))
    ]
