"""Academic program lookup tools for the CTU Chatbot.

Provides six LangChain tools backed by Neo4j Graph:

Existing (refactored):
* ``tra_cuu_nganh``       — look up a single program by name (graph query).
* ``so_sanh_nganh``       — compare two programs side-by-side (graph intersection).
* ``tim_nganh``           — search programs matching free-text criteria (graph traversal).

New:
* ``xem_chuoi_tien_quyet`` — prerequisite chain for a course (variable-length path).
* ``mon_chung_giua_nganh`` — shared courses between two programs (graph intersection).
* ``tim_nganh_co_mon``     — find programs containing a specific course (reverse traversal).
"""

from __future__ import annotations

import logging
from typing import Optional

from langchain.tools import tool

from app.services.graph_service import AcademicGraphService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level graph service reference — set by app startup (main.py)
# ---------------------------------------------------------------------------
_graph_service: Optional[AcademicGraphService] = None


def set_graph_service(service: AcademicGraphService) -> None:
    """Called once during app startup to inject the shared graph service."""
    global _graph_service
    _graph_service = service


def _get_service() -> AcademicGraphService:
    if _graph_service is None:
        raise RuntimeError(
            "AcademicGraphService chưa được khởi tạo. "
            "Hãy gọi set_graph_service() trước khi dùng tools."
        )
    return _graph_service


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _format_program_detail(data: dict) -> str:
    """Format kết quả lookup_program thành text đẹp."""
    prog = data["program"]
    lines = [
        f"📚 **{prog.get('name', '')}**",
        f"  - Mã ngành: {prog.get('code', '')}",
        f"  - Số tín chỉ: {prog.get('total_credits', '')}",
        f"  - Thời gian đào tạo: {prog.get('duration', '')}",
        f"  - Loại văn bằng: {prog.get('degree_type', '')}",
        f"  - Hình thức: {prog.get('training_forms', '')}",
        f"  - Đơn vị: {prog.get('unit', '')}",
        f"  - Tổng số môn học: {data.get('total_courses', 0)}",
    ]

    # Blocks summary
    blocks = data.get("blocks", [])
    if blocks:
        lines.append("\n**Cấu trúc khung chương trình:**")
        for block in blocks:
            bb = block.get("tc_bat_buoc", 0) or 0
            tc = block.get("tc_tu_chon", 0) or 0
            lines.append(
                f"  - {block['name']}: {block.get('total_credits', 0)} TC "
                f"(BB: {bb}, TC: {tc}) — {len(block.get('courses', []))} môn"
            )

    # Sample courses from each block
    if blocks:
        lines.append("\n**Một số môn học chính:**")
        count = 0
        for block in blocks:
            courses = block.get("courses", [])
            for course in courses[:5]:
                if course.get("code"):
                    count += 1
                    req = "BB" if course.get("is_required") else "TC"
                    lines.append(
                        f"  {count}. {course['name']} ({course['code']}) "
                        f"— {course.get('credits', '?')} TC [{req}]"
                    )
                if count >= 30:
                    break
            if count >= 30:
                remaining = data.get("total_courses", 0) - 30
                if remaining > 0:
                    lines.append(f"  ... và {remaining} môn khác.")
                break

    # PLOs
    plos = data.get("plos", [])
    if plos:
        lines.append(f"\n**Chuẩn đầu ra ({len(plos)} PLOs):**")
        for plo in plos[:5]:
            desc = plo["description"]
            if len(desc) > 120:
                desc = desc[:117] + "..."
            lines.append(f"  - {plo['id']}: {desc}")
        if len(plos) > 5:
            lines.append(f"  ... và {len(plos) - 5} PLOs khác.")

    return "\n".join(lines)


