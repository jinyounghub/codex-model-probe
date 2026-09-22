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
        metadata = request_metadata(message, websocket=True)
        self.assertEqual(metadata["requested_model"], "requested")
        self.assertEqual(metadata["session_id"], "session-123")
        self.assertEqual(metadata["thread_id"], "thread-123")
        self.assertEqual(metadata["turn_id"], "turn-123")
        self.assertEqual(metadata["request_evidence"], "response.create.model")
        self.assertIsNone(request_metadata({"type": "session_meta", "model": "other"}, websocket=True))
        self.assertIsNone(request_metadata({"type": "response.create", "model": None}, websocket=True))

    def test_sse_uses_only_final_server_payload(self):
        body = "\n\n".join([
            'data: {"type":"response.created","response":{"model":"requested-model"}}',
            'event: response.completed\ndata: {"response":{"id":"resp_1","model":"served-model"}}',
        ]) + "\n\n"
        self.assertEqual(len(analyze_body(body)), 1)
        self.assertEqual(analyze_body(body)[0]["model"], "served-model")
        self.assertEqual(analyze_body(body)[0]["response_id"], "resp_1")

    def test_request_and_session_model_are_ignored(self):
        body = '\n'.join([
            '{"type":"session_meta","payload":{"model":"session-model"}}',
            '{"type":"turn_context","payload":{"model":"configured-model"}}',
            '{"type":"response.created","response":{"model":"initial-model"}}',
        ])
        self.assertEqual(analyze_body(body), [])

    def test_missing_final_model_is_unknown(self):
        result = analyze_body('{"type":"response.completed","response":{"id":"r"}}')[0]
        self.assertIsNone(result["model"])
        self.assertEqual(result["response_id"], "r")

    def test_actual_request_and_completed_response_reasoning_fields(self):
        request = {"type": "response.create", "model": "gpt-6-astra",
                   "reasoning": {"effort": "xhigh", "context": "all_turns"}}
        metadata = request_metadata(request, websocket=True)
        self.assertEqual(metadata["request_reasoning_effort"], "xhigh")
        self.assertEqual(metadata["request_reasoning_context"], "all_turns")
        response = {"type": "response.completed", "response": {
            "id": "resp_1", "model": "gpt-6-astra",
            "reasoning": {"effort": "xhigh", "mode": "standard", "context": "all_turns"},
            "usage": {"output_tokens_details": {"reasoning_tokens": 0}},
        }}
        result = analyze_body(json.dumps(response))[0]
        self.assertEqual(result["response_reasoning_effort"], "xhigh")
        self.assertEqual(result["response_reasoning_mode"], "standard")
        self.assertEqual(result["response_reasoning_context"], "all_turns")
        self.assertEqual(result["reasoning_tokens"], 0)

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
