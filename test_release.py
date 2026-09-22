"""A detected runtime must not be restored by the release tooling."""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import package_release
import vendor_mitmdump


class DistributionHoldTests(unittest.TestCase):
    def test_vendor_stops_before_download_or_extraction(self):
        with patch("vendor_mitmdump.urlopen") as download, \
             patch("vendor_mitmdump.ZipFile") as archive, \
             patch("vendor_mitmdump.ARCHIVE") as path:
            with self.assertRaisesRegex(RuntimeError, "distribution is on hold"):
                vendor_mitmdump.main()
            download.assert_not_called()
            archive.assert_not_called()
            path.parent.mkdir.assert_not_called()

    def test_new_package_rejects_drivers_old_runtime_and_private_records(self):
        for filename in ("WinDivert64.sys", "windows-redirector.exe", "mitmdump.exe", "results.jsonl", "mitmproxy-ca.pem"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as directory:
                bundle = Path(directory)
                (bundle / filename).write_text("test fixture")
                with self.assertRaisesRegex(ValueError, "Unexpected release file"):
                    package_release.validate_bundle(bundle, require_manifest=False)

    def test_manifest_detects_modified_bundled_files(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory)
            (bundle / "app.txt").write_text("original")
            package_release.write_manifest(bundle)
            package_release.validate_bundle(bundle)
            (bundle / "app.txt").write_text("changed")
            with self.assertRaisesRegex(ValueError, "manifest mismatch"):
                package_release.validate_bundle(bundle)


if __name__ == "__main__":
    unittest.main()
