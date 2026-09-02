"""Tuition graph lookup tools for the CTU Chatbot.

Provides two LangChain tools backed by Neo4j Graph:

* ``tra_cuu_hoc_phi_graph``    — look up tuition fees by program + cohort (graph-first, JSON fallback).
* ``tra_cuu_quy_dinh_hoc_phi`` — look up tuition policies (hệ số, VLVH, thạc sĩ...).

Both tools delegate to ``AcademicGraphService.lookup_tuition()``
and ``AcademicGraphService.get_tuition_policies()`` respectively.
"""

from __future__ import annotations

import logging
from typing import Optional

from langchain.tools import tool

from app.services.graph_service import AcademicGraphService
from app.services.tuition_catalog import TuitionRateCatalog

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level references — set by app startup (main.py)
# ---------------------------------------------------------------------------
_graph_service: Optional[AcademicGraphService] = None
_tuition_catalog: Optional[TuitionRateCatalog] = None


def set_tuition_graph_service(service: AcademicGraphService) -> None:
    """Called once during app startup to inject the shared graph service."""
    global _graph_service
    _graph_service = service


def set_tuition_catalog(catalog: TuitionRateCatalog) -> None:
    """Called once during app startup to inject the JSON fallback catalog."""
    global _tuition_catalog
    _tuition_catalog = catalog


def _get_graph_service() -> AcademicGraphService:
    if _graph_service is None:
        raise RuntimeError(
            "AcademicGraphService chưa được khởi tạo. "
            "Hãy gọi set_tuition_graph_service() trước khi dùng tools."
        )
    return _graph_service


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

RATE_UNIT_LABELS = {
    "dong/tin_chi": "đồng/tín chỉ",
    "trieu_dong/nam_hoc": "triệu đồng/năm học",
    "trieu_dong/khoa": "triệu đồng/toàn khóa",
    "dong/nam_hoc": "đồng/năm học",
}


def _format_graph_results(results: list[dict]) -> str:
    """Format graph lookup results into a readable string."""
    if not results:
        return ""

    lines = ["[KẾT QUẢ TRA CỨU HỌC PHÍ TỪ GRAPH - NGUỒN ƯU TIÊN]"]

    # Group by (ten_nganh, loai_ct)
    groups: dict[tuple, list] = {}
    for r in results:
        key = (
            r.get("ten_nganh") or r.get("program_name", ""),
            r.get("loai_ct", ""),
        )
        groups.setdefault(key, []).append(r)

    for (ten_nganh, loai_ct), items in groups.items():
        loai_label = {
            "chuan": "Đại trà/chuẩn",
            "clc": "Chất lượng cao (CLC)",
            "tien_tien": "Tiên tiến",
            "clc_tt": "CLC/TT (đại cương chung)",
        }.get(loai_ct, loai_ct)

        lines.append(f"\nNgành: {ten_nganh}")
        lines.append(f"Chương trình: {loai_label}")

        for item in sorted(items, key=lambda x: (x.get("khoa", ""), x.get("don_vi_tinh", ""))):
            khoa = item.get("khoa", "")
            muc_hp = item.get("muc_hp", 0)
            don_vi = item.get("don_vi_tinh", "")
            don_vi_label = RATE_UNIT_LABELS.get(don_vi, don_vi)

            if don_vi in ("trieu_dong/nam_hoc", "trieu_dong/khoa"):
                formatted = f"{muc_hp} {don_vi_label}"
            else:
                formatted = f"{int(muc_hp):,} {don_vi_label}".replace(",", ".")

            lines.append(f"- Khóa {khoa}: {formatted}")

    lines.append(f"\nNăm học: 2026-2027")
    lines.append("Phải dùng các con số trên; không thay bằng kết quả vector search khác.")
    return "\n".join(lines)


def _format_policy_results(results: list[dict]) -> str:
    """Format policy lookup results into a readable string."""
    if not results:
        return "Không tìm thấy quy định học phí phù hợp."

    lines = ["[KẾT QUẢ TRA CỨU QUY ĐỊNH HỌC PHÍ TỪ GRAPH]"]

    for r in results:
        mo_ta = r.get("mo_ta", "")
        he_so = r.get("he_so")
        muc_hp = r.get("muc_hp")
        don_vi = r.get("don_vi_tinh", "")
        doi_tuong = r.get("doi_tuong", "")

        if he_so is not None:
            value_str = f"hệ số {he_so}"
        elif muc_hp is not None:
            don_vi_label = RATE_UNIT_LABELS.get(don_vi, don_vi)
            value_str = f"{int(muc_hp):,} {don_vi_label}".replace(",", ".")
        else:
            value_str = "(xem mô tả)"

        lines.append(f"- {mo_ta}")
        lines.append(f"  Giá trị: {value_str}")
        lines.append(f"  Đối tượng: {doi_tuong}")

    lines.append("\nNăm học: 2026-2027")
    lines.append("Nguồn: Văn bản 423/ĐHCT-KHTC ngày 03/02/2026")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@tool
