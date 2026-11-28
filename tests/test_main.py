import main as main_module


def test_main_aborts_when_sifted_keys_are_empty(monkeypatch, capsys):
    monkeypatch.setattr(main_module, "NUM_BITS", 8)
    monkeypatch.setattr(main_module, "generate_bits", lambda count, seed=None: [0] * count)
    monkeypatch.setattr(main_module, "generate_bases", lambda count, seed=None: ["Z"] * count)
    monkeypatch.setattr(main_module, "prepare_qubits", lambda bits, bases: ["circuit"] * len(bits))
    monkeypatch.setattr(main_module, "transmit", lambda circuits: circuits)
    monkeypatch.setattr(main_module, "measure_qubits", lambda circuits, bases, seed=None: [0] * len(circuits))
    monkeypatch.setattr(
        main_module,
        "sift_keys",
        lambda *args: ([], [], [])
    )
    monkeypatch.setattr(
        main_module,
        "estimate_qber",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("QBER estimation must not run with empty sifted keys.")
        )
    )

    main_module.main()

    output = capsys.readouterr().out
    assert "Sifted key length      : 0" in output
    assert "Session status: ABORT" in output
    assert "No matching measurement bases; sifted key is empty." in output
    assert "QBER ESTIMATION" not in output
    assert "AES-256-GCM ENCRYPTION" not in output