def _format_comparison(data: dict) -> str:
    """Format kết quả compare_programs thành bảng Markdown."""
    if data.get("error"):
        nf = data.get("not_found", [])
        return f"Không tìm thấy ngành: {', '.join(nf)}"

    p1 = data["program1"]
    p2 = data["program2"]
    common = data.get("common_courses", [])

    table = f"""## So sánh: {p1.get('name')} vs {p2.get('name')}

| Tiêu chí | {p1.get('name')} | {p2.get('name')} |
|----------|----------------|----------------|
| Mã ngành | {p1.get('code')} | {p2.get('code')} |
| Số tín chỉ | {p1.get('total_credits')} | {p2.get('total_credits')} |
| Thời gian | {p1.get('duration')} | {p2.get('duration')} |
| Văn bằng | {p1.get('degree_type')} | {p2.get('degree_type')} |
| Đơn vị | {p1.get('unit')} | {p2.get('unit')} |
| Tổng môn | {data.get('total_courses_1', '?')} | {data.get('total_courses_2', '?')} |
| Môn chung | {data.get('common_count', 0)} | {data.get('common_count', 0)} |
| Môn riêng | {data.get('only1_count', 0)} | {data.get('only2_count', 0)} |
"""

    if common:
        table += "\n**Một số môn chung:**\n"
        for i, c in enumerate(common[:15], 1):
            table += f"  {i}. {c.get('name', '?')} ({c.get('code', '?')}) — {c.get('credits', '?')} TC\n"
        if len(common) > 15:
            table += f"  ... và {len(common) - 15} môn chung khác.\n"

    return table


# ---------------------------------------------------------------------------
# REFACTORED TOOLS (3 tools cũ → dùng Neo4j backend)
# ---------------------------------------------------------------------------


@tool
def tra_cuu_nganh(ten_nganh: str) -> str:
    """Tra cứu thông tin tổng quan về một ngành đào tạo tại Đại học Cần Thơ.
    Đầu vào:
    - ten_nganh: Tên ngành hoặc mã ngành cần tra cứu (ví dụ: "Công nghệ thông tin", "7480201", "CNTT").
    """
    svc = _get_service()
    result = svc.lookup_program(ten_nganh)
    if not result:
        return (
            f"Không tìm thấy ngành '{ten_nganh}' trong dữ liệu chương trình đào tạo. "
            "Vui lòng kiểm tra lại tên hoặc mã ngành."
        )
    return _format_program_detail(result)


@tool
def so_sanh_nganh(nganh_1: str, nganh_2: str) -> str:
    """So sánh hai ngành đào tạo tại Đại học Cần Thơ.
    Đầu vào:
    - nganh_1: Tên hoặc mã ngành thứ nhất (ví dụ: "CNTT").
    - nganh_2: Tên hoặc mã ngành thứ hai (ví dụ: "Trí tuệ nhân tạo").
    """
    svc = _get_service()
    result = svc.compare_programs(nganh_1, nganh_2)
    if not result:
        return "Không thể so sánh hai ngành. Vui lòng kiểm tra lại tên ngành."
    return _format_comparison(result)


@tool
def tim_nganh(tieu_chi: str) -> str:
    """Tìm ngành đào tạo theo tiêu chí (ví dụ: 'ngành nào có học AI', 'ngành 4 năm', 'ngành thuộc trường CNTT').
    Đầu vào:
    - tieu_chi: Tiêu chí tìm kiếm tự do.
    """
    svc = _get_service()
    matches = svc.search_programs(tieu_chi)

    if not matches:
        return f"Không tìm thấy ngành nào phù hợp với tiêu chí '{tieu_chi}'."

    output = f"Tìm thấy {len(matches)} ngành phù hợp với '{tieu_chi}':\n\n"
    for m in matches[:10]:
        matched = m.get("matched_courses")
        extra = ""
        if matched:
            extra = f" (có môn: {', '.join(matched)})"
        output += (
            f"- **{m.get('name', '?')}** (Mã: {m.get('code', '?')}) "
            f"— {m.get('total_credits', '?')} TC, {m.get('duration', '?')}"
            f"{extra}\n"
        )
    if len(matches) > 10:
        output += f"\n... và {len(matches) - 10} ngành khác.\n"
    return output


# ---------------------------------------------------------------------------
# NEW TOOLS (3 tools mới)
# ---------------------------------------------------------------------------


