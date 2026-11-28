from pathlib import Path

from qiskit import QuantumCircuit

from attack.eve import (
    build_eve_measurement_circuit,
    build_eve_resend_circuit,
)
from bb84.alice import prepare_qubit
from bb84.bob import measure_qubit
from visualization.quantum_circuits import export_quantum_circuits


def test_alice_prepares_bit_one_in_x_basis():
    circuit = prepare_qubit(1, "X")

    assert circuit.num_qubits == 1
    assert circuit.count_ops().get("x", 0) == 1
    assert circuit.count_ops().get("h", 0) == 1
    assert circuit.count_ops().get("measure", 0) == 0


def test_bob_measures_x_basis_after_hadamard():
    source = prepare_qubit(0, "Z")
    measured = measure_qubit(source, "X")

    assert measured.count_ops().get("h", 0) == 1
    assert measured.count_ops().get("measure", 0) == 1
    assert source.count_ops().get("measure", 0) == 0


def test_eve_intercept_and_resend_circuits_are_separate_stages():
    source = prepare_qubit(1, "X")
    measurement = build_eve_measurement_circuit(source, "Z")
    resend = build_eve_resend_circuit(1, "Z")

    assert measurement.count_ops().get("measure", 0) == 1
    assert resend.count_ops().get("x", 0) == 1
    assert resend.count_ops().get("measure", 0) == 0


def test_circuit_export_creates_four_pngs_and_metadata(tmp_path):
    images, metadata = export_quantum_circuits(tmp_path)

    assert len(images) == 4
    assert all(Path(image).is_file() and Path(image).stat().st_size > 0 for image in images)
    assert metadata.is_file()
    assert "alice_prepare_x.png" in metadata.read_text(encoding="utf-8")
