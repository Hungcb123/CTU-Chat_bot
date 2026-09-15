import unittest
from unittest.mock import patch

from app.services.remote_reranker import RemoteCrossEncoder


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _FakeClient:
    payload = None
    request = None

    def __init__(self, timeout):
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return None

    def post(self, url, headers, json):
        type(self).request = {"url": url, "headers": headers, "json": json}
        return _FakeResponse(type(self).payload)


class RemoteCrossEncoderTests(unittest.TestCase):
    def test_aligns_scores_by_document_id(self):
        _FakeClient.payload = {
            "scores": [
                {"id": "1", "score": 0.25},
                {"id": "0", "score": 0.9},
            ]
        }
        with patch("app.services.remote_reranker.httpx.Client", _FakeClient):
            model = RemoteCrossEncoder(
                "https://reranker.example", api_key="secret", fail_open=False
            )
            scores = model.score([("query", "first"), ("query", "second")])

        self.assertEqual(scores, [0.9, 0.25])
        self.assertEqual(_FakeClient.request["url"], "https://reranker.example/rerank")
        self.assertEqual(_FakeClient.request["headers"]["Authorization"], "Bearer secret")
        self.assertEqual(
            _FakeClient.request["json"]["documents"][0], {"id": "0", "text": "first"}
        )

    def test_fail_open_preserves_input_order(self):
        class BrokenClient(_FakeClient):
            def post(self, url, headers, json):
                raise RuntimeError("offline")

        with patch("app.services.remote_reranker.httpx.Client", BrokenClient):
            model = RemoteCrossEncoder("https://reranker.example", fail_open=True)
            scores = model.score([
                ("query", "a"), ("query", "b"), ("query", "c")
            ])

        self.assertEqual(scores, [3.0, 2.0, 1.0])

    def test_fail_closed_raises(self):
        class BrokenClient(_FakeClient):
            def post(self, url, headers, json):
                raise RuntimeError("offline")

        with patch("app.services.remote_reranker.httpx.Client", BrokenClient):
            model = RemoteCrossEncoder("https://reranker.example", fail_open=False)
            with self.assertRaisesRegex(RuntimeError, "offline"):
                model.score([("query", "document")])

    def test_rejects_mismatched_response_ids(self):
        _FakeClient.payload = {"scores": [{"id": "missing", "score": 1.0}]}
        with patch("app.services.remote_reranker.httpx.Client", _FakeClient):
            model = RemoteCrossEncoder("https://reranker.example", fail_open=False)
            with self.assertRaisesRegex(ValueError, "IDs do not match"):
                model.score([("query", "document")])


if __name__ == "__main__":
    unittest.main()
