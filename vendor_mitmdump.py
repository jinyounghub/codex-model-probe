"""Fetch the pinned official Windows standalone mitmdump for release packaging."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "build" / "vendor" / "mitmproxy-12.2.3-windows-x86_64.zip"
OUTPUT = ROOT / "dist" / "mitmdump.exe"
URL = "https://snapshots.mitmproxy.org/12.2.3/mitmproxy-12.2.3-windows-x86_64.zip"
SHA256 = "04a01ea95ae96df75058a893e774957d294e69012dab1f4e256ce2b0c6725483"
MITMDUMP_SHA256 = "36a45aadeb842185b8064b8f0be3730e079c9f9c125bc8be22363332969857bf"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE.is_file():
        print(f"Downloading official mitmproxy 12.2.3: {URL}", flush=True)
        partial = ARCHIVE.with_suffix(".partial")
        try:
            with urlopen(URL, timeout=30) as source, partial.open("wb") as destination:
                shutil.copyfileobj(source, destination)
            partial.replace(ARCHIVE)
        finally:
            partial.unlink(missing_ok=True)
    digest = file_sha256(ARCHIVE)
    if digest != SHA256:
        raise ValueError(f"mitmproxy archive SHA256 mismatch: {digest}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.is_file() and file_sha256(OUTPUT) == MITMDUMP_SHA256:
        print(f"Verified existing {OUTPUT}", flush=True)
        return
    with ZipFile(ARCHIVE) as archive:
        with archive.open("mitmdump.exe") as source, OUTPUT.open("wb") as destination:
            shutil.copyfileobj(source, destination)
    if file_sha256(OUTPUT) != MITMDUMP_SHA256:
        OUTPUT.unlink(missing_ok=True)
        raise ValueError("mitmdump.exe SHA256 mismatch")
    print(f"Verified and extracted {OUTPUT}", flush=True)


if __name__ == "__main__":
    main()
