import os
import ast
import queue
import ssl
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import gui
from gui import App, clean_child_environment, edition_language, mitmproxy_certificate_trusted, model_comparison
from translations import EN, translate


class DisplayTests(unittest.TestCase):
    def test_pyinstaller_tcl_paths_are_not_passed_to_children(self):
        with patch.dict(os.environ, {"TCL_LIBRARY": "stale", "TK_LIBRARY": "stale",
                                     "_PYI_APPLICATION_HOME_DIR": "stale", "KEEP_ME": "yes"}):
            child = clean_child_environment()
        self.assertNotIn("TCL_LIBRARY", child)
        self.assertNotIn("TK_LIBRARY", child)
        self.assertNotIn("_PYI_APPLICATION_HOME_DIR", child)
        self.assertEqual(child["KEEP_ME"], "yes")

    def test_model_values_are_compared_only_when_both_are_present(self):
        self.assertEqual(model_comparison({"requested_model": "a", "model": "a"}), "값 일치")
        self.assertEqual(model_comparison({"requested_model": "a", "model": "b"}), "값 다름")
        self.assertEqual(model_comparison({"requested_model": None, "model": "b"}), "확인 불가")

    def test_english_gui_has_every_translated_label(self):
        tree = ast.parse(Path(gui.__file__).read_text(encoding="utf-8"))
        keys = {
            node.args[0].value for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "tr" and node.args
            and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)
        }
        self.assertFalse(keys - EN.keys())
        self.assertEqual(translate("최종 응답 모델", "en"), "Final response model")
        self.assertEqual(translate("최종 응답 모델", "ko"), "최종 응답 모델")

    def test_comparison_uses_selected_gui_language(self):
        original = gui.LANGUAGE
        try:
            gui.LANGUAGE = "en"
            self.assertEqual(model_comparison({"requested_model": "a", "model": "b"}), "Values differ")
        finally:
            gui.LANGUAGE = original

    def test_executable_name_selects_language(self):
        self.assertEqual(edition_language("C:/tool/CodexModelMonitor-ko.exe"), "ko")
        self.assertEqual(edition_language("C:/tool/CodexModelMonitor-en.exe"), "en")


class CertificateTests(unittest.TestCase):
    def test_installed_ca_matches_current_user_root(self):
        with tempfile.TemporaryDirectory() as directory:
            cert_dir = Path(directory) / ".mitmproxy"
            cert_dir.mkdir()
            der = b"\x30\x03\x02\x01\x01"
            (cert_dir / "mitmproxy-ca-cert.cer").write_text(ssl.DER_cert_to_PEM_cert(der))
            with patch("gui.Path.home", return_value=Path(directory)), \
                 patch("gui.ssl.enum_certificates", return_value=[(der, "x509_asn", set())]):
                self.assertIs(mitmproxy_certificate_trusted(), True)


class DesktopRelaunchTests(unittest.TestCase):
    def test_desktop_child_receives_only_scoped_proxy_environment(self):
        app = object.__new__(App)
        app.proc = SimpleNamespace(poll=lambda: None)
        app.desktop_messages = queue.Queue()
        app.desktop_launch_cancel = threading.Event()
        app.desktop_relaunch_pending = True
        original_http_proxy = os.environ.get("HTTP_PROXY")
        executable = Path(r"C:\Program Files\WindowsApps\OpenAI.Codex\app\ChatGPT.exe")
        with patch("gui.codex_desktop_running", return_value=False), patch("gui.subprocess.Popen") as popen:
            app._relaunch_desktop_when_closed(executable, "http://127.0.0.1:8080",
                                              app.desktop_launch_cancel)
        args, kwargs = popen.call_args
        self.assertEqual(args[0], [str(executable)])
        self.assertEqual(kwargs["env"]["HTTPS_PROXY"], "http://127.0.0.1:8080")
        self.assertEqual(kwargs["env"]["HTTP_PROXY"], "http://127.0.0.1:8080")
        self.assertTrue(kwargs["env"]["CODEX_CA_CERTIFICATE"].endswith("mitmproxy-ca-cert.pem"))
        self.assertEqual(os.environ.get("HTTP_PROXY"), original_http_proxy)


if __name__ == "__main__":
    unittest.main()
