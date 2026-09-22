import contextlib
import io
import re
import sys
import unittest
from unittest.mock import patch

from proxy_runtime import parser, parse_hosts, proxy_options, disable_transparent_capture


class RestrictedProxyTests(unittest.TestCase):
    def test_platform_adapters_cannot_supply_a_driver_or_redirect_traffic(self):
        with patch.dict(sys.modules), patch.object(sys, "platform", "win32"):
            disable_transparent_capture()
            self.assertIsNone(sys.modules["mitmproxy.platform"].original_addr)
            with self.assertRaisesRegex(RuntimeError, "not included"):
                sys.modules["mitmproxy.platform"].init_transparent_mode()
            with self.assertRaisesRegex(RuntimeError, "not included"):
                sys.modules["mitmproxy_windows"].executable_path()

    def test_explicit_loopback_only_and_verified_upstream_tls(self):
        args = parser().parse_args(["--port", "8080", "--output", "fixture.jsonl"])
        options = proxy_options(args)
        self.assertEqual(options["listen_host"], "127.0.0.1")
        self.assertEqual(options["mode"], ["regular"])
        self.assertIs(options["ssl_insecure"], False)
        patterns = options["allow_hosts"]
        for allowed in ("chatgpt.com", "api.openai.com:443"):
            self.assertTrue(any(re.fullmatch(pattern, allowed) for pattern in patterns))
        for unrelated in ("example.com", "chatgpt.com.example.com", "api.openai.com:8080"):
            self.assertFalse(any(re.fullmatch(pattern, unrelated) for pattern in patterns))

    def test_arbitrary_hosts_and_capture_modes_are_not_available(self):
        for hosts in ("", "example.com", ".*", "chatgpt.com,example.com"):
            with self.subTest(hosts=hosts), self.assertRaises(ValueError):
                parse_hosts(hosts)
        for option in (["--mode", "local:codex"], ["--listen-host", "0.0.0.0"], ["-s", "addon.py"]):
            with self.subTest(option=option), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                parser().parse_args(["--port", "8080", "--output", "fixture.jsonl", *option])


if __name__ == "__main__":
    unittest.main()
