import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from mitmproxy import ctx
from mitmproxy.websocket import WebSocketMessage
from wsproto.frame_protocol import Opcode

from capture import ModelProbe


class WebSocketCaptureTests(unittest.TestCase):
    def setUp(self):
        self.probe = ModelProbe()
        self.records = []
        self.probe._write = self.records.append
        self.probe._allowed_host = lambda _flow: True
        self.flow = SimpleNamespace(
            id="flow-1",
            request=SimpleNamespace(host="chatgpt.com"),
            websocket=SimpleNamespace(messages=[]),
        )

    def send(self, payload, *, from_client=False):
        self.flow.websocket.messages.append(WebSocketMessage(
            Opcode.TEXT, from_client, json.dumps(payload).encode("utf-8")
        ))
        with patch.object(ctx, "log", SimpleNamespace(info=lambda _message: None), create=True):
            self.probe.websocket_message(self.flow)

    def test_only_completed_server_websocket_model_is_reported(self):
        self.send({"model": "requested", "type": "response.create", "client_metadata": {
            "session_id": "session-1", "thread_id": "thread-1", "turn_id": "turn-1"
        }}, from_client=True)
        self.send({"type": "response.created", "response": {"id": "r1", "model": "initial"}})
        self.send({"type": "response.completed", "response": {"id": "r1", "model": "served"}})
        models = [item for item in self.records if item["kind"] == "model"]
        self.assertEqual([(item["model"], item["response_id"], item["transport"]) for item in models],
                         [("served", "r1", "websocket")])
        self.assertEqual(models[0]["requested_model"], "requested")
        self.assertEqual(models[0]["session_id"], "session-1")
        self.assertEqual(models[0]["thread_id"], "thread-1")
        self.assertEqual(models[0]["turn_id"], "turn-1")
        self.assertEqual(models[0]["request_pairing"], "response.created.id")
        self.assertEqual(sum(item["kind"] == "response_seen" for item in self.records), 2)

    def test_multiple_requests_are_paired_with_their_response_ids(self):
        for model, session in (("want-a", "session-a"), ("want-b", "session-b")):
            self.send({"type": "response.create", "model": model,
                       "client_metadata": {"session_id": session}}, from_client=True)
        self.send({"type": "response.created", "response": {"id": "r-a"}})
        self.send({"type": "response.created", "response": {"id": "r-b"}})
        self.send({"type": "response.completed", "response": {"id": "r-b", "model": "actual-b"}})
        self.send({"type": "response.completed", "response": {"id": "r-a", "model": "actual-a"}})
        models = [item for item in self.records if item["kind"] == "model"]
        self.assertEqual([(item["response_id"], item["requested_model"], item["session_id"])
                          for item in models], [("r-b", "want-b", "session-b"),
                                               ("r-a", "want-a", "session-a")])

    def test_unpaired_final_is_left_unidentified(self):
        self.send({"type": "response.completed", "response": {"id": "r-other", "model": "actual"}})
        model = next(item for item in self.records if item["kind"] == "model")
        self.assertIsNone(model["requested_model"])
        self.assertIsNone(model["session_id"])

    def test_websocket_handshake_is_not_counted_as_server_message(self):
        self.flow.response = SimpleNamespace(status_code=101)
        self.probe.responseheaders(self.flow)
        self.assertEqual(self.records, [])


if __name__ == "__main__":
    unittest.main()
