#!/usr/bin/env python3
"""Check a remote reranker endpoint with a small Vietnamese ranking example."""

from __future__ import annotations

import argparse
import json
import os

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-test the remote reranker HTTP API")
    parser.add_argument("--url", default=os.getenv("RAG_REMOTE_RERANKER_URL", ""))
    parser.add_argument("--api-key", default=os.getenv("RAG_REMOTE_RERANKER_API_KEY", ""))
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()
    if not args.url:
        parser.error("Provide --url or RAG_REMOTE_RERANKER_URL")

    headers = {"Authorization": f"Bearer {args.api_key}"} if args.api_key else {}
    base_url = args.url.rstrip("/")
    with httpx.Client(timeout=args.timeout) as client:
        health = client.get(f"{base_url}/health", headers=headers)
        health.raise_for_status()
        response = client.post(
            f"{base_url}/rerank",
            headers=headers,
            json={
                "query": "Lệ phí xin cấp bản sao văn bằng tốt nghiệp là bao nhiêu?",
                "documents": [
                    {"id": "diploma", "text": "Phiếu đề nghị cấp bản sao văn bằng. Lệ phí cấp một bản sao là 10.000 đồng."},
                    {"id": "tuition", "text": "Bảng mức thu học phí chương trình đại học chính quy khóa 52."},
                ],
            },
        )
        response.raise_for_status()

    result = response.json()
    scores = {str(item["id"]): float(item["score"]) for item in result["scores"]}
    print(json.dumps({"health": health.json(), "rerank": result}, ensure_ascii=False, indent=2))
    if scores.get("diploma", float("-inf")) <= scores.get("tuition", float("inf")):
        raise SystemExit("FAIL: diploma evidence was not ranked above tuition evidence")
    print("PASS: remote reranker ranked the relevant diploma evidence first")


if __name__ == "__main__":
    main()
