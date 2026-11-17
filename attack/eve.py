import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def generate_eve_bases(num_bits, seed=None):
    rng = np.random.default_rng(seed)
    return rng.choice(["Z", "X"], size=num_bits)


def intercept_resend(circuits, attack_probability=1.0, seed=None):
    if not 0.0 <= attack_probability <= 1.0:
        raise ValueError("Attack probability must be between 0 and 1.")

    if not circuits:
        return [], [], []

    rng = np.random.default_rng(seed)

    num_bits = len(circuits)
    eve_bases = generate_eve_bases(num_bits, seed)
    attack_flags = rng.random(num_bits) < attack_probability

    attacked_indices = np.flatnonzero(attack_flags)
    measured_results = {}

    if len(attacked_indices) > 0:
        measurement_circuits = []

        for index in attacked_indices:
            circuit = circuits[index].copy()

            if eve_bases[index] == "X":
                circuit.h(0)

            circuit.measure(0, 0)
            measurement_circuits.append(circuit)

        simulator = AerSimulator()
        compiled = transpile(measurement_circuits, simulator)

        job = simulator.run(
            compiled,
            shots=1,
            memory=True,
            seed_simulator=seed
        )

        result = job.result()

        for position, index in enumerate(attacked_indices):
            measurement = result.get_memory(position)[0]
            measured_results[index] = int(
                measurement.replace(" ", "")[-1]
            )

    output_circuits = []

    for index, circuit in enumerate(circuits):
        if not attack_flags[index]:
            output_circuits.append(circuit.copy())
            continue

        measured_bit = measured_results[index]
        new_circuit = QuantumCircuit(1, 1)

        if measured_bit == 1:
            new_circuit.x(0)

        if eve_bases[index] == "X":
            new_circuit.h(0)

        output_circuits.append(new_circuit)

    return output_circuits, eve_bases, attack_flags
