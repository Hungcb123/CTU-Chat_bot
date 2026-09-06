"""Regression tests for Graph queries used by the Table 5 experiment."""

import unittest

from app.services.graph_service import AcademicGraphService


class _FakeSession:
    def __init__(self):
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def run(self, query, **parameters):
        self.calls.append((query, parameters))
        return []


class _FakeDriver:
    def __init__(self):
        self.session_instance = _FakeSession()

    def session(self):
        return self.session_instance


class GraphServiceTests(unittest.TestCase):
    def test_t5_t6_exemption_lookup_does_not_reuse_session_query_argument(self):
        """T5/T6: Cypher parameters must not collide with Session.run(query)."""
        service = AcademicGraphService.__new__(AcademicGraphService)
        service._driver = _FakeDriver()

        service.lookup_exemption_basis(query="7480201")

        cypher, parameters = service._driver.session_instance.calls[0]
        self.assertIn("$query_text", cypher)
        self.assertEqual(parameters["query_text"], "7480201")


if __name__ == "__main__":
    unittest.main()
