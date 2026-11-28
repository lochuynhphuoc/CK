import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator


def generate_bases(num_bits, seed=None):
    rng = np.random.default_rng(seed)
    return rng.choice(["Z", "X"], size=num_bits)


def measure_qubit(circuit, basis):
    if basis not in ("Z", "X"):
        raise ValueError(f"Invalid basis: {basis}")

    measured_circuit = circuit.copy()

    if basis == "X":
        measured_circuit.h(0)

    measured_circuit.measure(0, 0)
    return measured_circuit


def measure_qubits(circuits, bases, seed=None):
    if len(circuits) != len(bases):
        raise ValueError("Circuits and bases must have the same length.")

    if not circuits:
        return []

    measured_circuits = [
        measure_qubit(circuit, basis)
        for circuit, basis in zip(circuits, bases)
    ]

    simulator = AerSimulator()
    compiled_circuits = transpile(measured_circuits, simulator)

    job = simulator.run(
        compiled_circuits,
        shots=1,
        memory=True,
        seed_simulator=seed
    )

    result = job.result()

    return [
        int(result.get_memory(index)[0])
        for index in range(len(measured_circuits))
    ]
