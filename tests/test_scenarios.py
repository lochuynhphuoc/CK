from experiments import scenarios


def test_run_trial_aborts_when_no_bases_match(monkeypatch):
    monkeypatch.setattr(scenarios, "generate_bits", lambda count, seed=None: [0] * count)
    monkeypatch.setattr(scenarios, "generate_bases", lambda count, seed=None: ["Z"] * count)
    monkeypatch.setattr(scenarios, "prepare_qubits", lambda bits, bases: ["circuit"] * len(bits))
    monkeypatch.setattr(scenarios, "transmit", lambda circuits: circuits)
    monkeypatch.setattr(
        scenarios, "intercept_resend",
        lambda circuits, attack_probability, seed=None: (circuits, [], [False] * len(circuits))
    )
    monkeypatch.setattr(scenarios, "generate_bob_bases", lambda count, seed=None: ["X"] * count)
    monkeypatch.setattr(scenarios, "measure_qubits", lambda circuits, bases, seed=None: [0] * len(circuits))
    monkeypatch.setattr(
        scenarios, "sift_keys",
        lambda *args: ([], [], [])
    )

    result = scenarios.run_trial(
        attack_probability=0.0,
        trial=1,
        num_bits=8,
        base_seed=10
    )

    assert result["session_status"] == "ABORT"
    assert result["accepted"] is False
    assert result["sifted_key_length"] == 0
    assert result["sample_size"] == 0
    assert result["sample_qber"] is None
    assert "empty" in result["reason"].lower()


def test_run_trial_keeps_normal_qber_path(monkeypatch):
    monkeypatch.setattr(scenarios, "generate_bits", lambda count, seed=None: [0] * count)
    monkeypatch.setattr(scenarios, "generate_bases", lambda count, seed=None: ["Z"] * count)
    monkeypatch.setattr(scenarios, "prepare_qubits", lambda bits, bases: ["circuit"] * len(bits))
    monkeypatch.setattr(scenarios, "transmit", lambda circuits: circuits)
    monkeypatch.setattr(
        scenarios, "intercept_resend",
        lambda circuits, attack_probability, seed=None: (circuits, [], [False] * len(circuits))
    )
    monkeypatch.setattr(scenarios, "generate_bob_bases", lambda count, seed=None: ["Z"] * count)
    monkeypatch.setattr(scenarios, "measure_qubits", lambda circuits, bases, seed=None: [0] * len(circuits))
    monkeypatch.setattr(
        scenarios, "sift_keys",
        lambda *args: (list(range(8)), [0] * 8, [0] * 8)
    )

    result = scenarios.run_trial(
        attack_probability=0.0,
        trial=1,
        num_bits=8,
        sample_rate=0.25,
        base_seed=10
    )
    assert result["session_status"] == "CONTINUE"
    assert result["sample_size"] == 2
    assert result["sample_qber"] == 0.0
