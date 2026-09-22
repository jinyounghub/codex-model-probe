import os
import ast
import queue
import ssl
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import gui
from gui import (App, clean_child_environment, edition_language, install_current_user_ca,
                 mitmproxy_certificate_trusted, model_comparison, terminate_process_tree)
from translations import EN, translate


class ProxyFailureTests(unittest.TestCase):
    def make_app(self, directory: Path):
        app = object.__new__(App)
        app.watch_only = False
        app.quick_active = False
        app.desktop_relaunch_pending = False
        # A previous process may have exited before the next launch fails.
        app.proc = SimpleNamespace(poll=lambda: 1)
        for name, value in {
            "mitmdump_var": str(directory / "mitmdump.exe"),
            "mode_var": "수동 HTTP 프록시", "port_var": "8080",
            "hosts_var": "chatgpt.com", "output_var": str(directory / "results.jsonl"),
        }.items():
            setattr(app, name, Mock(get=Mock(return_value=value)))
        for name in ("root", "quick_button", "quick_stop_button", "status_var",
                     "_update_mode", "_set_tail_start", "_reset_live_state"):
            setattr(app, name, Mock())
        return app

    def test_blocked_launch_does_not_continue_to_certificate_or_relaunch(self):
        for code in (225, 226):
            with self.subTest(winerror=code), tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                (folder / "mitmdump.exe").write_text("test placeholder; never executed")
                app = self.make_app(folder)
                error = OSError("blocked by security software")
                error.winerror = code
                with patch("gui.subprocess.Popen", side_effect=error) as popen, \
                     patch("gui.messagebox.showerror") as dialog, \
                     patch("gui.codex_desktop_executable", return_value=folder / "Codex.exe"), \
                     patch.object(App, "available_port", return_value=8080), \
                     patch("gui.install_current_user_ca") as install:
                    app.quick_start()
                self.assertIsNone(app.proc)
                self.assertFalse(app.quick_active)
                app.root.after.assert_not_called()
                install.assert_not_called()
                popen.assert_called_once()
                self.assertEqual(dialog.call_args.args[0], "프록시 보안 차단")

    def test_missing_runtime_stops_without_launching_and_mentions_protection_history(self):
        with tempfile.TemporaryDirectory() as directory:
            app = self.make_app(Path(directory))
            with patch("gui.subprocess.Popen") as popen, patch("gui.messagebox.showerror") as dialog:
                app.start_proxy()
            popen.assert_not_called()
            self.assertIsNone(app.proc)
            self.assertIn("보호 기록", dialog.call_args.args[1])
            self.assertIn(str(Path(directory) / "mitmdump.exe"), dialog.call_args.args[1])

    def test_packaged_gui_keeps_missing_bundle_path_instead_of_falling_back(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.dict(os.environ, {}, clear=True), \
             patch.object(gui.sys, "frozen", True, create=True), \
             patch.object(gui, "HERE", Path(directory)), \
             patch("gui.shutil.which") as which:
            self.assertEqual(gui.default_mitmdump(), str(Path(directory) / "mitmdump.exe"))
            which.assert_not_called()


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

    def test_quick_install_targets_only_the_local_current_user_root(self):
        with tempfile.TemporaryDirectory() as directory:
            cert = Path(directory) / "mitmproxy-ca-cert.cer"
            cert.write_text(ssl.DER_cert_to_PEM_cert(b"\x30\x03\x02\x01\x01"), encoding="ascii")
            with patch("gui.local_ca_certificate", return_value=cert), \
                 patch("gui.mitmproxy_certificate_trusted", return_value=True), \
                 patch("gui.subprocess.run", return_value=SimpleNamespace(returncode=0)) as run:
                install_current_user_ca(cert)
                self.assertEqual(run.call_args.args[0],
                                 ["certutil.exe", "-user", "-addstore", "Root", str(cert)])
                with self.assertRaises(ValueError):
                    install_current_user_ca(Path(directory) / "other.cer")
                self.assertEqual(run.call_count, 1)


class QuickStartTests(unittest.TestCase):
    def test_one_click_reuses_running_proxy_and_schedules_readiness_check(self):
        app = object.__new__(App)
        app.watch_only = False
        app.quick_active = False
        app.desktop_relaunch_pending = False
        app.proc = SimpleNamespace(poll=lambda: None)
        app.mode_var = Mock()
        app._update_mode = Mock()
        app.quick_button = Mock()
        app.quick_stop_button = Mock()
        app.status_var = Mock()
        app.root = Mock()
        with patch("gui.codex_desktop_executable", return_value=Path("C:/Codex/ChatGPT.exe")):
            app.quick_start()
        self.assertTrue(app.quick_active)
        app.root.after.assert_called_once_with(200, app._quick_wait)
        app.quick_button.configure.assert_called_with(state="disabled")

    def test_certificate_is_not_installed_without_explicit_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            cert = Path(directory) / "mitmproxy-ca-cert.cer"
            cert.write_text("certificate", encoding="ascii")
            app = object.__new__(App)
            app.quick_active = True
            app.quick_deadline = time.monotonic() + 10
            app.proc = SimpleNamespace(poll=lambda: None)
            app.port_var = Mock()
            app.port_var.get.return_value = "8080"
            app.quick_button = Mock()
            app.status_var = Mock()
            app.stop_proxy = Mock()
            with patch("gui.socket.create_connection"), \
                 patch("gui.local_ca_certificate", return_value=cert), \
                 patch("gui.mitmproxy_certificate_trusted", return_value=False), \
                 patch("gui.certificate_fingerprint", return_value="FINGERPRINT"), \
                 patch("gui.messagebox.askyesno", return_value=False), \
                 patch("gui.install_current_user_ca") as install:
                app._quick_wait()
            install.assert_not_called()
            app.stop_proxy.assert_called_once()
            self.assertFalse(app.quick_active)

    @unittest.skipUnless(os.name == "nt", "Windows process tree behavior")
    def test_stop_covers_standalone_proxy_child_process(self):
        proc = SimpleNamespace(pid=1234, poll=Mock(side_effect=[None, 1]), terminate=Mock())
        with patch("gui.subprocess.run") as run:
            terminate_process_tree(proc)
        self.assertEqual(run.call_args.args[0], ["taskkill.exe", "/PID", "1234", "/T", "/F"])
        proc.terminate.assert_not_called()


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
