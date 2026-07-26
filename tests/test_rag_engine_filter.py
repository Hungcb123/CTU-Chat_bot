import unittest

from app.services.rag_engine import AdvancedChunkingEngine


class RagEngineFilterTests(unittest.TestCase):
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
