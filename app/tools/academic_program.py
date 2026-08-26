"""Academic program lookup tools for the CTU Chatbot.

Provides three LangChain tools that query the ``data/markdown_graph`` dataset:

* ``tra_cuu_nganh``  — look up a single program by name (fuzzy match).
* ``so_sanh_nganh``  — compare two programs side-by-side.
* ``tim_nganh``      — search programs matching free-text criteria.
"""

from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from langchain.tools import tool

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MARKDOWN_GRAPH_DIR = PROJECT_ROOT / "data" / "markdown_graph"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Lower-case, remove diacritics, collapse whitespace."""
    decomposed = unicodedata.normalize("NFD", text)
    without_marks = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    lowered = without_marks.casefold().replace("đ", "d")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", lowered)).strip()


def _extract_frontmatter(content: str) -> Dict[str, str]:
    """Parse YAML-like frontmatter between ``---`` fences."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    meta: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta


def _extract_general_info(content: str) -> Dict[str, str]:
    """Extract key facts from the '1. Thông tin chung' section."""
    info: Dict[str, str] = {}

    patterns = {
        "nganh": r"Ngành:\s*\*{0,2}(.+?)(?:\*{0,2})\s*(?:\(|$)",
        "ma_nganh": r"Mã ngành:\s*(\S+)",
        "so_tin_chi": r"Số lượng tín chỉ:\s*(\d+)",
        "thoi_gian": r"Thời gian đào tạo:\s*(.+?)$",
        "loai_van_bang": r"Loại văn bằng:\s*(.+?)$",
        "hinh_thuc": r"Hình thức đào tạo:\s*(.+?)$",
        "don_vi": r"Đơn vị quản lý:\s*(.+?)$",
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, content, re.MULTILINE)
        if m:
            info[key] = m.group(1).strip().rstrip("*")
    return info


def _extract_courses(content: str) -> List[str]:
    """Return a list of course names found in the khung chương trình."""
    # Courses appear as "* **<name>** (Mã số: ...)"
    return re.findall(r"\*\s+\*\*(.+?)\*\*\s*\(", content)


# ---------------------------------------------------------------------------
# Program index (loaded lazily)
# ---------------------------------------------------------------------------

@dataclass
class ProgramInfo:
    file_path: str
    file_name: str
    ma_nganh: str = ""
    ten_nganh: str = ""
    so_tin_chi: str = ""
    thoi_gian: str = ""
    don_vi: str = ""
    loai_van_bang: str = ""
    hinh_thuc: str = ""
    mon_hoc: List[str] = field(default_factory=list)
    _normalized_name: str = ""


_PROGRAM_INDEX: Dict[str, ProgramInfo] | None = None


def _load_index() -> Dict[str, ProgramInfo]:
    """Scan all markdown_graph files and build an in-memory index."""
    global _PROGRAM_INDEX
    if _PROGRAM_INDEX is not None:
        return _PROGRAM_INDEX

    index: Dict[str, ProgramInfo] = {}

    if not MARKDOWN_GRAPH_DIR.exists():
        _PROGRAM_INDEX = index
        return index

    for md_file in sorted(MARKDOWN_GRAPH_DIR.glob("*.md")):
        if md_file.name == "quychehocvu.md":
            continue  # Quy chế học vụ is not a program
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        fm = _extract_frontmatter(content)
        info = _extract_general_info(content)
        courses = _extract_courses(content)

        ten_nganh = fm.get("nganh_hoc", "") or info.get("nganh", "")
        prog = ProgramInfo(
            file_path=str(md_file),
            file_name=md_file.name,
            ma_nganh=info.get("ma_nganh", ""),
            ten_nganh=ten_nganh,
            so_tin_chi=info.get("so_tin_chi", ""),
            thoi_gian=info.get("thoi_gian", ""),
            don_vi=fm.get("don_vi", "") or info.get("don_vi", ""),
            loai_van_bang=info.get("loai_van_bang", ""),
            hinh_thuc=info.get("hinh_thuc", ""),
            mon_hoc=courses,
            _normalized_name=_normalize(ten_nganh),
        )
        # Index by several keys for fuzzy lookup
        index[_normalize(ten_nganh)] = prog
        if prog.ma_nganh:
            index[prog.ma_nganh] = prog

    _PROGRAM_INDEX = index
    return index


def _fuzzy_find(query: str) -> List[ProgramInfo]:
    """Find programs whose normalized name contains the query tokens."""
    index = _load_index()
    norm_query = _normalize(query)

    # Exact match first
    if norm_query in index:
        return [index[norm_query]]

    # Token containment
    query_tokens = set(norm_query.split())
    scored: List[tuple[float, ProgramInfo]] = []
    seen_paths: set[str] = set()
    for key, prog in index.items():
        if prog.file_path in seen_paths:
            continue
        key_tokens = set(key.split())
        overlap = len(query_tokens & key_tokens)
        if overlap > 0:
            score = overlap / max(len(query_tokens), 1)
            scored.append((score, prog))
            seen_paths.add(prog.file_path)

    scored.sort(key=lambda x: x[0], reverse=True)
    return [prog for _, prog in scored[:5]]


