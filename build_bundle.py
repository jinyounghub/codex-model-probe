"""Build inspectable Windows folders with an embedded, regular-HTTP-only proxy."""

from __future__ import annotations

import importlib.metadata
import subprocess
import sys
from pathlib import Path

from package_release import BUNDLE_ROOT, ROOT, VERSION, write_manifest, validate_bundle, validate_module_inventory


def main() -> None:
    if importlib.metadata.version("mitmproxy") != "12.2.3":
        raise RuntimeError("This build requires mitmproxy==12.2.3")
    for language in ("ko", "en"):
        name = f"CodexModelMonitor-{language}"
        if not (BUNDLE_ROOT / name).resolve().is_relative_to((ROOT / "dist").resolve()):
            raise ValueError("Bundle output must stay under this repository's dist folder")
        subprocess.run([
            sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir",
            "--windowed", "--noupx", "--name", name,
            "--distpath", str(BUNDLE_ROOT), "--workpath", str(ROOT / "build" / VERSION / language),
            "--specpath", str(ROOT / "build" / VERSION),
            "--exclude-module", "mitmproxy_windows", "--exclude-module", "mitmproxy_linux",
            "--exclude-module", "mitmproxy_macos", "--exclude-module", "mitmproxy.tools.console",
            "--exclude-module", "pydivert", "--exclude-module", "mitmproxy.platform",
            "--exclude-module", "mitmproxy.tools.web", "--collect-data", "mitmproxy",
            "--copy-metadata", "mitmproxy", "--copy-metadata", "mitmproxy_rs",
            str(ROOT / "gui.py"),
        ], check=True, cwd=ROOT)
        bundle = BUNDLE_ROOT / name
        for filename in (f"README.{language}.md", "MITMPROXY_LICENSE.txt", "DEFENDER.md"):
            (bundle / filename).write_bytes((ROOT / filename).read_bytes())
        (bundle / "PYTHON_LICENSE.txt").write_bytes((Path(sys.base_prefix) / "LICENSE.txt").read_bytes())
        notices = ["Build environment dependency notices (some build-only packages may be listed).\n"]
        for dist in sorted(importlib.metadata.distributions(), key=lambda item: item.metadata["Name"].lower()):
            if dist.metadata["Name"].lower().replace("_", "-") in {"mitmproxy-windows", "mitmproxy-linux", "mitmproxy-macos", "pydivert"}:
                continue
            notices.append(f"\n=== {dist.metadata['Name']} {dist.version} ===\n")
            for path in dist.files or ():
                if any(word in path.name.lower() for word in ("license", "copying", "notice")) and ".dist-info/" in str(path):
                    notices.append(dist.locate_file(path).read_text(encoding="utf-8", errors="replace"))
        (bundle / "THIRD-PARTY-NOTICES.txt").write_text("\n".join(notices), encoding="utf-8")
        validate_bundle(bundle, require_manifest=False)
        validate_module_inventory(bundle)
        write_manifest(bundle)
        validate_bundle(bundle)


if __name__ == "__main__":
    main()
