import bb84.session as session_module


def test_session_aborts_before_key_processing_when_qber_fails(monkeypatch):
    monkeypatch.setattr(session_module, "NUM_BITS", 8)
    monkeypatch.setattr(session_module, "generate_bits", lambda count, seed=None: [0] * count)
    monkeypatch.setattr(session_module, "generate_bases", lambda count, seed=None: ["Z"] * count)
    monkeypatch.setattr(session_module, "prepare_qubits", lambda bits, bases: ["circuit"] * len(bits))
    monkeypatch.setattr(session_module, "transmit", lambda circuits: circuits)
    monkeypatch.setattr(session_module, "measure_qubits", lambda circuits, bases, seed=None: [1] * len(circuits))
    monkeypatch.setattr(
        session_module,
        "sift_keys",
        lambda *args: (list(range(8)), [0] * 8, [1] * 8)
    )
    monkeypatch.setattr(
        session_module,
        "estimate_qber",
        lambda *args, **kwargs: {
            "sample_size": 2,
            "error_count": 2,
            "qber": 1.0,
            "accepted": False,
            "remaining_length": 6
        }
    )
    monkeypatch.setattr(
        session_module,
        "process_key",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("Key processing must not run after QBER abort.")
        )
    )

    result = session_module.run_bb84_session()

    assert result["success"] is False
    assert result["status"] == "ABORT"
    assert result["key"] is None
    assert "QBER" in result["reason"]


def test_session_continues_only_when_final_keys_match(monkeypatch):
    monkeypatch.setattr(session_module, "NUM_BITS", 8)
    monkeypatch.setattr(session_module, "generate_bits", lambda count, seed=None: [0] * count)
    monkeypatch.setattr(session_module, "generate_bases", lambda count, seed=None: ["Z"] * count)
    monkeypatch.setattr(session_module, "prepare_qubits", lambda bits, bases: ["circuit"] * len(bits))
    monkeypatch.setattr(session_module, "transmit", lambda circuits: circuits)
    monkeypatch.setattr(session_module, "measure_qubits", lambda circuits, bases, seed=None: [0] * len(circuits))
    monkeypatch.setattr(
        session_module,
        "sift_keys",
        lambda *args: (list(range(8)), [0] * 8, [0] * 8)
    )
    monkeypatch.setattr(
        session_module,
        "estimate_qber",
        lambda *args, **kwargs: {
            "sample_size": 2,
            "error_count": 0,
            "qber": 0.0,
            "accepted": True,
            "remaining_length": 6,
            "alice_remaining_key": [0, 1, 0, 1, 0, 1],
            "bob_remaining_key": [0, 1, 0, 1, 0, 1]
        }
    )
    monkeypatch.setattr(
        session_module,
        "process_key",
        lambda *args, **kwargs: {
            "success": True,
            "alice_key": [index % 2 for index in range(256)],
            "bob_key": [index % 2 for index in range(256)],
            "key_length": 256,
            "reconciliation": {
                "corrected_errors": 0,
                "remaining_errors": 0,
                "disclosed_bits": 0
            }
        }
    )

    result = session_module.run_bb84_session()

    assert result["success"] is True
    assert result["status"] == "CONTINUE"
    assert len(result["key"]) == 256
    assert result["metrics"]["final_key_length"] == 256
