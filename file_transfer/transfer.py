from pathlib import Path

from bb84.session import run_bb84_session
from encryption.file_encryption import encrypt_file, decrypt_file
from file_transfer.integrity import verify_file_integrity


def _validate_transfer_paths(source_path, encrypted_path, decrypted_path):
    paths = {
        "source": Path(source_path).resolve(),
        "encrypted": Path(encrypted_path).resolve(),
        "decrypted": Path(decrypted_path).resolve()
    }

    if len(set(paths.values())) != len(paths):
        duplicates = []
        names = list(paths)
        for index, first in enumerate(names):
            for second in names[index + 1:]:
                if paths[first] == paths[second]:
                    duplicates.append(f"{first} and {second}")

        raise ValueError(
            "Source, encrypted, and decrypted paths must be different: "
            + ", ".join(duplicates)
        )


def transfer_file(
    source_path,
    encrypted_path,
    decrypted_path
):
    source_path = Path(source_path)
    encrypted_path = Path(encrypted_path)
    decrypted_path = Path(decrypted_path)

    if not source_path.is_file():
        raise FileNotFoundError(
            f"Source file not found: {source_path}"
        )

    _validate_transfer_paths(
        source_path,
        encrypted_path,
        decrypted_path
    )

    result = {
        "success": False,
        "status": "ABORT",
        "reason": None,
        "file_name": source_path.name,
        "file_type": source_path.suffix.lower(),
        "file_size": source_path.stat().st_size,
        "bb84_metrics": {},
        "encryption_metrics": {},
        "decryption_metrics": {},
        "integrity": {}
    }

    session = run_bb84_session()

    result["bb84_metrics"] = session["metrics"]

    if not session["success"]:
        result["reason"] = session.get(
            "reason",
            "BB84 key generation failed."
        )
        return result

    key = session["key"]

    try:
        encryption_result = encrypt_file(
            source_path,
            encrypted_path,
            key
        )

        result["encryption_metrics"] = encryption_result

        decryption_result = decrypt_file(
            encrypted_path,
            decrypted_path,
            key
        )

        result["decryption_metrics"] = decryption_result

        integrity_result = verify_file_integrity(
            source_path,
            decrypted_path
        )

        result["integrity"] = integrity_result

        if not integrity_result["verified"]:
            result["reason"] = "SHA-256 verification failed."
            return result

    except (ValueError, TypeError, OSError) as error:
        result["reason"] = str(error)
        return result

    result["success"] = True
    result["status"] = "SUCCESS"

    return result
