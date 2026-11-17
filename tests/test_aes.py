from encryption.aes_gcm import encrypt_data, decrypt_data


def test_encryption_decryption():
    key = [i % 2 for i in range(256)]
    message = "BB84 and AES-256-GCM"

    encrypted = encrypt_data(message, key)
    decrypted = decrypt_data(encrypted, key)

    assert decrypted.decode("utf-8") == message

    print("[PASS] Encryption and decryption")
    print("[PASS] Original and decrypted data match")


def test_ciphertext_tampering():
    key = [i % 2 for i in range(256)]
    encrypted = encrypt_data("BB84 and AES-256-GCM", key)

    tampered = encrypted.copy()

    tampered["ciphertext"] = (
        bytes([tampered["ciphertext"][0] ^ 1])
        + tampered["ciphertext"][1:]
    )

    try:
        decrypt_data(tampered, key)
        raise AssertionError("Tampered ciphertext was accepted.")
    except ValueError as error:
        if "Authentication failed" not in str(error):
            raise

    print("[PASS] Tampered ciphertext rejected")


def test_tag_tampering():
    key = [i % 2 for i in range(256)]
    encrypted = encrypt_data("BB84 and AES-256-GCM", key)

    tampered = encrypted.copy()

    tampered["tag"] = (
        bytes([tampered["tag"][0] ^ 1])
        + tampered["tag"][1:]
    )

    try:
        decrypt_data(tampered, key)
        raise AssertionError("Tampered tag was accepted.")
    except ValueError as error:
        if "Authentication failed" not in str(error):
            raise

    print("[PASS] Tampered authentication tag rejected")


if __name__ == "__main__":
    test_encryption_decryption()
    test_ciphertext_tampering()
    test_tag_tampering()

    print("\nAll AES tests passed.")
