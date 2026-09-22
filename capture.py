"""mitmproxy addon: retain only model evidence from completed server responses.

Run with: mitmdump -s capture.py --set modelprobe_output=results.jsonl
"""

import json
import importlib
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

from mitmproxy import ctx, http

import model_probe

# mitmproxy reloads this addon file without necessarily reloading its imported modules.
model_probe = importlib.reload(model_probe)
analyze_body = model_probe.analyze_body
request_metadata = model_probe.request_metadata


class ModelProbe:
    def __init__(self):
        self.pending_ws = defaultdict(deque)
        self.ws_responses = defaultdict(dict)
        self.http_requests = {}

    def load(self, loader):
        loader.add_option("modelprobe_output", str, "modelprobe-results.jsonl",
                          "File for minimal completed-response model records")
        loader.add_option("modelprobe_hosts", str, "chatgpt.com,api.openai.com",
                          "Comma-separated exact HTTP host allowlist")

    def _allowed_host(self, flow: http.HTTPFlow):
        hosts = {host.strip().lower() for host in ctx.options.modelprobe_hosts.split(",")}
        return flow.request.host.lower() in hosts

    def _write(self, record):
        output = Path(ctx.options.modelprobe_output).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    def request(self, flow: http.HTTPFlow):
        if not self._allowed_host(flow) or "/responses" not in flow.request.path:
            return
        try:
            value = json.loads(flow.request.get_text(strict=False))
        except (ValueError, UnicodeError):
            return
        info = request_metadata(value)
        if info:
            self.http_requests[flow.id] = info

    def responseheaders(self, flow: http.HTTPFlow):
        if not self._allowed_host(flow):
            return
        # 101 is only the WebSocket handshake, not a model response.
        if flow.response is not None and flow.response.status_code == 101:
            return
        self._write({
            "kind": "response_seen",
            "time_utc": datetime.now(timezone.utc).isoformat(),
            "host": flow.request.host.lower(),
            "transport": "http",
        })

    def response(self, flow: http.HTTPFlow):
        if not self._allowed_host(flow) or flow.response is None:
            return
        host = flow.request.host.lower()
        info = self.http_requests.pop(flow.id, None)
        # The proxy has already decoded HTTP transport and TLS. Never persist bodies or headers.
        for item in analyze_body(flow.response.get_text(strict=False)):
            self._write_model(host, "http", item, info, "same HTTP flow")

    def websocket_message(self, flow: http.HTTPFlow):
        """Pair a client response.create with server response.created/completed."""
        if not self._allowed_host(flow) or flow.websocket is None:
            return
        message = flow.websocket.messages[-1]
        if message.injected:
            return
        try:
            body = message.content.decode("utf-8")
        except UnicodeDecodeError:
            return
        if message.from_client:
            try:
                value = json.loads(body)
            except json.JSONDecodeError:
                return
            info = request_metadata(value, websocket=True)
            if info:
                self.pending_ws[flow.id].append(info)
            return
        self._write({
            "kind": "response_seen",
            "time_utc": datetime.now(timezone.utc).isoformat(),
            "host": flow.request.host.lower(),
            "transport": "websocket",
        })
        try:
            event = json.loads(body)
        except json.JSONDecodeError:
            event = None
        if isinstance(event, dict):
            response = event.get("response")
            response_id = response.get("id") if isinstance(response, dict) else None
            if event.get("type") == "response.created" and isinstance(response_id, str):
                if self.pending_ws[flow.id]:
                    self.ws_responses[flow.id][response_id] = self.pending_ws[flow.id].popleft()
            elif event.get("type") in ("response.failed", "response.incomplete") and isinstance(response_id, str):
                self.ws_responses[flow.id].pop(response_id, None)
        for item in analyze_body(body):
            response_id = item["response_id"]
            info = self.ws_responses[flow.id].pop(response_id, None) if response_id else None
            self._write_model(flow.request.host.lower(), "websocket", item, info,
                              "response.created.id" if info else None)

    def websocket_end(self, flow: http.HTTPFlow):
        self.pending_ws.pop(flow.id, None)
        self.ws_responses.pop(flow.id, None)

    def error(self, flow: http.HTTPFlow):
        self.http_requests.pop(flow.id, None)
        self.pending_ws.pop(flow.id, None)
        self.ws_responses.pop(flow.id, None)

    def _write_model(self, host, transport, item, info=None, request_pairing=None):
        info = info or {}
        self._write({
            "kind": "model",
            "time_utc": datetime.now(timezone.utc).isoformat(),
            "host": host,
            "transport": transport,
            "response_id": item["response_id"],
            "model": item["model"],
            "evidence": item["evidence"],
            "requested_model": info.get("requested_model"),
            "request_reasoning_effort": info.get("request_reasoning_effort"),
            "request_reasoning_context": info.get("request_reasoning_context"),
            "response_reasoning_effort": item.get("response_reasoning_effort"),
            "response_reasoning_mode": item.get("response_reasoning_mode"),
            "response_reasoning_context": item.get("response_reasoning_context"),
            "reasoning_tokens": item.get("reasoning_tokens"),
            "session_id": info.get("session_id"),
            "thread_id": info.get("thread_id"),
            "turn_id": info.get("turn_id"),
            "request_evidence": info.get("request_evidence"),
            "request_pairing": request_pairing,
        })
        ctx.log.info(f"Codex model: {item['model'] or 'unknown'} ({transport}; {item['evidence']})")


addons = [ModelProbe()]