def _format_program(prog: ProgramInfo) -> str:
    """Format a single program as readable text."""
    lines = [
        f"📚 **{prog.ten_nganh}**",
        f"  - Mã ngành: {prog.ma_nganh}" if prog.ma_nganh else "",
        f"  - Số tín chỉ: {prog.so_tin_chi}" if prog.so_tin_chi else "",
        f"  - Thời gian đào tạo: {prog.thoi_gian}" if prog.thoi_gian else "",
        f"  - Loại văn bằng: {prog.loai_van_bang}" if prog.loai_van_bang else "",
        f"  - Hình thức: {prog.hinh_thuc}" if prog.hinh_thuc else "",
        f"  - Đơn vị: {prog.don_vi}" if prog.don_vi else "",
    ]
    if prog.mon_hoc:
        lines.append(f"  - Số môn học trong khung CTĐT: {len(prog.mon_hoc)}")
    return "\n".join(line for line in lines if line)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def tra_cuu_nganh(ten_nganh: str) -> str:
    """Tra cứu thông tin tổng quan về một ngành đào tạo tại Đại học Cần Thơ.
    Đầu vào:
    - ten_nganh: Tên ngành hoặc mã ngành cần tra cứu (ví dụ: "Công nghệ thông tin", "7480201", "CNTT").
    """
    results = _fuzzy_find(ten_nganh)
    if not results:
        return (
            f"Không tìm thấy ngành '{ten_nganh}' trong dữ liệu chương trình đào tạo. "
            "Vui lòng kiểm tra lại tên hoặc mã ngành."
        )
    if len(results) == 1:
        prog = results[0]
        output = _format_program(prog)
        if prog.mon_hoc:
            output += "\n\n**Danh sách một số môn học chính:**\n"
            for i, course in enumerate(prog.mon_hoc[:30], 1):
                output += f"  {i}. {course}\n"
            if len(prog.mon_hoc) > 30:
                output += f"  ... và {len(prog.mon_hoc) - 30} môn khác.\n"
        return output

    # Multiple matches
    output = f"Tìm thấy {len(results)} ngành phù hợp với '{ten_nganh}':\n\n"
    for prog in results:
        output += _format_program(prog) + "\n\n"
    return output


@tool
def so_sanh_nganh(nganh_1: str, nganh_2: str) -> str:
    """So sánh hai ngành đào tạo tại Đại học Cần Thơ.
    Đầu vào:
    - nganh_1: Tên hoặc mã ngành thứ nhất (ví dụ: "CNTT").
    - nganh_2: Tên hoặc mã ngành thứ hai (ví dụ: "Trí tuệ nhân tạo").
    """
    results_1 = _fuzzy_find(nganh_1)
    results_2 = _fuzzy_find(nganh_2)

    if not results_1:
        return f"Không tìm thấy ngành '{nganh_1}'."
    if not results_2:
        return f"Không tìm thấy ngành '{nganh_2}'."

    p1, p2 = results_1[0], results_2[0]

    # Common and unique courses
    set1 = set(_normalize(c) for c in p1.mon_hoc)
    set2 = set(_normalize(c) for c in p2.mon_hoc)
    common = set1 & set2
    only1 = set1 - set2
    only2 = set2 - set1

    table = f"""## So sánh: {p1.ten_nganh} vs {p2.ten_nganh}

| Tiêu chí | {p1.ten_nganh} | {p2.ten_nganh} |
|----------|----------------|----------------|
| Mã ngành | {p1.ma_nganh} | {p2.ma_nganh} |
| Số tín chỉ | {p1.so_tin_chi} | {p2.so_tin_chi} |
| Thời gian | {p1.thoi_gian} | {p2.thoi_gian} |
| Văn bằng | {p1.loai_van_bang} | {p2.loai_van_bang} |
| Đơn vị | {p1.don_vi} | {p2.don_vi} |
| Số môn học | {len(p1.mon_hoc)} | {len(p2.mon_hoc)} |
| Môn chung | {len(common)} | {len(common)} |
| Môn riêng | {len(only1)} | {len(only2)} |
"""
    return table


@tool
def tim_nganh(tieu_chi: str) -> str:
    """Tìm ngành đào tạo theo tiêu chí (ví dụ: 'ngành nào có học AI', 'ngành 4 năm', 'ngành thuộc trường CNTT').
    Đầu vào:
    - tieu_chi: Tiêu chí tìm kiếm tự do.
    """
    index = _load_index()
    norm_criteria = _normalize(tieu_chi)
    criteria_tokens = set(norm_criteria.split())

    matches: List[tuple[int, ProgramInfo]] = []
    seen_paths: set[str] = set()

    for key, prog in index.items():
        if prog.file_path in seen_paths:
            continue

        score = 0
        searchable = _normalize(
            f"{prog.ten_nganh} {prog.don_vi} {prog.hinh_thuc} "
            f"{prog.loai_van_bang} {' '.join(prog.mon_hoc)}"
        )
        searchable_tokens = set(searchable.split())
        overlap = len(criteria_tokens & searchable_tokens)
        if overlap > 0:
            score = overlap
            matches.append((score, prog))
            seen_paths.add(prog.file_path)

    if not matches:
        return f"Không tìm thấy ngành nào phù hợp với tiêu chí '{tieu_chi}'."

    matches.sort(key=lambda x: x[0], reverse=True)
    top = matches[:10]

    output = f"Tìm thấy {len(matches)} ngành phù hợp với '{tieu_chi}':\n\n"
    for _, prog in top:
        output += f"- **{prog.ten_nganh}** (Mã: {prog.ma_nganh}) — {prog.so_tin_chi} TC, {prog.thoi_gian}\n"
    if len(matches) > 10:
        output += f"\n... và {len(matches) - 10} ngành khác.\n"
    return output
