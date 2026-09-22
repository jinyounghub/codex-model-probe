"""A detected runtime must not be restored by the release tooling."""

import unittest
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

    def test_packaging_stops_before_writing_release_files(self):
        with patch("package_release.DIST") as dist, patch("package_release.ZipFile") as archive:
            with self.assertRaisesRegex(RuntimeError, "distribution is on hold"):
                package_release.main()
            dist.mkdir.assert_not_called()
            archive.assert_not_called()


if __name__ == "__main__":
    unittest.main()
