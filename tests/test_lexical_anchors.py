"""Tests for lexical anchor detection."""

import unittest

from app.services.lexical_anchors import LexicalAnchors, detect_lexical_anchors


class LexicalAnchorTests(unittest.TestCase):
    """Pattern detection and BM25 boost logic."""

    def test_program_code_detected(self):
        """7-digit program code triggers anchor."""
        anchors = detect_lexical_anchors("Ngành 7480201 có bao nhiêu tín chỉ?")
        self.assertEqual(anchors.program_codes, ("7480201",))
        self.assertTrue(anchors.has_anchor)
        self.assertEqual(anchors.bm25_boost, 1.5)

    def test_course_code_detected(self):
        """2-letter + 3-digit course code triggers anchor."""
        anchors = detect_lexical_anchors("Môn tiên quyết của CT101 là gì?")
        self.assertEqual(anchors.course_codes, ("CT101",))
        self.assertTrue(anchors.has_anchor)

    def test_course_code_with_suffix(self):
        """Course code with letter suffix (e.g. XH001A)."""
        anchors = detect_lexical_anchors("Thông tin môn XH001A")
        self.assertIn("XH001A", anchors.course_codes)

    def test_cohort_detected(self):
        """K + 2-digit cohort triggers anchor."""
        anchors = detect_lexical_anchors("Học phí K52 ngành CNTT?")
        self.assertEqual(anchors.cohorts, ("K52",))
        self.assertTrue(anchors.has_anchor)

    def test_cohort_with_space(self):
        """K 52 (with space) also detected."""
        anchors = detect_lexical_anchors("Học phí K 52?")
        self.assertEqual(anchors.cohorts, ("K52",))

    def test_training_system_clc(self):
        """CLC detected as training system."""
        anchors = detect_lexical_anchors("Học phí CLC bao nhiêu?")
        self.assertIn("CLC", anchors.training_systems)
        self.assertTrue(anchors.has_anchor)

    def test_training_system_vlvh(self):
        """VLVH detected as training system."""
        anchors = detect_lexical_anchors("Mức học phí VLVH ngành Luật?")
        self.assertIn("VLVH", anchors.training_systems)

    def test_training_system_vietnamese(self):
        """Vietnamese phrase 'chất lượng cao' detected."""
        anchors = detect_lexical_anchors("Học phí chương trình chất lượng cao?")
        self.assertIn("CLC", anchors.training_systems)

    def test_training_system_dai_tra(self):
        """'đại trà' detected as training system."""
        anchors = detect_lexical_anchors("Học phí đại trà K52?")
        self.assertIn("đại trà", anchors.training_systems)

    def test_no_anchor_returns_boost_1(self):
        """No anchor → bm25_boost = 1.0."""
        anchors = detect_lexical_anchors("Học phí trường mình bao nhiêu?")
        self.assertFalse(anchors.has_anchor)
        self.assertEqual(anchors.bm25_boost, 1.0)

    def test_multiple_anchors(self):
        """Multiple anchors in one query."""
        anchors = detect_lexical_anchors("So sánh CT101 và CT102 cho K52 CLC")
        self.assertEqual(len(anchors.course_codes), 2)
        self.assertEqual(anchors.cohorts, ("K52",))
        self.assertIn("CLC", anchors.training_systems)
        self.assertEqual(anchors.bm25_boost, 1.5)

    def test_no_false_positive_on_short_numbers(self):
        """Short numbers like '70%' should NOT match program code."""
        anchors = detect_lexical_anchors("Giảm 70% học phí")
        self.assertEqual(anchors.program_codes, ())

    def test_dedup_training_systems(self):
        """Same canonical system not duplicated."""
        anchors = detect_lexical_anchors("CLC hay chất lượng cao?")
        clc_count = anchors.training_systems.count("CLC")
        self.assertEqual(clc_count, 1)

    def test_scholarship_vallet_detected(self):
        """Vallet scholarship entity triggers anchor and boost."""
        anchors = detect_lexical_anchors("Học bổng Vallet năm 2026 có bao nhiêu suất?")
        self.assertIn("Vallet", anchors.scholarships)
        self.assertTrue(anchors.has_anchor)
        self.assertEqual(anchors.bm25_boost, 1.5)

    def test_scholarship_scic_detected(self):
        """SCIC scholarship entity triggers anchor."""
        anchors = detect_lexical_anchors("Điều kiện nộp học bổng SCIC?")
        self.assertIn("SCIC", anchors.scholarships)
        self.assertTrue(anchors.has_anchor)


if __name__ == "__main__":
    unittest.main()
