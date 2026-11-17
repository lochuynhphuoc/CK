import secrets
from Crypto.Cipher import AES


KEY_LENGTH = 32
NONCE_LENGTH = 12
TAG_LENGTH = 16


def _normalize_key(key):
    if isinstance(key, (list, tuple)):
        if len(key) != 256:
            raise ValueError("AES-256 requires exactly 256 key bits.")

        if any(bit not in (0, 1) for bit in key):
            raise ValueError("Key must contain only 0 and 1.")

        key = bytes(
            int("".join(map(str, key[index:index + 8])), 2)
            for index in range(0, 256, 8)
        )

    if not isinstance(key, bytes) or len(key) != KEY_LENGTH:
        raise ValueError("AES-256 requires a 32-byte key.")

    return key


def encrypt_data(plaintext, key, associated_data=None):
    key = _normalize_key(key)

    if isinstance(plaintext, str):
        plaintext = plaintext.encode("utf-8")

    if not isinstance(plaintext, bytes):
        raise TypeError("Plaintext must be a string or bytes.")

    if associated_data is not None and not isinstance(
        associated_data, bytes
    ):
        raise TypeError("Associated data must be bytes.")

    nonce = secrets.token_bytes(NONCE_LENGTH)

    cipher = AES.new(
        key,
        AES.MODE_GCM,
        nonce=nonce,
        mac_len=TAG_LENGTH
    )

    if associated_data is not None:
        cipher.update(associated_data)

    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    return {
        "nonce": nonce,
        "ciphertext": ciphertext,
        "tag": tag
    }


def decrypt_data(
    encrypted_data,
    key,
    associated_data=None
):
    key = _normalize_key(key)

    if not isinstance(encrypted_data, dict):
        raise TypeError("Encrypted data must be a dictionary.")

    try:
        nonce = encrypted_data["nonce"]
        ciphertext = encrypted_data["ciphertext"]
        tag = encrypted_data["tag"]
    except KeyError as exc:
        raise ValueError("Encrypted data is incomplete.") from exc

    if not isinstance(nonce, bytes) or len(nonce) != NONCE_LENGTH:
        raise ValueError("Invalid nonce.")

    if not isinstance(tag, bytes) or len(tag) != TAG_LENGTH:
        raise ValueError("Invalid authentication tag.")

    if not isinstance(ciphertext, bytes):
        raise TypeError("Ciphertext must be bytes.")

    if associated_data is not None and not isinstance(
        associated_data, bytes
    ):
        raise TypeError("Associated data must be bytes.")

    cipher = AES.new(
        key,
        AES.MODE_GCM,
        nonce=nonce,
        mac_len=TAG_LENGTH
    )

    if associated_data is not None:
        cipher.update(associated_data)

    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError as exc:
        raise ValueError(
            "Authentication failed: data may have been modified."
        ) from exc

    return plaintext
