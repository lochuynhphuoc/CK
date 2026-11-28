import time
from pathlib import Path

from encryption.aes_gcm import (
    encrypt_data,
    decrypt_data,
    NONCE_LENGTH,
    TAG_LENGTH
)


FILE_MAGIC = b"BB84GCM1"
HEADER_LENGTH = len(FILE_MAGIC)


def _ensure_distinct_files(input_path, output_path, message):
    input_path = Path(input_path)
    output_path = Path(output_path)

    if input_path.resolve() == output_path.resolve():
        raise ValueError(message)

    if input_path.exists() and output_path.exists():
        try:
            same_file = input_path.samefile(output_path)
        except OSError:
            same_file = False
        if same_file:
            raise ValueError(message)


def encrypt_file(input_path, encrypted_path, key):
    input_path = Path(input_path)
    encrypted_path = Path(encrypted_path)

    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    _ensure_distinct_files(
        input_path,
        encrypted_path,
        "Input and encrypted file must be different."
    )

    plaintext = input_path.read_bytes()

    start_time = time.perf_counter()

    encrypted_data = encrypt_data(
        plaintext,
        key,
        associated_data=FILE_MAGIC
    )

    encryption_time = time.perf_counter() - start_time

    encrypted_content = (
        FILE_MAGIC
        + encrypted_data["nonce"]
        + encrypted_data["tag"]
        + encrypted_data["ciphertext"]
    )

    encrypted_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    encrypted_path.write_bytes(encrypted_content)

    return {
        "input_size": len(plaintext),
        "encrypted_size": len(encrypted_content),
        "encryption_time": encryption_time,
        "encrypted_path": str(encrypted_path)
    }


def decrypt_file(encrypted_path, output_path, key):
    encrypted_path = Path(encrypted_path)
    output_path = Path(output_path)

    if not encrypted_path.is_file():
        raise FileNotFoundError(
            f"Encrypted file not found: {encrypted_path}"
        )

    _ensure_distinct_files(
        encrypted_path,
        output_path,
        "Encrypted and decrypted file must be different."
    )

    encrypted_content = encrypted_path.read_bytes()

    minimum_length = (
        HEADER_LENGTH
        + NONCE_LENGTH
        + TAG_LENGTH
    )

    if len(encrypted_content) < minimum_length:
        raise ValueError("Encrypted file is incomplete.")

    magic = encrypted_content[:HEADER_LENGTH]

    if magic != FILE_MAGIC:
        raise ValueError("Invalid encrypted file format.")

    nonce_start = HEADER_LENGTH
    tag_start = nonce_start + NONCE_LENGTH
    ciphertext_start = tag_start + TAG_LENGTH

    encrypted_data = {
        "nonce": encrypted_content[nonce_start:tag_start],
        "tag": encrypted_content[tag_start:ciphertext_start],
        "ciphertext": encrypted_content[ciphertext_start:]
    }

    start_time = time.perf_counter()

    plaintext = decrypt_data(
        encrypted_data,
        key,
        associated_data=FILE_MAGIC
    )

    decryption_time = time.perf_counter() - start_time

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path.write_bytes(plaintext)

    return {
        "decrypted_size": len(plaintext),
        "decryption_time": decryption_time,
        "output_path": str(output_path)
    }
