"""Create the two explicit Windows release archives without local capture data."""

from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from vendor_mitmdump import require_distribution_clearance


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
COMMON = ("capture.py", "model_probe.py", "MITMPROXY_LICENSE.txt")


def main() -> None:
    require_distribution_clearance()
    DIST.mkdir(exist_ok=True)
    hashes = []
    for language in ("ko", "en"):
        files = (
            DIST / f"CodexModelMonitor-{language}.exe",
            DIST / "mitmdump.exe",
            *(ROOT / name for name in COMMON),
            ROOT / f"README.{language}.md",
        )
        missing = [str(path) for path in files if not path.is_file()]
        if missing:
            raise FileNotFoundError(", ".join(missing))
        archive = DIST / f"codex-model-probe-{language}-win64.zip"
        with ZipFile(archive, "w", ZIP_DEFLATED) as output:
            for path in files:
                output.write(path, path.name)
        with ZipFile(archive) as check:
            assert set(check.namelist()) == {path.name for path in files}
            assert check.testzip() is None
        hashes.append(f"{sha256(archive.read_bytes()).hexdigest()}  {archive.name}")
        print(f"Created {archive}")
    (DIST / "SHA256SUMS.txt").write_text("\n".join(hashes) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
