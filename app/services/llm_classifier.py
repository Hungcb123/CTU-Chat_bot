"""LLM-based intent classifier with rule-base fallback.

Replaces the deterministic keyword router with a Gemini Flash Lite call that
returns ``{lane, confidence, params}``.  When the LLM is unavailable or returns
low-confidence results the system falls back to the existing rule-base in
``query_intent._classify_one``.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.services.query_intent import (
    QueryIntent,
    QueryRoutingDecision,
    _classify_one,
    _extract_academic_year,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Valid lane names — must stay in sync with QueryIntent enum
# ---------------------------------------------------------------------------
VALID_LANES: set[str] = {
    "ACTUAL_TUITION",
    "EXEMPTION_BASIS",
    "EXEMPTION_POLICY",
    "CALCULATION",
    "BOTH",
    "SCHOLARSHIP",
    "STUDENT_LOAN",
    "SOCIAL_SUPPORT",
    "ACADEMIC_PROGRAM",
    "ACADEMIC_RULES",
    "QUY_CHE_GENERAL",
    "AMBIGUOUS_TUITION",
    "OTHER",
}

TUITION_LANES: set[str] = {
    "ACTUAL_TUITION",
    "EXEMPTION_BASIS",
    "EXEMPTION_POLICY",
    "CALCULATION",
    "BOTH",
    "AMBIGUOUS_TUITION",
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
class RouteAction(str, Enum):
    PASS = "pass"
    CLARIFY = "clarify"
    BLOCK = "block"


@dataclass(frozen=True)
class LLMClassifierResult:
    """Structured output of the LLM intent classifier."""

    lane: str  # e.g. "ACTUAL_TUITION"
    confidence: float  # 0.0 – 1.0
    params: Dict[str, Any] = field(default_factory=dict)
    source: str = "llm"  # "llm" | "rule_fallback"


# ---------------------------------------------------------------------------
# Classification prompt
# ---------------------------------------------------------------------------
_CLASSIFICATION_SYSTEM_PROMPT = """\
Bạn là bộ phân loại câu hỏi sinh viên Đại học Cần Thơ.
Phân tích câu hỏi và trả về **duy nhất** một JSON object (không giải thích thêm):

{{"lane": "<LANE_NAME>", "confidence": <0.0-1.0>, "params": {{}}}}

### Các lanes hợp lệ:

| Lane | Mô tả | Params có thể trích xuất |
|------|--------|--------------------------|
| ACTUAL_TUITION | Hỏi mức học phí thực tế phải đóng | nganh, khoa, hoc_phan, nam_hoc |
| EXEMPTION_BASIS | Hỏi mức học phí làm cơ sở tính miễn giảm | khoi_nganh, nam_hoc |
| EXEMPTION_POLICY | Hỏi chính sách, đối tượng, điều kiện miễn giảm | doi_tuong |
| CALCULATION | Yêu cầu TÍNH TOÁN số tiền (miễn giảm, phải đóng) | nganh, khoa, phan_tram_giam, nam_hoc |
| BOTH | Yêu cầu so sánh cả 2 mức học phí | nam_hoc |
| SCHOLARSHIP | Hỏi về học bổng | gpa, drl, khoi_nganh |
| STUDENT_LOAN | Hỏi về vay vốn sinh viên | |
| SOCIAL_SUPPORT | Hỏi về trợ cấp xã hội | |
| ACADEMIC_PROGRAM | Hỏi về ngành học, chương trình đào tạo, môn học, tín chỉ của ngành | ten_nganh, loai_thong_tin |
| ACADEMIC_RULES | Hỏi quy chế học vụ (đăng ký môn, rút môn, tín chỉ tối thiểu/tối đa) | |
| QUY_CHE_GENERAL | Hỏi quy định chung về đào tạo (thi, điểm, học lại, bảo lưu, thôi học) | |
| AMBIGUOUS_TUITION | Hỏi học phí nhưng không rõ loại nào | nam_hoc |
| OTHER | Không thuộc domain nào ở trên | |

### Quy tắc:
1. Nếu câu hỏi nhắc đến tên ngành, chương trình đào tạo, môn học của ngành, khung chương trình → ACADEMIC_PROGRAM.
2. Nếu câu hỏi nhắc đến quy chế đăng ký, rút môn, số tín chỉ tối thiểu/tối đa mỗi học kỳ → ACADEMIC_RULES.
3. Nếu câu hỏi nhắc đến thi, điểm, học lại, cải thiện điểm, bảo lưu, thôi học → QUY_CHE_GENERAL.
4. Nếu câu hỏi yêu cầu "tính", "tính giúp", "tính tiền", "còn đóng bao nhiêu" → CALCULATION.
5. Nếu câu hỏi nhắc đến "học phí" nhưng thiếu ngữ cảnh loại → AMBIGUOUS_TUITION.
6. confidence = 1.0 khi chắc chắn, < 0.8 khi mơ hồ.
7. Chỉ trích xuất params nếu thông tin CÓ TRONG câu hỏi, không bịa.

