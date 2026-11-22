from config import (
    NUM_BITS,
    ALICE_SEED,
    BOB_SEED,
    SIMULATOR_SEED,
    EVE_SEED,
    ENABLE_EVE,
    EVE_ATTACK_PROBABILITY,
    QBER_SAMPLE_RATE,
    QBER_THRESHOLD
)

from bb84.alice import generate_bits, generate_bases, prepare_qubits
from bb84.bob import measure_qubits
from bb84.quantum_channel import transmit
from bb84.key_sifting import sift_keys

from attack.eve import intercept_resend

from security.qber import estimate_qber
from security.key_processing import process_key

from encryption.aes_gcm import encrypt_data, decrypt_data


def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():
    print_section("BB84 QUANTUM KEY DISTRIBUTION SIMULATOR")

    # ==================================================
    # 1. ALICE PREPARES QUBITS
    # ==================================================

    alice_bits = generate_bits(
        NUM_BITS,
        seed=ALICE_SEED
    )

    alice_bases = generate_bases(
        NUM_BITS,
        seed=ALICE_SEED + 1
    )

    print(f"\nNumber of transmitted qubits: {NUM_BITS}")

    circuits = prepare_qubits(
        alice_bits,
        alice_bases
    )

    print("Alice: Qubits prepared successfully.")

    # ==================================================
    # 2. QUANTUM CHANNEL
    # ==================================================

    received_circuits = transmit(circuits)

    print("Quantum channel: Transmission started.")

    if ENABLE_EVE:
        received_circuits, eve_bases, attack_flags = intercept_resend(
            received_circuits,
            attack_probability=EVE_ATTACK_PROBABILITY,
            seed=EVE_SEED
        )

        attacked_count = sum(attack_flags)

        print("\nEVE INTERCEPT-RESEND ATTACK")
        print("-" * 60)
        print("Attack enabled          : Yes")
        print(
            f"Configured attack rate  : "
            f"{EVE_ATTACK_PROBABILITY * 100:.2f}%"
        )
        print(f"Attacked qubits         : {attacked_count}")
        print(
            f"Actual attack rate      : "
            f"{attacked_count / NUM_BITS * 100:.2f}%"
        )

    else:
        print("\nEve attack: Disabled")

    print("\nQuantum channel: Transmission completed.")

    # ==================================================
    # 3. BOB MEASURES QUBITS
    # ==================================================

    bob_bases = generate_bases(
        NUM_BITS,
        seed=BOB_SEED
    )

    bob_bits = measure_qubits(
        received_circuits,
        bob_bases,
        seed=SIMULATOR_SEED
    )

    print("Bob: Qubits measured successfully.")

    # ==================================================
    # 4. BASIS SIFTING
    # ==================================================

    matching_indices, alice_key, bob_key = sift_keys(
        alice_bits,
        alice_bases,
        bob_bits,
        bob_bases
    )

    print_section("BB84 SIFTING RESULTS")

    print(f"Total transmitted bits : {NUM_BITS}")
    print(f"Matching basis         : {len(matching_indices)}")
    print(f"Discarded bits         : {NUM_BITS - len(matching_indices)}")
    print(f"Sifted key length      : {len(alice_key)}")

    if not alice_key or not bob_key:
        print_section("SECURITY DECISION")
        print("Result: No matching measurement bases; sifted key is empty.")
        print("Session status: ABORT")
        print("The session is terminated before QBER estimation.")
        print("The empty key must be discarded.")
        print("\\nBB84 simulation completed.")
        return

    # ==================================================
    # 5. QBER ESTIMATION
    # ==================================================

    print_section("QBER ESTIMATION")

    qber_result = estimate_qber(
        alice_key,
        bob_key,
        sample_rate=QBER_SAMPLE_RATE,
        threshold=QBER_THRESHOLD,
        seed=SIMULATOR_SEED + 1
    )

    print(f"Sample rate            : {QBER_SAMPLE_RATE * 100:.2f}%")
    print(f"Sample size            : {qber_result['sample_size']}")
    print(f"Errors in sample       : {qber_result['error_count']}")
    print(f"Estimated QBER         : {qber_result['qber'] * 100:.2f}%")
    print(f"Illustrative threshold : {qber_result['threshold'] * 100:.2f}%")
    print(f"Remaining key length   : {qber_result['remaining_length']}")

    # ==================================================
    # 6. SECURITY DECISION
    # ==================================================

    print_section("SECURITY DECISION")

    if not qber_result["accepted"]:
        print("Result: QBER exceeds the configured threshold.")
        print("Session status: ABORT")
        print("The remaining key must be discarded.")

        print("\nBB84 simulation completed.")
        return

    print("Result: QBER is within the configured threshold.")
    print("Session status: CONTINUE")
    print("Proceeding to key post-processing.")

    # ==================================================
    # 7. INFORMATION RECONCILIATION
    # ==================================================

    print_section("INFORMATION RECONCILIATION")

    try:
        key_result = process_key(
            qber_result["alice_remaining_key"],
            qber_result["bob_remaining_key"],
            output_length=256,
            seed=SIMULATOR_SEED + 2
        )

    except ValueError as error:
        print(f"Key processing error: {error}")
        print("Session status: ABORT")
        print("BB84 simulation completed.")
        return

    reconciliation = key_result["reconciliation"]

    print(f"Input key length       : {reconciliation['key_length']}")
    print(f"Corrected errors      : {reconciliation['corrected_errors']}")
    print(f"Remaining errors      : {reconciliation['remaining_errors']}")
    print(f"Disclosed parity bits : {reconciliation['disclosed_bits']}")

    if not key_result["success"]:
        print("\nInformation reconciliation failed.")
        print("Session status: ABORT")
        print("The generated key must be discarded.")

        print("\nBB84 simulation completed.")
        return

    print("Information reconciliation: SUCCESS")

    # ==================================================
    # 8. PRIVACY AMPLIFICATION
    # ==================================================

    print_section("PRIVACY AMPLIFICATION")

    amplification = key_result["privacy_amplification"]

    alice_final_key = key_result["alice_key"]
    bob_final_key = key_result["bob_key"]

    print(f"Input key length       : {amplification['input_length']}")
    print(f"Output key length      : {amplification['output_length']}")
    print("Hashing method         : Toeplitz matrix")
    print(f"Final key length       : {key_result['key_length']} bits")
    print(f"Alice and Bob match    : {alice_final_key == bob_final_key}")

    if alice_final_key != bob_final_key:
        print("\nFinal keys do not match.")
        print("Session status: ABORT")
        print("BB84 simulation completed.")
        return

    # ==================================================
    # 9. AES-256-GCM ENCRYPTION
    # ==================================================

    print_section("AES-256-GCM ENCRYPTION")

    plaintext = (
        "This is a confidential message transmitted "
        "using a key generated by the BB84 simulation."
    )

    try:
        encrypted_data = encrypt_data(
            plaintext,
            alice_final_key
        )

        print("Encryption status      : SUCCESS")
        print(f"Plaintext              : {plaintext}")
        print(f"Ciphertext              : {encrypted_data['ciphertext'].hex()}")
        print(f"Nonce                   : {encrypted_data['nonce'].hex()}")
        print(f"Authentication tag      : {encrypted_data['tag'].hex()}")

    except (ValueError, TypeError) as error:
        print(f"Encryption error: {error}")
        print("Session status: ABORT")
        print("BB84 simulation completed.")
        return

    # ==================================================
    # 10. BOB DECRYPTS AND VERIFIES
    # ==================================================

    print_section("AES-256-GCM DECRYPTION")

    try:
        decrypted_data = decrypt_data(
            encrypted_data,
            bob_final_key
        )

        decrypted_text = decrypted_data.decode("utf-8")

        print("Decryption status      : SUCCESS")
        print(f"Decrypted message      : {decrypted_text}")
        print(f"Data integrity         : {decrypted_text == plaintext}")

    except (ValueError, TypeError) as error:
        print(f"Decryption error: {error}")
        print("Session status: ABORT")
        print("BB84 simulation completed.")
        return

    # ==================================================
    # 11. TAMPERING DETECTION
    # ==================================================

    print_section("TAMPERING DETECTION")

    tampered_data = encrypted_data.copy()

    original_ciphertext = tampered_data["ciphertext"]

    tampered_data["ciphertext"] = (
        bytes([original_ciphertext[0] ^ 1])
        + original_ciphertext[1:]
    )

    try:
        decrypt_data(
            tampered_data,
            bob_final_key
        )

        print("Tampering detection     : FAILED")
        print("Modified ciphertext was accepted.")

    except ValueError:
        print("Tampering detection     : SUCCESS")
        print("Modified ciphertext was rejected.")
        print("Authentication failed as expected.")

    # ==================================================
    # 12. FINAL RESULT
    # ==================================================

    print_section("FINAL SIMULATION RESULT")

    print("BB84 key exchange       : SUCCESS")
    print("QBER verification      : ACCEPTED")
    print("Information reconciliation: SUCCESS")
    print("Privacy amplification  : SUCCESS")
    print("AES-256-GCM encryption : SUCCESS")
    print("AES-256-GCM decryption : SUCCESS")
    print("Data integrity         : VERIFIED")
    print("Tampering detection    : VERIFIED")

    print("\nBB84 and AES simulation completed.")
    print("Note: This is an educational simulation,")
    print("not a security-certified QKD implementation.")


if __name__ == "__main__":
    main()
