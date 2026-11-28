
import csv
import hashlib
import os
from pathlib import Path


OUTPUT_DIR = Path("data/benchmark")

FILE_TYPES = {
    ".txt": b"BB84 AES-256-GCM synthetic text test file\n",
    ".docx": b"PK\x03\x04",
    ".png": b"\x89PNG\r\n\x1a\n",
    ".jpg": b"\xff\xd8\xff",
    ".wav": b"RIFF\x00\x00\x00\x00WAVE",
    ".mp3": b"ID3\x04\x00\x00",
    ".mp4": b"\x00\x00\x00\x18ftypmp42",
}

SIZES = {
    "1KB": 1 * 1024,
    "100KB": 100 * 1024,
    "1MB": 1 * 1024 * 1024,
    "10MB": 10 * 1024 * 1024,
    "50MB": 50 * 1024 * 1024,
}

CHUNK_SIZE = 1024 * 1024


def calculate_sha256(file_path):
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(CHUNK_SIZE), b""):
            digest.update(chunk)

    return digest.hexdigest()


def write_test_file(file_path, extension, target_size):
    header = FILE_TYPES[extension]

    if target_size < len(header):
        raise ValueError(f"Target size too small for {extension}")

    file_path.parent.mkdir(parents=True, exist_ok=True)

    remaining = target_size

    with file_path.open("wb") as file:
        file.write(header)
        remaining -= len(header)

        if extension == ".txt":
            pattern = FILE_TYPES[".txt"]

            while remaining > 0:
                chunk = pattern[:min(len(pattern), remaining)]
                file.write(chunk)
                remaining -= len(chunk)
        else:
            while remaining > 0:
                chunk_size = min(CHUNK_SIZE, remaining)
                file.write(os.urandom(chunk_size))
                remaining -= chunk_size

    if file_path.stat().st_size != target_size:
        raise RuntimeError(f"Incorrect file size: {file_path}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = []

    total_files = 0
    total_bytes = 0

    print("=" * 60)
    print("BB84 + AES-256-GCM TEST DATA GENERATOR")
    print("=" * 60)

    for extension in FILE_TYPES:
        type_dir = OUTPUT_DIR / extension.replace(".", "")

        for size_label, target_size in SIZES.items():
            file_name = f"sample_{size_label}{extension}"
            file_path = type_dir / file_name

            write_test_file(file_path, extension, target_size)

            file_hash = calculate_sha256(file_path)

            manifest.append({
                "file_name": file_name,
                "file_type": extension,
                "size_label": size_label,
                "size_bytes": target_size,
                "file_path": str(file_path).replace("\\", "/"),
                "sha256": file_hash
            })

            total_files += 1
            total_bytes += target_size

            print(
                f"[OK] {extension:5} | "
                f"{size_label:5} | "
                f"{target_size:>10,} bytes | "
                f"{file_path}"
            )

    manifest_path = OUTPUT_DIR / "manifest.csv"

    with manifest_path.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "file_name",
                "file_type",
                "size_label",
                "size_bytes",
                "file_path",
                "sha256"
            ]
        )

        writer.writeheader()
        writer.writerows(manifest)

    print("\n" + "=" * 60)
    print("GENERATION COMPLETED")
    print("=" * 60)
    print("Total files:", total_files)
    print("Total size:", f"{total_bytes / (1024 * 1024):.2f} MB")
    print("Manifest:", manifest_path)


if __name__ == "__main__":
    main()
