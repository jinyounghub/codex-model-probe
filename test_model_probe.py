import base64
import json
import tempfile
import unittest
from pathlib import Path

from model_probe import analyze_body, analyze_file, request_metadata


class ModelProbeTests(unittest.TestCase):
    def test_request_model_and_session_come_from_client_payload(self):
        message = {"type": "response.create", "model": "requested", "client_metadata": {
            "session_id": "session-123", "thread_id": "thread-123", "turn_id": "turn-123"
        }}
        self.assertEqual(request_metadata(message, websocket=True), {
            "requested_model": "requested", "session_id": "session-123",
            "thread_id": "thread-123", "turn_id": "turn-123",
            "request_evidence": "response.create.model",
        })
        self.assertIsNone(request_metadata({"type": "session_meta", "model": "other"}, websocket=True))
        self.assertIsNone(request_metadata({"type": "response.create", "model": None}, websocket=True))

    def test_sse_uses_only_final_server_payload(self):
        body = "\n\n".join([
            'data: {"type":"response.created","response":{"model":"requested-model"}}',
            'event: response.completed\ndata: {"response":{"id":"resp_1","model":"served-model"}}',
        ]) + "\n\n"
        self.assertEqual(analyze_body(body), [{
            "model": "served-model", "response_id": "resp_1",
            "evidence": "response.completed.response.model",
        }])

    def test_request_and_session_model_are_ignored(self):
        body = '\n'.join([
            '{"type":"session_meta","payload":{"model":"session-model"}}',
            '{"type":"turn_context","payload":{"model":"configured-model"}}',
            '{"type":"response.created","response":{"model":"initial-model"}}',
        ])
        self.assertEqual(analyze_body(body), [])

    def test_missing_final_model_is_unknown(self):
        self.assertEqual(analyze_body('{"type":"response.completed","response":{"id":"r"}}'), [{
            "model": None, "response_id": "r",
            "evidence": "response.completed.response.model",
        }])

    def test_non_streaming_completed_response(self):
        self.assertEqual(analyze_body('{"object":"response","status":"completed","id":"r","model":"m"}')[0]["model"], "m")

    def test_har_reads_response_body_only(self):
        response = '{"type":"response.completed","response":{"model":"served"}}'
        har = {"log": {"entries": [{
            "request": {"postData": {"text": '{"model":"requested"}'}},
            "response": {"content": {"encoding": "base64", "text": base64.b64encode(response.encode()).decode()}},
        }]}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capture.har"
            path.write_text(json.dumps(har), encoding="utf-8")
            self.assertEqual(analyze_file(path)[0]["model"], "served")


if __name__ == "__main__":
    unittest.main()
