#!/usr/bin/env python3
"""Read a captured server response and report only final-payload model evidence."""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path
from typing import Any, Iterator


def request_metadata(message: Any, *, websocket: bool = False) -> dict[str, str | None] | None:
    """Read only model and session identifiers from an outgoing response request."""
    if not isinstance(message, dict):
        return None
    if websocket and message.get("type") != "response.create":
        return None
    model = message.get("model")
    if not isinstance(model, str) or not model or len(model) > 256:
        return None
    client = message.get("client_metadata")
    if not isinstance(client, dict):
        client = {}

    def identifier(name: str) -> str | None:
        value = client.get(name)
        return value if isinstance(value, str) and 0 < len(value) <= 128 else None

    return {
        "requested_model": model,
        "session_id": identifier("session_id"),
        "thread_id": identifier("thread_id"),
        "turn_id": identifier("turn_id"),
        "request_evidence": "response.create.model" if websocket else "request.model",
    }


def _final_model(message: Any, event_name: str | None = None) -> dict[str, str | None] | None:
    if not isinstance(message, dict):
        return None

    kind = message.get("type") or event_name
    if kind == "response.completed":
        response = message.get("response")
        if not isinstance(response, dict):
            return {"model": None, "response_id": None,
                    "evidence": "response.completed.response.model (missing)"}
        model = response.get("model")
        return {
            "model": model if isinstance(model, str) and model else None,
            "response_id": response.get("id") if isinstance(response.get("id"), str) else None,
            "evidence": "response.completed.response.model",
        }

    # A non-streaming Responses API reply is itself the final response object.
    if message.get("object") == "response" and message.get("status") == "completed":
        model = message.get("model")
        return {
            "model": model if isinstance(model, str) and model else None,
            "response_id": message.get("id") if isinstance(message.get("id"), str) else None,
            "evidence": "completed response.model",
        }
    return None


def _sse_messages(text: str) -> Iterator[tuple[dict[str, Any], str | None]]:
    event_name: str | None = None
    data: list[str] = []
    for line in (text + "\n\n").splitlines():
        if not line:
            if data:
                try:
                    value = json.loads("\n".join(data))
                except json.JSONDecodeError:
                    value = None
                if isinstance(value, dict):
                    yield value, event_name
            event_name, data = None, []
        elif line.startswith("event:"):
            event_name = line[6:].strip()
        elif line.startswith("data:"):
            data.append(line[5:].lstrip())


def analyze_body(body: str) -> list[dict[str, str | None]]:
    """Accept JSON, JSONL or SSE response bodies. Ignore request/session metadata."""
    results: list[dict[str, str | None]] = []
    try:
        value = json.loads(body)
    except json.JSONDecodeError:
        value = None
    if isinstance(value, dict):
        item = _final_model(value)
        if item:
            return [item]
        # Some capture tools wrap a server event in a `data` field.
        data = value.get("data")
        if isinstance(data, dict):
            item = _final_model(data, value.get("event"))
            if item:
                return [item]
        return []

    if "data:" in body:
        for value, event_name in _sse_messages(body):
            item = _final_model(value, event_name)
            if item:
                results.append(item)
        return results

    for line in body.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = _final_model(value)
        if item:
            results.append(item)
    return results


def analyze_file(path: Path) -> list[dict[str, str | None]]:
    raw = path.read_text(encoding="utf-8-sig")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        value = None

    if isinstance(value, dict) and isinstance(value.get("log"), dict):
        results: list[dict[str, str | None]] = []
        for index, entry in enumerate(value["log"].get("entries", []), start=1):
            if not isinstance(entry, dict):
                continue
            content = entry.get("response", {}).get("content", {})
            if not isinstance(content, dict) or not isinstance(content.get("text"), str):
                continue
            body = content["text"]
            if content.get("encoding") == "base64":
                try:
                    body = base64.b64decode(body, validate=True).decode("utf-8")
                except (ValueError, UnicodeDecodeError):
                    continue
            for item in analyze_body(body):
                results.append({**item, "location": f"HAR response #{index}"})
        return results

    results = analyze_body(raw)
    if results:
        return [{**item, "location": "response body"} for item in results]

    # A capture can be JSONL where each line contains a response body string.
    for line_number, line in enumerate(raw.splitlines(), start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        body = record.get("response_body")
        if isinstance(body, str):
            for item in analyze_body(body):
                results.append({**item, "location": f"line {line_number} response_body"})
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Codex 서버 최종 응답의 모델 필드 검사")
    parser.add_argument("capture", type=Path, help="서버 응답 본문(SSE/JSON/JSONL) 또는 HAR 파일")
    parser.add_argument("--json", action="store_true", help="기계 판독용 JSON 출력")
    args = parser.parse_args()
    try:
        results = analyze_file(args.capture)
    except (OSError, UnicodeError) as exc:
        print(f"파일을 읽을 수 없습니다: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif results:
        for item in results:
            model = item["model"] or "확인 불가 (최종 응답에 모델 필드 없음)"
            print(f"{model} | {item['evidence']} | {item['response_id'] or '-'} | {item['location']}")
    else:
        print("확인 불가: 캡처에서 서버의 최종 응답 페이로드를 찾지 못했습니다.")
    return 0 if results and all(item["model"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
