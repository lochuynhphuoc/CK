import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def generate_eve_bases(num_bits, seed=None):
    if num_bits < 0:
        raise ValueError("Number of bits cannot be negative.")

    rng = np.random.default_rng(seed)
    return rng.choice(["Z", "X"], size=num_bits)


def build_eve_measurement_circuit(circuit, basis):
    if basis not in ("Z", "X"):
        raise ValueError(f"Invalid basis: {basis}")

    measured_circuit = circuit.copy()
    measured_circuit.name = f"eve_measure_{basis}"

    if basis == "X":
        measured_circuit.h(0)

    measured_circuit.measure(0, 0)
    return measured_circuit


def build_eve_resend_circuit(measured_bit, basis):
    if int(measured_bit) not in (0, 1):
        raise ValueError("Measured bit must be 0 or 1.")
    if basis not in ("Z", "X"):
        raise ValueError(f"Invalid basis: {basis}")

    circuit = QuantumCircuit(1, 1)
    circuit.name = f"eve_resend_{basis}_{int(measured_bit)}"

    if int(measured_bit) == 1:
        circuit.x(0)
    if basis == "X":
        circuit.h(0)

    return circuit


def intercept_resend(circuits, attack_probability=1.0, seed=None):
    if not 0.0 <= attack_probability <= 1.0:
        raise ValueError("Attack probability must be between 0 and 1.")

    if not circuits:
        return [], [], []

    basis_sequence, attack_sequence, simulator_sequence = (
        np.random.SeedSequence(seed).spawn(3)
    )

    basis_rng = np.random.default_rng(basis_sequence)
    attack_rng = np.random.default_rng(attack_sequence)
    simulator_seed = int(
        simulator_sequence.generate_state(1, dtype=np.uint32)[0]
    )

    num_bits = len(circuits)
    eve_bases = basis_rng.choice(["Z", "X"], size=num_bits)
    attack_flags = attack_rng.random(num_bits) < attack_probability

    attacked_indices = np.flatnonzero(attack_flags)
    measured_results = {}

    if len(attacked_indices) > 0:
        measurement_circuits = [
            build_eve_measurement_circuit(circuits[index], eve_bases[index])
            for index in attacked_indices
        ]

        simulator = AerSimulator()
        compiled = transpile(measurement_circuits, simulator)

        job = simulator.run(
            compiled,
            shots=1,
            memory=True,
            seed_simulator=simulator_seed
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

        output_circuits.append(
            build_eve_resend_circuit(
                measured_results[index],
                eve_bases[index]
            )
        )

    return output_circuits, eve_bases, attack_flags
