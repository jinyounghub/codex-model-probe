"""Package v0.4 folders with a file inventory and no packet-capture drivers."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent
VERSION = "0.4.0"
DIST = ROOT / "dist" / VERSION
BUNDLE_ROOT = DIST / "bundles"


def file_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def forbidden_file(path: Path) -> bool:
    name = str(path).lower().replace("\\", "/")
    return (any(value in name for value in ("windivert", "windows-redirector", "mitmproxy_windows", "pydivert", "mitmdump.exe", "mitmproxy-ca"))
            or path.suffix.lower() in {".sys", ".jsonl", ".mitm"}
            or path.name.lower() in {"auth.json", "config.toml", "state_5.sqlite"})


def inventory(bundle: Path) -> dict[str, str]:
    return {path.relative_to(bundle).as_posix(): file_hash(path)
            for path in sorted(bundle.rglob("*")) if path.is_file() and path.name != "BUNDLE-MANIFEST.json"}


def write_manifest(bundle: Path) -> None:
    manifest = {"version": VERSION, "proxy_mode": "regular", "bind": "127.0.0.1",
                "process_capture": False, "packet_capture_drivers": False, "files": inventory(bundle)}
    (bundle / "BUNDLE-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def validate_bundle(bundle: Path, require_manifest: bool = True) -> None:
    if not bundle.is_dir():
        raise FileNotFoundError(bundle)
    for path in bundle.rglob("*"):
        if path.is_symlink() or forbidden_file(path.relative_to(bundle)):
            raise ValueError(f"Unexpected release file: {path.relative_to(bundle)}")
    if require_manifest:
        manifest = json.loads((bundle / "BUNDLE-MANIFEST.json").read_text(encoding="utf-8"))
        if manifest.get("version") != VERSION or manifest.get("files") != inventory(bundle):
            raise ValueError(f"Bundle manifest mismatch: {bundle.name}")


def validate_module_inventory(bundle: Path) -> None:
    from PyInstaller.archive.readers import CArchiveReader
    exe = bundle / (bundle.name + ".exe")
    archive = CArchiveReader(str(exe)).open_embedded_archive("PYZ.pyz")
    prohibited = [name for name in archive.toc
                  if name.startswith(("pydivert", "mitmproxy_windows", "mitmproxy.platform"))]
    if prohibited:
        raise ValueError(f"Capture modules included in bundle: {prohibited}")


def main() -> None:
    bundles = [BUNDLE_ROOT / f"CodexModelMonitor-{language}" for language in ("ko", "en")]
    for bundle in bundles:
        validate_bundle(bundle)
        validate_module_inventory(bundle)
    for language, bundle in zip(("ko", "en"), bundles):
        archive = DIST / f"codex-model-probe-{language}-win64.zip"
        with ZipFile(archive, "w", ZIP_DEFLATED) as output:
            for path in sorted(bundle.rglob("*")):
                if path.is_file():
                    output.write(path, path.relative_to(bundle).as_posix())
        print(f"Created {archive}")
    artifacts = sorted(DIST.glob("*.zip")) + sorted(DIST.glob("CodexModelProbe-Setup-*.exe"))
    (DIST / "SHA256SUMS.txt").write_text("".join(f"{file_hash(path)}  {path.name}\n" for path in artifacts), encoding="ascii")


if __name__ == "__main__":
    main()
