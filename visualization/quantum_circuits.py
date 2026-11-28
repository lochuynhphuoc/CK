import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
from qiskit_aer import AerSimulator

from attack.eve import build_eve_measurement_circuit
from bb84.alice import prepare_qubit
from bb84.bob import measure_qubit


def export_circuit(circuit, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    figure = circuit.draw(output="mpl", fold=-1)
    figure.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(figure)
    return output_path


def export_quantum_circuits(output_dir="results/quantum_circuits"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    alice_circuit = prepare_qubit(1, "X", index=0)
    bob_circuit = measure_qubit(alice_circuit, "X")
    eve_circuit = build_eve_measurement_circuit(alice_circuit, "Z")

    simulator = AerSimulator()
    circuit_specs = [
        ("alice_prepare_x.png", alice_circuit),
        ("bob_measure_x.png", bob_circuit),
        ("eve_intercept_z.png", eve_circuit),
    ]

    rows = []
    for filename, circuit in circuit_specs:
        path = export_circuit(circuit, output_dir / filename)
        rows.append({
            "figure": filename,
            "circuit_name": circuit.name or "circuit",
            "qubits": circuit.num_qubits,
            "classical_bits": circuit.num_clbits,
            "operations": str(circuit.count_ops()),
            "simulator": simulator.name,
        })

    csv_path = output_dir / "circuit_metadata.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    return [output_dir / item[0] for item in circuit_specs], csv_path


def main():
    parser = argparse.ArgumentParser(
        description="Export diagrams of the project's Qiskit BB84 circuits."
    )
    parser.add_argument(
        "--output-dir",
        default="results/quantum_circuits",
        help="Directory for generated circuit diagrams and metadata."
    )
    args = parser.parse_args()

    images, metadata = export_quantum_circuits(args.output_dir)
    print("Quantum circuit diagrams exported.")
    for image_path in images:
        print(f"Circuit: {image_path}")
    print(f"Metadata: {metadata}")


if __name__ == "__main__":
    main()
