import unittest
from unittest.mock import patch

from app.services.orchestration_contract import (
    owner_for_intent,
    repair_route_decision,
    tool_gate_prompt,
)


class OrchestrationContractTests(unittest.TestCase):
    def test_owner_mapping(self):
        self.assertEqual(owner_for_intent("scholarship"), "scholarship")
        self.assertEqual(owner_for_intent("student_loan"), "general")

    def test_repairs_strong_cross_domain_signal(self):
        result = repair_route_decision(
            "Em muốn vay tiền đóng học phí theo NHCSXH",
            "financial",
            "actual_tuition",
        )
        self.assertTrue(result.repaired)
        self.assertEqual(result.agent, "general")
        self.assertEqual(result.intent.value, "student_loan")

    def test_repairs_invalid_agent_intent_pair(self):
        result = repair_route_decision("Điều kiện Vallet?", "general", "scholarship")
        self.assertEqual(result.agent, "scholarship")

    def test_feature_flag_disables_repair(self):
        with patch.dict("os.environ", {"ROUTING_REPAIR_ENABLED": "false"}):
            result = repair_route_decision("Điều kiện Vallet?", "general", "scholarship")
        self.assertFalse(result.repaired)
        self.assertEqual(result.agent, "general")

    def test_specialist_prompt_is_scoped(self):
        prompt = tool_gate_prompt("scholarship")
        self.assertIn("tinh_tien_hoc_bong", prompt)
        self.assertNotIn("tra_cuu_nganh", prompt)


if __name__ == "__main__":
    unittest.main()
