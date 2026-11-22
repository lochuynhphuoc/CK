import hashlib

import pytest

import file_transfer.transfer as transfer_module
from encryption.aes_gcm import encrypt_data
from encryption.file_encryption import decrypt_file, encrypt_file
from file_transfer.transfer import transfer_file


VALID_SESSION = {
    "success": True,
    "status": "CONTINUE",
    "key": [index % 2 for index in range(256)],
    "metrics": {"final_key_length": 256}
}


def test_transfer_encrypts_decrypts_and_verifies_sha256(tmp_path, monkeypatch):
    source = tmp_path / "source.bin"
    encrypted = tmp_path / "source.bin.enc"
    decrypted = tmp_path / "restored.bin"
    source.write_bytes(bytes(range(256)) * 4)

    monkeypatch.setattr(
        transfer_module,
        "run_bb84_session",
        lambda: VALID_SESSION.copy()
    )

    result = transfer_file(source, encrypted, decrypted)

    assert result["success"] is True
    assert result["status"] == "SUCCESS"
    assert encrypted.is_file()
    assert decrypted.read_bytes() == source.read_bytes()
    assert result["integrity"]["verified"] is True
    assert hashlib.sha256(source.read_bytes()).hexdigest() == (
        result["integrity"]["decrypted_sha256"]
    )


def test_transfer_aborts_without_creating_output_files(tmp_path, monkeypatch):
    source = tmp_path / "source.txt"
    encrypted = tmp_path / "source.txt.enc"
    decrypted = tmp_path / "restored.txt"
    source.write_text("test payload", encoding="utf-8")

    monkeypatch.setattr(
        transfer_module,
        "run_bb84_session",
        lambda: {
            "success": False,
            "status": "ABORT",
            "reason": "QBER exceeds threshold.",
            "key": None,
            "metrics": {"qber": 0.3}
        }
    )

    result = transfer_file(source, encrypted, decrypted)

    assert result["success"] is False
    assert result["status"] == "ABORT"
    assert not encrypted.exists()
    assert not decrypted.exists()


@pytest.mark.parametrize("same_target", ["encrypted", "decrypted"])
def test_transfer_rejects_output_path_equal_to_source(
    tmp_path,
    monkeypatch,
    same_target
):
    source = tmp_path / "source.txt"
    source.write_text("keep this file", encoding="utf-8")
    encrypted = source if same_target == "encrypted" else tmp_path / "x.enc"
    decrypted = source if same_target == "decrypted" else tmp_path / "restored.txt"

    monkeypatch.setattr(
        transfer_module,
        "run_bb84_session",
        lambda: pytest.fail("BB84 must not start for invalid paths.")
    )

    with pytest.raises(ValueError, match="must be different"):
        transfer_file(source, encrypted, decrypted)

    assert source.read_text(encoding="utf-8") == "keep this file"


def test_transfer_rejects_identical_encrypted_and_decrypted_paths(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("payload", encoding="utf-8")
    output = tmp_path / "same-output"

    with pytest.raises(ValueError, match="must be different"):
        transfer_file(source, output, output)


def test_decrypt_rejects_tampered_tag_without_writing_plaintext(
    tmp_path
):
    source = tmp_path / "source.txt"
    encrypted = tmp_path / "source.enc"
    decrypted = tmp_path / "restored.txt"
    key = VALID_SESSION["key"]

    source.write_bytes(b"authenticated payload")
    encrypt_file(source, encrypted, key)

    data = bytearray(encrypted.read_bytes())
    data[8 + 12] ^= 1
    encrypted.write_bytes(data)

    with pytest.raises(ValueError, match="Authentication failed"):
        decrypt_file(encrypted, decrypted, key)

    assert not decrypted.exists()


def test_decrypt_rejects_wrong_key(tmp_path):
    source = tmp_path / "source.txt"
    encrypted = tmp_path / "source.enc"
    decrypted = tmp_path / "restored.txt"

    source.write_bytes(b"payload")
    encrypt_file(source, encrypted, VALID_SESSION["key"])

    wrong_key = [1 - bit for bit in VALID_SESSION["key"]]

    with pytest.raises(ValueError, match="Authentication failed"):
        decrypt_file(encrypted, decrypted, wrong_key)

    assert not decrypted.exists()
