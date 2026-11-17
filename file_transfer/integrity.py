import hashlib
from pathlib import Path


def calculate_sha256(file_path):
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def verify_file_integrity(original_path, decrypted_path):
    original_hash = calculate_sha256(original_path)
    decrypted_hash = calculate_sha256(decrypted_path)

    return {
        "original_sha256": original_hash,
        "decrypted_sha256": decrypted_hash,
        "verified": original_hash == decrypted_hash
    }