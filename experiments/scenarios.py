import argparse
from pathlib import Path

from bb84.alice import generate_bits, generate_bases, prepare_qubits
from bb84.bob import generate_bases as generate_bob_bases, measure_qubits
from bb84.key_sifting import sift_keys
from bb84.quantum_channel import transmit
from attack.eve import intercept_resend
from config import NUM_BITS, QBER_SAMPLE_RATE, QBER_THRESHOLD
from security.qber import estimate_qber
from experiments.results import save_experiment_results


DEFAULT_ATTACK_RATES = tuple(index / 10 for index in range(11))
DEFAULT_TRIALS = 10
DEFAULT_BASE_SEED = 10000


def run_trial(
    attack_probability,
    trial,
    num_bits=NUM_BITS,
    sample_rate=QBER_SAMPLE_RATE,
    threshold=QBER_THRESHOLD,
    base_seed=DEFAULT_BASE_SEED
):
    if not 0.0 <= attack_probability <= 1.0:
        raise ValueError("Attack probability must be between 0 and 1.")
    if trial < 1:
        raise ValueError("Trial number must be at least 1.")
    if num_bits < 2:
        raise ValueError("Number of transmitted qubits must be at least 2.")
    if not 0.0 < sample_rate <= 1.0:
        raise ValueError("Sample rate must be greater than 0 and at most 1.")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("QBER threshold must be between 0 and 1.")

    seed = base_seed + trial * 1000
    alice_bits = generate_bits(num_bits, seed=seed)
    alice_bases = generate_bases(num_bits, seed=seed + 1)
    circuits = prepare_qubits(alice_bits, alice_bases)
    received_circuits = transmit(circuits)

    received_circuits, _, attack_flags = intercept_resend(
        received_circuits,
        attack_probability=attack_probability,
        seed=seed + 2
    )

    bob_bases = generate_bob_bases(num_bits, seed=seed + 3)
    bob_bits = measure_qubits(
        received_circuits,
        bob_bases,
        seed=seed + 4
    )

    matching_indices, alice_key, bob_key = sift_keys(
        alice_bits,
        alice_bases,
        bob_bits,
        bob_bases
    )

    attacked_count = int(sum(attack_flags))
    sifted_errors = sum(
        int(alice_bit) != int(bob_bit)
        for alice_bit, bob_bit in zip(alice_key, bob_key)
    )
    attacked_rate = attacked_count / num_bits

    if not alice_key:
        return {
            "attack_probability": attack_probability,
            "trial": trial,
            "seed": seed,
            "num_bits": num_bits,
            "attacked_qubits": attacked_count,
            "actual_attack_rate": attacked_rate,
            "matching_basis": len(matching_indices),
            "sifted_key_length": 0,
            "sample_size": 0,
            "sample_errors": 0,
            "sample_qber": None,
            "actual_sifted_errors": 0,
            "actual_sifted_qber": None,
            "threshold": threshold,
            "accepted": False,
            "session_status": "ABORT",
            "reason": "No matching measurement bases; sifted key is empty."
        }

    qber_result = estimate_qber(
        alice_key,
        bob_key,
        sample_rate=sample_rate,
        threshold=threshold,
        seed=seed + 5
    )

    actual_sifted_qber = sifted_errors / len(alice_key)

    return {
        "attack_probability": attack_probability,
        "trial": trial,
        "seed": seed,
        "num_bits": num_bits,
        "attacked_qubits": attacked_count,
        "actual_attack_rate": attacked_rate,
        "matching_basis": len(matching_indices),
        "sifted_key_length": len(alice_key),
        "sample_size": qber_result["sample_size"],
        "sample_errors": qber_result["error_count"],
        "sample_qber": qber_result["qber"],
        "actual_sifted_errors": sifted_errors,
        "actual_sifted_qber": actual_sifted_qber,
        "threshold": threshold,
        "accepted": qber_result["accepted"],
        "session_status": "CONTINUE" if qber_result["accepted"] else "ABORT",
        "reason": None if qber_result["accepted"] else "Sample QBER exceeds threshold."
    }


def run_experiments(
    attack_rates=DEFAULT_ATTACK_RATES,
    trials=DEFAULT_TRIALS,
    num_bits=NUM_BITS,
    sample_rate=QBER_SAMPLE_RATE,
    threshold=QBER_THRESHOLD,
    base_seed=DEFAULT_BASE_SEED,
    output_dir="results"
):
    if trials < 1:
        raise ValueError("Number of trials must be at least 1.")
    rates = tuple(float(rate) for rate in attack_rates)
    if not rates:
        raise ValueError("At least one attack rate must be provided.")
    if any(not 0.0 <= rate <= 1.0 for rate in rates):
        raise ValueError("Every attack rate must be between 0 and 1.")

    rows = []
    total_runs = len(rates) * trials

    for rate_index, attack_probability in enumerate(rates):
        print(
            f"\nAttack probability: {attack_probability:.0%} "
            f"({rate_index + 1}/{len(rates)})"
        )
        for trial in range(1, trials + 1):
            result = run_trial(
                attack_probability=attack_probability,
                trial=trial + rate_index * trials,
                num_bits=num_bits,
                sample_rate=sample_rate,
                threshold=threshold,
                base_seed=base_seed
            )
            rows.append(result)
            print(
                f"  Trial {trial:02d}/{trials}: "
                f"QBER={result['sample_qber'] if result['sample_qber'] is not None else 'N/A'}, "
                f"attacked={result['actual_attack_rate']:.2%}, "
                f"status={result['session_status']}"
            )
        print(f"Completed runs: {len(rows)}/{total_runs}")

    raw_path, summary_path = save_experiment_results(
        rows,
        output_dir=Path(output_dir)
    )
    print("\nExperiment completed.")
    print(f"Raw results     : {raw_path}")
    print(f"Summary results : {summary_path}")
    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Run automated BB84 Eve attack experiments."
    )
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    parser.add_argument("--num-bits", type=int, default=NUM_BITS)
    parser.add_argument("--sample-rate", type=float, default=QBER_SAMPLE_RATE)
    parser.add_argument("--threshold", type=float, default=QBER_THRESHOLD)
    parser.add_argument("--base-seed", type=int, default=DEFAULT_BASE_SEED)
    parser.add_argument("--output-dir", default="results")
    args = parser.parse_args()

    run_experiments(
        trials=args.trials,
        num_bits=args.num_bits,
        sample_rate=args.sample_rate,
        threshold=args.threshold,
        base_seed=args.base_seed,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
