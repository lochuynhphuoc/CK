import secrets

from config import (
    NUM_BITS,
    ENABLE_EVE,
    EVE_ATTACK_PROBABILITY,
    QBER_SAMPLE_RATE,
    QBER_THRESHOLD
)

from bb84.alice import (
    generate_bits,
    generate_bases,
    prepare_qubits
)

from bb84.bob import measure_qubits
from bb84.quantum_channel import transmit
from bb84.key_sifting import sift_keys
from attack.eve import intercept_resend
from security.qber import estimate_qber
from security.key_processing import process_key


def run_bb84_session():
    session_seed = secrets.randbelow(2**32 - 1000)

    alice_seed = session_seed
    bob_seed = session_seed + 100
    simulator_seed = session_seed + 200
    eve_seed = session_seed + 300

    result = {
        "success": False,
        "status": "ABORT",
        "session_seed": session_seed,
        "key": None,
        "metrics": {}
    }

    alice_bits = generate_bits(
        NUM_BITS,
        seed=alice_seed
    )

    alice_bases = generate_bases(
        NUM_BITS,
        seed=alice_seed + 1
    )

    circuits = prepare_qubits(
        alice_bits,
        alice_bases
    )

    received_circuits = transmit(circuits)

    attacked_count = 0

    if ENABLE_EVE:
        received_circuits, eve_bases, attack_flags = intercept_resend(
            received_circuits,
            attack_probability=EVE_ATTACK_PROBABILITY,
            seed=eve_seed
        )

        attacked_count = sum(attack_flags)

    bob_bases = generate_bases(
        NUM_BITS,
        seed=bob_seed
    )

    bob_bits = measure_qubits(
        received_circuits,
        bob_bases,
        seed=simulator_seed
    )

    matching_indices, alice_key, bob_key = sift_keys(
        alice_bits,
        alice_bases,
        bob_bits,
        bob_bases
    )

    if not alice_key:
        result["reason"] = "No matching bases."
        return result

    qber_result = estimate_qber(
        alice_key,
        bob_key,
        sample_rate=QBER_SAMPLE_RATE,
        threshold=QBER_THRESHOLD,
        seed=simulator_seed + 1
    )

    result["metrics"] = {
        "num_bits": NUM_BITS,
        "attacked_count": attacked_count,
        "actual_attack_rate": attacked_count / NUM_BITS,
        "matching_bases": len(matching_indices),
        "sifted_key_length": len(alice_key),
        "sample_size": qber_result["sample_size"],
        "error_count": qber_result["error_count"],
        "qber": qber_result["qber"],
        "qber_threshold": QBER_THRESHOLD,
        "remaining_length": qber_result["remaining_length"]
    }

    if not qber_result["accepted"]:
        result["reason"] = "QBER exceeds the configured threshold."
        return result

    try:
        key_result = process_key(
            qber_result["alice_remaining_key"],
            qber_result["bob_remaining_key"],
            output_length=256,
            seed=simulator_seed + 2
        )

    except ValueError as error:
        result["reason"] = str(error)
        return result

    if not key_result["success"]:
        result["reason"] = key_result.get(
            "reason",
            "Information reconciliation or privacy amplification failed."
        )
        return result

    alice_final_key = key_result["alice_key"]
    bob_final_key = key_result["bob_key"]

    if alice_final_key != bob_final_key:
        result["reason"] = "Alice and Bob final keys do not match."
        return result

    result["success"] = True
    result["status"] = "CONTINUE"
    result["key"] = alice_final_key

    result["metrics"].update({
        "reconciliation_corrected_errors": (
            key_result["reconciliation"]["corrected_errors"]
        ),
        "reconciliation_remaining_errors": (
            key_result["reconciliation"]["remaining_errors"]
        ),
        "disclosed_bits": (
            key_result["reconciliation"]["disclosed_bits"]
        ),
        "final_key_length": key_result["key_length"]
    })

    return result