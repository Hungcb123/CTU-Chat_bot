import os
import unittest
from unittest.mock import patch

from app.services import rag_engine


AdvancedChunkingEngine = rag_engine.AdvancedChunkingEngine


class RagEngineFilterTests(unittest.TestCase):
    def test_reranker_config_defaults_to_bge_and_supports_gte_override(self):
        config = getattr(rag_engine, "_reranker_model_config", None)
        self.assertTrue(callable(config))

        with patch.dict(os.environ, {}, clear=True):
            model_name, model_kwargs = config()
        self.assertEqual(model_name, "BAAI/bge-reranker-v2-m3")
        self.assertEqual(model_kwargs["device"], "cuda")
        self.assertNotIn("trust_remote_code", model_kwargs)

        with patch.dict(
            os.environ,
            {
                "RAG_RERANKER_MODEL": "Alibaba-NLP/gte-multilingual-reranker-base",
                "RAG_RERANKER_DEVICE": "cpu",
            },
            clear=True,
        ):
            model_name, model_kwargs = config()
        self.assertEqual(model_name, "Alibaba-NLP/gte-multilingual-reranker-base")
        self.assertEqual(model_kwargs, {"device": "cpu", "trust_remote_code": True})

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
