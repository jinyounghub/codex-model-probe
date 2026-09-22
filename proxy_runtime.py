"""Explicit loopback HTTP proxy for the monitor; no process/driver capture.

This entry point intentionally does not expose mitmdump's general CLI, load
config.yaml, run user scripts, or select local/transparent/WireGuard modes.
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
import types
from pathlib import Path

ALLOWED_HOSTS = frozenset({"chatgpt.com", "api.openai.com"})


def disable_transparent_capture() -> None:
    """Provide no OS redirection API to mitmproxy's regular HTTP server.

    Upstream imports its Windows transparent-mode adapter unconditionally,
    including pydivert. This application has no transparent mode, so its
    adapter explicitly reports that original-destination lookup is unavailable.
    The original platform module and both driver packages are excluded at build.
    """
    adapter = types.ModuleType("mitmproxy.platform")
    adapter.original_addr = None

    def unsupported():
        raise RuntimeError("Transparent/process capture is not included in Codex Model Probe")

    adapter.init_transparent_mode = unsupported
    sys.modules["mitmproxy.platform"] = adapter
    # mitmproxy_rs checks for this module on import even in regular mode.
    # Supply only an explicitly unsupported provider, never a redirector path.
    if sys.platform == "win32":
        redirector = types.ModuleType("mitmproxy_windows")
        redirector.executable_path = unsupported
        sys.modules["mitmproxy_windows"] = redirector


def parse_hosts(value: str) -> tuple[str, ...]:
    hosts = tuple(sorted({host.strip().lower() for host in value.split(",") if host.strip()}))
    if not hosts or not set(hosts) <= ALLOWED_HOSTS:
        raise ValueError("Hosts must be chatgpt.com and/or api.openai.com")
    return hosts


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--port", type=int, required=True)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--hosts", default="chatgpt.com,api.openai.com")
    result.add_argument("--confdir", type=Path, default=Path.home() / ".mitmproxy")
    return result


def proxy_options(args) -> dict:
    if not 1 <= args.port <= 65535:
        raise ValueError("Port must be between 1 and 65535")
    hosts = parse_hosts(args.hosts)
    return {
        "mode": ["regular"],
        "listen_host": "127.0.0.1",
        "listen_port": args.port,
        "confdir": str(args.confdir),
        "allow_hosts": [rf"^{re.escape(host)}(?::443)?$" for host in hosts],
        "ssl_insecure": False,
    }


async def serve(args) -> None:
    disable_transparent_capture()
    from mitmproxy import options
    from mitmproxy.tools.dump import DumpMaster
    from capture import ModelProbe

    master = DumpMaster(options.Options(**proxy_options(args)), with_termlog=False, with_dumper=False)
    master.addons.add(ModelProbe())
    master.options.update(
        modelprobe_output=str(args.output), modelprobe_hosts=",".join(parse_hosts(args.hosts)),
        scripts=[], save_stream_file=None, hardump="", onboarding=False,
    )
    await master.run()


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    proxy_options(args)  # Validate before initializing the proxy or its CA.
    asyncio.run(serve(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