def tra_cuu_hoc_phi_graph(ten_nganh: str, khoa: str = "") -> str:
    """Tra cứu chính xác học phí thực tế theo tên ngành và khóa tuyển sinh từ Neo4j graph.

    Đầu vào:
    - ten_nganh: Tên ngành hoặc mã ngành cần tra cứu (Ví dụ: "Công nghệ thông tin", "7480201", "CNTT")
    - khoa: Khóa tuyển sinh (Ví dụ: "K52", "K51_ve_truoc"). Để trống nếu muốn xem tất cả khóa.

    Trả về mức học phí thực tế, đơn vị tính, loại chương trình.
    """
    service = _get_graph_service()

    # Normalize khoa input
    khoa_clean = khoa.strip() if khoa else None

    try:
        results = service.lookup_tuition(ten_nganh, khoa_clean)
    except Exception as e:
        logger.error("Graph lookup_tuition lỗi: %s", e)
        results = []

    if results:
        formatted = _format_graph_results(results)
        logger.info(
            "tra_cuu_hoc_phi_graph: found %d results from graph for '%s' khoa=%s",
            len(results), ten_nganh, khoa_clean,
        )
        return formatted

    # Fallback: JSON TuitionRateCatalog
    logger.info(
        "tra_cuu_hoc_phi_graph: graph empty, falling back to JSON for '%s'",
        ten_nganh,
    )
    if _tuition_catalog is not None:
        query_str = ten_nganh
        if khoa_clean:
            query_str += f" {khoa_clean}"
        fallback = _tuition_catalog.lookup(query_str)
        if fallback.status == "found":
            return fallback.message
        elif fallback.status == "needs_clarification":
            return fallback.message

    return f"Không tìm thấy học phí cho ngành '{ten_nganh}'" + (
        f" khóa {khoa_clean}" if khoa_clean else ""
    ) + " trong cả graph lẫn bảng chuẩn hóa."


@tool
def tra_cuu_quy_dinh_hoc_phi(doi_tuong: str = "") -> str:
    """Tra cứu quy định chung về học phí: hệ số ngoài giờ, VLVH, đào tạo từ xa, thạc sĩ, tiến sĩ, dự bị dân tộc.

    Đầu vào:
    - doi_tuong: Đối tượng hoặc loại hình cần tra cứu (Ví dụ: "VLVH", "thạc sĩ", "ngoài giờ thiết kế", "tiến sĩ", "từ xa").
                 Để trống nếu muốn xem tất cả quy định.

    Trả về quy định học phí, hệ số, mức tiền áp dụng.
    """
    service = _get_graph_service()

    doi_tuong_clean = doi_tuong.strip() if doi_tuong else None

    try:
        results = service.get_tuition_policies(doi_tuong_clean)
    except Exception as e:
        logger.error("Graph get_tuition_policies lỗi: %s", e)
        results = []

    return _format_policy_results(results)


def _format_exemption_results(results: list[dict]) -> str:
    """Format exemption basis lookup results into a readable string."""
    if not results:
        return "Không tìm thấy thông tin mức trần cơ sở miễn giảm học phí phù hợp trong Graph."

    lines = ["[KẾT QUẢ TRA CỨU CƠ SỞ TÍNH MIỄN GIẢM HỌC PHÍ TỪ GRAPH - NGUỒN ƯU TIÊN]"]
    lines.append("LƯU Ý: Đây là MỨC HỌC PHÍ TRẦN làm cơ sở tính miễn, giảm theo Nghị định 81/2021/NĐ-CP & NĐ 97/2023/NĐ-CP (Năm học 2025-2026), KHÔNG PHẢI mức học phí thực tế.")

    for item in results:
        prog_name = item.get("program_name")
        prog_code = item.get("program_code")
        ten_khoi = item.get("ten_khoi") or item.get("khoi")
        muc_hp = item.get("muc_hp", 0)
        don_vi = item.get("don_vi_tinh", "dong/tin_chi")
        ghi_chu = item.get("ghi_chu", "")
        formatted_muc_hp = f"{int(muc_hp):,} {don_vi}".replace(",", ".")

        if prog_name:
            lines.append(f"\n- Ngành: {prog_name} (Mã ngành: {prog_code})")
            lines.append(f"  + Thuộc: {ten_khoi}")
        else:
            lines.append(f"\n- Đối tượng / Khối ngành: {ten_khoi}")

        lines.append(f"  + Mức trần cơ sở miễn giảm: {formatted_muc_hp}")
        if ghi_chu:
            lines.append(f"  + Ghi chú: {ghi_chu}")

    lines.append("\nNăm học: 2025-2026")
    lines.append("Căn cứ: Số 517/ĐHCT-TC ngày 18/02/2025, NĐ 81/2021/NĐ-CP & NĐ 97/2023/NĐ-CP")
    return "\n".join(lines)


@tool
def tra_cuu_co_so_mien_giam_graph(
    ten_nganh_hoac_khoi: str = "",
    khoa: str = "",
) -> str:
    """Tra cứu MỨC HỌC PHÍ LÀM CƠ SỞ ĐỂ TÍNH MIỄN, GIẢM HỌC PHÍ (mức trần quy định theo Nghị định 81/2021/NĐ-CP và NĐ 97/2023/NĐ-CP, Năm học 2025-2026) từ Neo4j Graph.

    Đầu vào:
    - ten_nganh_hoac_khoi: Tên ngành, mã ngành hoặc tên khối ngành (Ví dụ: "Công nghệ thông tin", "7480201", "Luật", "Khối V", "Khối 5", "GDQP", "Tiên tiến K47"). Để trống để xem tất cả.
    - khoa: Khóa tuyển sinh (Ví dụ: "K47", "K52").

    Trả về mức trần tính miễn giảm (đồng/tín chỉ), khối ngành và ghi chú căn cứ.
    """
    service = _get_graph_service()
    query_clean = ten_nganh_hoac_khoi.strip() if ten_nganh_hoac_khoi else None

    try:
        results = service.lookup_exemption_basis(query=query_clean)
    except Exception as e:
        logger.error("Graph lookup_exemption_basis lỗi: %s", e)
        results = []

    return _format_exemption_results(results)

