"""HTTP client adapter for an externally hosted cross-encoder reranker."""

from __future__ import annotations

import logging
import math
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class RemoteCrossEncoder:
    """HTTP adapter compatible with ``HuggingFaceCrossEncoder.score``.

    The remote service returns raw cross-encoder scores keyed by the temporary
    document IDs sent in the request. On a transient remote failure, fail-open
    mode emits strictly descending scores so the caller preserves the incoming
    candidate order (including through the temporal tie-breaker).
    """

    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        timeout: float = 30.0,
        fail_open: bool = True,
        max_documents: int = 64,
        model_name: str = "BAAI/bge-reranker-v2-m3",
    ):
        if not base_url.strip():
            raise ValueError("Remote reranker base_url must not be empty")
        if max_documents < 1:
            raise ValueError("Remote reranker max_documents must be at least 1")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.fail_open = fail_open
        self.max_documents = max_documents
        self.model_name = f"remote:{model_name}"

    @staticmethod
    def _rank_preserving_scores(count: int) -> list[float]:
        return [float(count - index) for index in range(count)]

    def score(self, sentence_pairs: list[tuple[str, str]]) -> list[float]:
        if not sentence_pairs:
            return []

        try:
            queries = {str(query) for query, _ in sentence_pairs}
            if len(queries) != 1:
                raise ValueError("Remote reranker requires one shared query per batch")
            if len(sentence_pairs) > self.max_documents:
                raise ValueError(
                    f"Remote reranker batch has {len(sentence_pairs)} documents; "
                    f"maximum is {self.max_documents}"
                )

            query = str(sentence_pairs[0][0])
            documents = [
                {"id": str(index), "text": str(document)}
                for index, (_, document) in enumerate(sentence_pairs)
            ]
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/rerank",
                    headers=headers,
                    json={"query": query, "documents": documents},
                )
                response.raise_for_status()
                payload: dict[str, Any] = response.json()

            raw_scores = payload.get("scores")
            if not isinstance(raw_scores, list):
                raise ValueError("Remote reranker response is missing a scores list")
            scores_by_id: dict[str, float] = {}
            for item in raw_scores:
                if not isinstance(item, dict) or "id" not in item or "score" not in item:
                    raise ValueError("Remote reranker returned a malformed score item")
                item_id = str(item["id"])
                if item_id in scores_by_id:
                    raise ValueError(f"Remote reranker returned duplicate id={item_id}")
                if isinstance(item["score"], bool):
                    raise ValueError("Remote reranker score must be numeric, not boolean")
                value = float(item["score"])
                if not math.isfinite(value):
                    raise ValueError("Remote reranker returned a non-finite score")
                scores_by_id[item_id] = value

            expected_ids = {document["id"] for document in documents}
            if set(scores_by_id) != expected_ids:
                raise ValueError("Remote reranker response IDs do not match the request")
            return [scores_by_id[str(index)] for index in range(len(documents))]
        except Exception as exc:
            if not self.fail_open:
                raise
            logger.warning(
                "Remote reranker unavailable (%s); preserving incoming candidate order.",
                exc,
            )
            return self._rank_preserving_scores(len(sentence_pairs))