@tool
def xem_chuoi_tien_quyet(ma_mon: str) -> str:
    """Xem chuỗi các môn học tiên quyết (prerequisite chain) của một môn học.
    Cho biết: muốn học môn này cần học trước những môn nào, và thứ tự học.
    Đầu vào:
    - ma_mon: Mã môn học hoặc tên môn (ví dụ: "CT226H", "Lập trình hướng đối tượng").
    """
    svc = _get_service()
    result = svc.get_prerequisite_chain(ma_mon)

    if not result:
        return (
            f"Không tìm thấy môn học '{ma_mon}' trong dữ liệu. "
            "Vui lòng kiểm tra lại mã hoặc tên môn."
        )

    course = result["course"]
    chain = result["prerequisite_chain"]
    parallel = result["parallel_courses"]
    programs = result["belongs_to_programs"]

    lines = [f"📋 **Chuỗi tiên quyết của {course['name']} ({course['code']})**\n"]

    if len(chain) <= 1:
        lines.append("Môn này **không có tiên quyết** (có thể học ngay).")
    else:
        lines.append("**Thứ tự học (từ cơ bản → nâng cao):**")
        # chain[0] là môn gốc, chain[1:] là tiên quyết
        prereqs = [c for c in chain if c["depth"] > 0]
        # Reverse để hiện từ cơ bản nhất trước
        prereqs.sort(key=lambda x: x["depth"], reverse=True)
        for i, c in enumerate(prereqs, 1):
            lines.append(
                f"  {i}. {c['name']} ({c['code']}) — {c.get('credits', '?')} TC"
            )
        lines.append(f"  → **{course['name']} ({course['code']})**")

    if parallel:
        lines.append("\n**Môn song hành (cần học cùng lúc):**")
        for c in parallel:
            lines.append(f"  - {c['name']} ({c['code']}) — {c.get('credits', '?')} TC")

    if programs:
        lines.append(f"\n**Thuộc các ngành:** {', '.join(p['name'] for p in programs[:5])}")
        if len(programs) > 5:
            lines.append(f"... và {len(programs) - 5} ngành khác.")

    return "\n".join(lines)


@tool
def mon_chung_giua_nganh(nganh_1: str, nganh_2: str) -> str:
    """Tìm danh sách chi tiết các môn học chung giữa hai ngành đào tạo.
    Đầu vào:
    - nganh_1: Tên hoặc mã ngành thứ nhất.
    - nganh_2: Tên hoặc mã ngành thứ hai.
    """
    svc = _get_service()
    result = svc.get_shared_courses(nganh_1, nganh_2)

    if not result:
        return "Không thể tìm môn chung. Vui lòng kiểm tra lại tên ngành."

    if result.get("error"):
        nf = result.get("not_found", [])
        return f"Không tìm thấy ngành: {', '.join(nf)}"

    p1 = result["program1"]
    p2 = result["program2"]
    shared = result["shared_courses"]

    lines = [
        f"📊 **Môn chung giữa {p1['name']} và {p2['name']}**",
        f"Số môn chung: **{result['shared_count']}** "
        f"(tổng {result['shared_credits']} TC)\n",
    ]

    if not shared:
        lines.append("Hai ngành này không có môn chung nào.")
    else:
        for i, c in enumerate(shared[:30], 1):
            req = "BB" if c.get("is_required") else "TC"
            lines.append(
                f"  {i}. {c['name']} ({c['code']}) — {c.get('credits', '?')} TC [{req}]"
            )
        if len(shared) > 30:
            lines.append(f"\n... và {len(shared) - 30} môn chung khác.")

    return "\n".join(lines)


@tool
def tim_nganh_co_mon(ten_mon: str) -> str:
    """Tìm tất cả các ngành đào tạo có chứa một môn học cụ thể.
    Đầu vào:
    - ten_mon: Tên môn học hoặc mã môn (ví dụ: "Trí tuệ nhân tạo", "CT223H").
    """
    svc = _get_service()
    results = svc.find_programs_by_course(ten_mon)

    if not results:
        return (
            f"Không tìm thấy môn học '{ten_mon}' trong dữ liệu. "
            "Vui lòng kiểm tra lại mã hoặc tên môn."
        )

    lines = []
    for item in results:
        course = f"{item['course_name']} ({item['course_code']}) — {item.get('credits', '?')} TC"
        programs = item.get("programs", [])
        lines.append(f"📚 **{course}**")
        lines.append(f"Có trong **{len(programs)}** ngành:\n")
        for i, p in enumerate(programs[:15], 1):
            lines.append(
                f"  {i}. {p['prog_name']} ({p['prog_code']}) — {p.get('unit', '')}"
            )
        if len(programs) > 15:
            lines.append(f"  ... và {len(programs) - 15} ngành khác.\n")

    return "\n".join(lines)