### Ví dụ:
- "Ngành CNTT học những gì?" → {{"lane": "ACADEMIC_PROGRAM", "confidence": 0.95, "params": {{"ten_nganh": "Công nghệ thông tin", "loai_thong_tin": "mon_hoc"}}}}
- "Học phí ngành CNTT khóa 49 bao nhiêu?" → {{"lane": "ACTUAL_TUITION", "confidence": 0.92, "params": {{"nganh": "Công nghệ thông tin", "khoa": "K49"}}}}
- "Điều kiện miễn giảm 70% cho hộ nghèo?" → {{"lane": "EXEMPTION_POLICY", "confidence": 0.95, "params": {{"doi_tuong": "hộ nghèo"}}}}
- "GPA 3.5 ĐRL 85 được học bổng gì?" → {{"lane": "SCHOLARSHIP", "confidence": 0.97, "params": {{"gpa": 3.5, "drl": 85}}}}
- "Quy chế thi cuối kỳ?" → {{"lane": "QUY_CHE_GENERAL", "confidence": 0.90, "params": {{}}}}
- "So sánh ngành CNTT và AI" → {{"lane": "ACADEMIC_PROGRAM", "confidence": 0.93, "params": {{"ten_nganh": "CNTT và AI", "loai_thong_tin": "so_sanh"}}}}
"""

_CLASSIFICATION_USER_TEMPLATE = "Câu hỏi: {query}"


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------
class LLMIntentClassifier:
    """Hybrid LLM + rule-base intent classifier.

    * **Primary path** — call Gemini Flash Lite with a structured JSON prompt.
    * **Fallback path** — if the LLM call times out, raises an exception, or
      returns an unparseable response, delegate to the deterministic
      ``_classify_one()`` function in ``query_intent.py``.
    """

    def __init__(
        self,
        llm,
        confidence_threshold: float = 0.8,
        timeout_seconds: float = 5.0,
    ) -> None:
        self.llm = llm
        self.confidence_threshold = confidence_threshold
        self.timeout_seconds = timeout_seconds
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", _CLASSIFICATION_SYSTEM_PROMPT),
                ("human", _CLASSIFICATION_USER_TEMPLATE),
            ]
        )
        self._chain = self._prompt | self.llm | StrOutputParser()

    # ---- public API -------------------------------------------------------

    async def classify_with_fallback(
        self,
        query: str,
    ) -> LLMClassifierResult:
        """Classify *query*, falling back to rules on any failure."""
        try:
            result = await asyncio.wait_for(
                self._classify_llm(query),
                timeout=self.timeout_seconds,
            )
            logger.info(
                "LLM classifier lane=%s confidence=%.2f source=%s params=%s",
                result.lane,
                result.confidence,
                result.source,
                result.params,
            )
            return result
        except asyncio.TimeoutError:
            logger.warning(
                "LLM classifier timed out after %.1fs; falling back to rules",
                self.timeout_seconds,
            )
            return self._fallback_to_rules(query)
        except Exception as exc:
            logger.warning(
                "LLM classifier error (%s: %s); falling back to rules",
                type(exc).__name__,
                exc,
            )
            return self._fallback_to_rules(query)

    def route(self, result: LLMClassifierResult) -> RouteAction:
        """Decide whether the routing decision should proceed."""
        if result.lane not in VALID_LANES:
            return RouteAction.BLOCK
        if result.confidence < self.confidence_threshold:
            return RouteAction.CLARIFY
        return RouteAction.PASS

    def to_routing_decision(
        self,
        result: LLMClassifierResult,
        original_query: str,
    ) -> QueryRoutingDecision:
        """Convert a classifier result into the legacy ``QueryRoutingDecision``."""
        academic_year = (
            result.params.get("nam_hoc")
            or _extract_academic_year(original_query)
        )

        action = self.route(result)
        if action == RouteAction.CLARIFY:
            # Low confidence → degrade gracefully
            if result.lane in TUITION_LANES:
                intent = QueryIntent.AMBIGUOUS_TUITION
            else:
                intent = QueryIntent.OTHER
        elif action == RouteAction.BLOCK:
            intent = QueryIntent.OTHER
        else:
            try:
                intent = QueryIntent(result.lane.lower())
            except ValueError:
                intent = QueryIntent.OTHER

        return QueryRoutingDecision(
            intent=intent,
            academic_year=academic_year,
            classified_from=result.source,
        )

    # ---- private helpers --------------------------------------------------

    async def _classify_llm(self, query: str) -> LLMClassifierResult:
        """Call the LLM and parse the structured JSON response."""
        raw = await self._chain.ainvoke({"query": query})
        return self._parse_llm_response(raw)

    @staticmethod
    def _parse_llm_response(raw: str) -> LLMClassifierResult:
        """Extract the first JSON object from the LLM response."""
        # Strip markdown code fences if present
        cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`")

        # Find the first JSON object
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON object found in LLM response: {raw!r}")

        data = json.loads(match.group())
        lane = str(data.get("lane", "OTHER")).upper()
        if lane not in VALID_LANES:
            lane = "OTHER"

        confidence = float(data.get("confidence", 0.0))
        confidence = max(0.0, min(1.0, confidence))

        params = data.get("params", {})
        if not isinstance(params, dict):
            params = {}

        return LLMClassifierResult(
            lane=lane,
            confidence=confidence,
            params=params,
            source="llm",
        )

    @staticmethod
    def _fallback_to_rules(query: str) -> LLMClassifierResult:
        """Wrap the deterministic ``_classify_one()`` as a fallback."""
        intent = _classify_one(query)
        return LLMClassifierResult(
            lane=intent.value.upper(),
            confidence=1.0,  # Rules are deterministic
            params={},
            source="rule_fallback",
        )
