"""Regression tests for the fixed-evidence T7 graph path."""

import unittest

from langchain_core.prompts import ChatPromptTemplate

from app.agents.graph import _escape_prompt_literal


class GraphAgentTests(unittest.TestCase):
    def test_t7_json_evidence_is_literal_prompt_text(self):
        """T7: JSON braces from T6 evidence must not become template variables."""
        system_prompt = 'Evidence: {"don_vi": "dong/tin_chi"}'
        prompt = ChatPromptTemplate.from_messages([
            ("system", _escape_prompt_literal(system_prompt)),
            ("human", "{question}"),
        ])

        messages = prompt.invoke({"question": "Học phí bao nhiêu?"}).to_messages()

        self.assertIn('{"don_vi": "dong/tin_chi"}', messages[0].content)


if __name__ == "__main__":
    unittest.main()
