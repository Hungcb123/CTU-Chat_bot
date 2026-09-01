import os
import unittest
from pathlib import Path
from unittest.mock import patch
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

from app.services import rag_engine


AdvancedChunkingEngine = rag_engine.AdvancedChunkingEngine


class RagEngineFilterTests(unittest.TestCase):
    def test_openrouter_cross_encoder_defaults(self):
        """OpenRouterCrossEncoder uses correct default model."""
        encoder = rag_engine.OpenRouterCrossEncoder(api_key="test-key")
        self.assertEqual(encoder.model_name, "nvidia/llama-nemotron-rerank-v1:free")
        self.assertEqual(encoder.api_key, "test-key")

    def test_openrouter_cross_encoder_returns_default_scores_without_key(self):
        """Without API key, score() returns default scores instead of crashing."""
        encoder = rag_engine.OpenRouterCrossEncoder(api_key="")
        scores = encoder.score([("query", "doc1"), ("query", "doc2")])
        self.assertEqual(len(scores), 2)
        self.assertTrue(all(s == 0.0 for s in scores))

    def test_social_support_lane_filters_social_support_domain(self):
        qdrant_filter = AdvancedChunkingEngine.build_filter(
            lane="social_support",
            metadata_filter_enabled=True,
        )

        conditions = {
            condition.key: condition.match.value
            for condition in qdrant_filter.must
        }
        self.assertEqual(conditions["metadata.status"], "active")
        self.assertEqual(conditions["metadata.domain"], "social_support")


if __name__ == "__main__":
    unittest.main()
