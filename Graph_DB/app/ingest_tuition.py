"""Ingest học phí từ markdown vào Neo4j graph.

Parse 4 file markdown học phí:
- MucHocPhi_DaiHocChinhQuy_Khoa51_VeTruoc.md
- MucHocPhi_DaiHocChinhQuy_Khoa52.md
- MucHocPhi_ChatLuongCao_TienTien.md
- MucHocPhi_QuyDinhChung.md

Tạo node TuitionFee + TuitionPolicy, kết nối với Program hiện có.
Sử dụng MERGE → idempotent, chạy lại không duplicate.
"""

from __future__ import annotations

import os
import re
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MARKDOWN_DIR = PROJECT_ROOT / "data" / "markdown"

NAM_HOC = "2026-2027"


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────


def _parse_table(text: str) -> List[List[str]]:
    """Parse markdown table → list of rows (list of cell strings).

    Bỏ qua header separator (--- | ---) và header row.
    Returns list of data rows only.
    """
    rows: List[List[str]] = []
    header_found = False
    separator_found = False

    for line in text.split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue

        cells = [c.strip() for c in line.split("|")]
        # Remove empty first/last from leading/trailing |
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]

        if not cells:
            continue

        # First table row = header
        if not header_found:
            header_found = True
            continue

        # Second row = separator (--- | ---)
        if not separator_found:
            if all(c.replace("-", "").replace(" ", "") == "" for c in cells):
                separator_found = True
                continue

        rows.append(cells)

    return rows


def _parse_money(value: str) -> Optional[int]:
    """Parse Vietnamese money format → int.

    '695.000' → 695000
    '1.553.000' → 1553000
    '25' → 25 (triệu, keep as-is)
    '' → None
    """
    value = value.strip()
    if not value:
        return None
    # Remove dots used as thousand separators
    cleaned = value.replace(".", "")
    try:
        return int(cleaned)
    except ValueError:
        # Try float for cases like "114,5"
        try:
            return float(value.replace(",", "."))
        except ValueError:
            return None


def _make_tuition_id(
    ma_nganh: str, khoa: str, loai_ct: str, don_vi: str
) -> str:
    """Generate unique ID for TuitionFee node."""
    return f"{ma_nganh}_{khoa}_{loai_ct}_{don_vi}".lower().replace("/", "_")


# ─────────────────────────────────────────────────────────────────────────────
# Parsers
# ─────────────────────────────────────────────────────────────────────────────


def parse_tuition_k51(filepath: Path) -> List[Dict[str, Any]]:
    """Parse MucHocPhi_DaiHocChinhQuy_Khoa51_VeTruoc.md.

    Table format: STT | Mã ngành | Khối | Lĩnh vực | Ngành | Đơn vị | Mức HP 26-27/TC
    → 1 TuitionFee per row.
    """
    text = filepath.read_text(encoding="utf-8")
    rows = _parse_table(text)
    fees: List[Dict[str, Any]] = []

    for row in rows:
        if len(row) < 7:
            continue

        ma_nganh = row[1].strip()
        khoi = row[2].strip()
        ten_nganh = row[4].strip()
        don_vi = row[5].strip()
        muc_hp = _parse_money(row[6])

        if not ma_nganh or muc_hp is None:
            continue

        fee_id = _make_tuition_id(ma_nganh, "K51_ve_truoc", "chuan", "dong_tc")
        fees.append({
            "id": fee_id,
            "ma_nganh": ma_nganh,
            "khoa": "K51_ve_truoc",
            "nam_hoc": NAM_HOC,
            "loai_ct": "chuan",
            "don_vi_tinh": "dong/tin_chi",
            "muc_hp": muc_hp,
            "ten_nganh": ten_nganh,
            "don_vi": don_vi,
            "khoi": khoi,
        })

    logger.info("  Parsed K51: %d TuitionFee nodes", len(fees))
    return fees


def parse_tuition_k52(filepath: Path) -> List[Dict[str, Any]]:
    """Parse MucHocPhi_DaiHocChinhQuy_Khoa52.md.

    Table format: STT | Mã ngành | Khối | Lĩnh vực | Ngành | Đơn vị | K52 Trđ/khóa | K52 Đồng/tín chỉ
    → 2 TuitionFee per row (HP/khóa + HP/TC).
    """
    text = filepath.read_text(encoding="utf-8")
    rows = _parse_table(text)
    fees: List[Dict[str, Any]] = []

    for row in rows:
        if len(row) < 8:
            continue

        ma_nganh = row[1].strip()
        khoi = row[2].strip()
        ten_nganh = row[4].strip()
        don_vi = row[5].strip()
        hp_khoa = _parse_money(row[6])
        hp_tc = _parse_money(row[7])

        if not ma_nganh:
            continue

        # HP toàn khóa (triệu đồng)
        if hp_khoa is not None:
            fee_id = _make_tuition_id(ma_nganh, "K52", "chuan", "trieu_dong_khoa")
            fees.append({
                "id": fee_id,
                "ma_nganh": ma_nganh,
                "khoa": "K52",
                "nam_hoc": NAM_HOC,
                "loai_ct": "chuan",
                "don_vi_tinh": "trieu_dong/khoa",
                "muc_hp": hp_khoa,
                "ten_nganh": ten_nganh,
                "don_vi": don_vi,
                "khoi": khoi,
            })

        # HP/tín chỉ
        if hp_tc is not None:
            fee_id = _make_tuition_id(ma_nganh, "K52", "chuan", "dong_tc")
            fees.append({
                "id": fee_id,
                "ma_nganh": ma_nganh,
                "khoa": "K52",
                "nam_hoc": NAM_HOC,
                "loai_ct": "chuan",
                "don_vi_tinh": "dong/tin_chi",
                "muc_hp": hp_tc,
                "ten_nganh": ten_nganh,
                "don_vi": don_vi,
                "khoi": khoi,
            })

    logger.info("  Parsed K52: %d TuitionFee nodes", len(fees))
    return fees


def parse_tuition_clc_tt(filepath: Path) -> List[Dict[str, Any]]:
    """Parse MucHocPhi_ChatLuongCao_TienTien.md.

    Multiple tables with multi-column khóa format (K44..K52).
    → 1 TuitionFee per non-empty cell.
    """
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")
    fees: List[Dict[str, Any]] = []

    # We need to detect table sections and parse them contextually
    current_section = ""
    current_loai_ct = ""
    current_don_vi_tinh = ""
    in_table = False
    header_cols: List[str] = []
    separator_seen = False

    # Map section headings to metadata
    KHOA_COLS = ["K44", "K45", "K46", "K47", "K48", "K49", "K50", "K51", "K52"]

    for line in lines:
        stripped = line.strip()

        # Detect section headings
        if stripped.startswith("## I."):
            current_don_vi_tinh = "trieu_dong/nam_hoc"
            in_table = False
            separator_seen = False
            continue

        if stripped.startswith("## II."):
            current_don_vi_tinh = "dong/tin_chi"
            in_table = False
            separator_seen = False
            continue

        if "Chương trình Chất lượng cao" in stripped and stripped.startswith("###"):
            current_loai_ct = "clc"
            in_table = False
            separator_seen = False
            continue

        if "Chương trình Tiên tiến" in stripped and stripped.startswith("###"):
            current_loai_ct = "tien_tien"
            in_table = False
            separator_seen = False
            continue

        # Detect HP đại cương chung table
        if "Mức học phí của khối kiến thức đại cương chung" in stripped:
            current_section = "dai_cuong_chung"
            in_table = False
            separator_seen = False
            continue

        # Parse table rows
        if not stripped.startswith("|"):
            if in_table:
                in_table = False
                separator_seen = False
            continue

        cells = [c.strip() for c in stripped.split("|")]
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]

        if not cells:
            continue

        # Header row
        if not in_table:
            in_table = True
            header_cols = cells
            separator_seen = False
            continue

        # Separator row
        if not separator_seen:
            if all(c.replace("-", "").replace(" ", "") == "" for c in cells):
                separator_seen = True
                continue

        # Special case: HP đại cương chung (2-row table: Khóa + Đồng/TC)
        if current_section == "dai_cuong_chung":
            # This is a 2-row table: header = Khóa labels, data = values
            for i, cell in enumerate(cells):
                if i == 0:
                    continue  # Skip label column
                muc_hp = _parse_money(cell)
                if muc_hp is None:
                    continue

                # Map column index to khóa from header
                if i < len(header_cols):
                    khoa = header_cols[i].strip()
                else:
                    continue

                fee_id = _make_tuition_id(
                    "dai_cuong_chung", khoa, "clc_tt", "dong_tc"
                )
                fees.append({
                    "id": fee_id,
                    "ma_nganh": "dai_cuong_chung",
                    "khoa": khoa,
                    "nam_hoc": NAM_HOC,
                    "loai_ct": "clc_tt",
                    "don_vi_tinh": "dong/tin_chi",
                    "muc_hp": muc_hp,
                    "ten_nganh": "Đại cương chung (CLC/TT)",
                    "don_vi": "",
                    "khoi": "",
                })

            current_section = ""  # Reset after processing
            continue

        # Normal table: TT | Ngành | K44 | K45 | ... | K52
        if len(cells) < 3:
            continue

        ten_nganh = cells[1].strip()
        if not ten_nganh:
            continue

        # Data columns start at index 2
        for col_idx in range(2, len(cells)):
            cell_val = cells[col_idx].strip()
            muc_hp = _parse_money(cell_val)
            if muc_hp is None:
                continue

            # Map column to khóa
            khoa_idx = col_idx - 2
            if khoa_idx < len(KHOA_COLS):
                khoa = KHOA_COLS[khoa_idx]
            else:
                continue

            # We don't have mã ngành in CLC/TT tables, use tên ngành as part of ID
            nganh_key = re.sub(
                r"[^a-z0-9]+", "_",
                ten_nganh.lower()
                .replace("đ", "d")
                .replace("ă", "a")
                .replace("â", "a")
                .replace("ê", "e")
                .replace("ô", "o")
                .replace("ơ", "o")
                .replace("ư", "u")
            ).strip("_")

            don_vi_key = "trieu_nam" if current_don_vi_tinh == "trieu_dong/nam_hoc" else "dong_tc"
            fee_id = f"{nganh_key}_{khoa}_{current_loai_ct}_{don_vi_key}".lower()

            fees.append({
                "id": fee_id,
                "ma_nganh": "",  # CLC/TT tables don't have mã ngành
                "khoa": khoa,
                "nam_hoc": NAM_HOC,
                "loai_ct": current_loai_ct,
                "don_vi_tinh": current_don_vi_tinh,
                "muc_hp": muc_hp,
                "ten_nganh": ten_nganh,
                "don_vi": "",
                "khoi": "",
            })

    logger.info("  Parsed CLC/TT: %d TuitionFee nodes", len(fees))
    return fees


def parse_tuition_policies(filepath: Path) -> List[Dict[str, Any]]:
    """Parse MucHocPhi_QuyDinhChung.md → TuitionPolicy nodes.

    Extract structured policy data from rule text.
    """
    policies: List[Dict[str, Any]] = []

    # ─── Hardcoded policies from the document ───
    # These are structured rules that are best extracted deterministically

    # 1. Hệ số ngoài giờ thiết kế
    policies.append({
        "id": "ngoai_gio_thiet_ke_k51",
        "loai": "he_so",
        "mo_ta": "Học ngoài thời gian thiết kế CTĐT ngành thứ nhất (K51 trở về trước): HP nhân hệ số 1,3",
        "he_so": 1.3,
        "muc_hp": None,
        "don_vi_tinh": "",
        "doi_tuong": "ĐHCQ chuẩn K51 trở về trước",
        "nam_hoc": NAM_HOC,
    })

    policies.append({
        "id": "ngoai_gio_thiet_ke_k52",
        "loai": "he_so",
        "mo_ta": "Học ngoài thời gian thiết kế CTĐT ngành thứ nhất (K52): HP nhân hệ số 1,3",
        "he_so": 1.3,
        "muc_hp": None,
        "don_vi_tinh": "",
        "doi_tuong": "ĐHCQ chuẩn K52",
        "nam_hoc": NAM_HOC,
    })

    policies.append({
        "id": "ngoai_gio_clc_k50_truoc",
        "loai": "he_so",
        "mo_ta": "Học ngoài thời gian thiết kế CTĐT CLC/TT (K50 trở về trước): HP nhân hệ số 1,0",
        "he_so": 1.0,
        "muc_hp": None,
        "don_vi_tinh": "",
        "doi_tuong": "CLC/TT K50 trở về trước",
        "nam_hoc": NAM_HOC,
    })

    policies.append({
        "id": "ngoai_gio_clc_k51_sau",
        "loai": "he_so",
        "mo_ta": "Học ngoài thời gian thiết kế CTĐT CLC/TT (K51 trở về sau): HP nhân hệ số 1,3",
        "he_so": 1.3,
        "muc_hp": None,
        "don_vi_tinh": "",
        "doi_tuong": "CLC/TT K51 trở về sau",
        "nam_hoc": NAM_HOC,
    })

    # 2. HP đại cương chung K51
    policies.append({
        "id": "dai_cuong_chung_k51",
        "loai": "muc_hp_co_dinh",
        "mo_ta": "Mức HP khối kiến thức đại cương chung tất cả ngành K51 trở về trước",
        "he_so": None,
        "muc_hp": 695000,
        "don_vi_tinh": "dong/tin_chi",
        "doi_tuong": "ĐHCQ chuẩn K51 trở về trước - đại cương chung",
        "nam_hoc": NAM_HOC,
    })

    # 3. HP đại cương chung K52
    policies.append({
        "id": "dai_cuong_chung_k52",
        "loai": "muc_hp_co_dinh",
        "mo_ta": "Mức HP khối kiến thức đại cương chung tất cả ngành K52: 695.000 đ/TC",
        "he_so": None,
        "muc_hp": 695000,
        "don_vi_tinh": "dong/tin_chi",
        "doi_tuong": "ĐHCQ chuẩn K52 - đại cương chung",
        "nam_hoc": NAM_HOC,
    })

    # 4. Dự bị dân tộc
    policies.append({
        "id": "du_bi_dan_toc",
        "loai": "muc_hp_co_dinh",
        "mo_ta": "HP bồi dưỡng kiến thức tại Khoa Dự bị Dân tộc: 12.000.000 đ/năm; 6.000.000 đ/HK; 300.000 đ/TC",
        "he_so": None,
        "muc_hp": 12000000,
        "don_vi_tinh": "dong/nam_hoc",
        "doi_tuong": "Học sinh diện xét tuyển thẳng, bồi dưỡng tại Khoa Dự bị Dân tộc",
        "nam_hoc": NAM_HOC,
    })

    # 5. VLVH
    policies.append({
        "id": "vlvh_khoa_2026_truoc",
        "loai": "muc_hp_co_dinh",
        "mo_ta": "HP VLVH khóa tuyển sinh từ 2026 về trước: 693.000 đ/TC (từ HK2 năm 2026-2027)",
        "he_so": None,
        "muc_hp": 693000,
        "don_vi_tinh": "dong/tin_chi",
        "doi_tuong": "VLVH khóa tuyển sinh ≤2026",
        "nam_hoc": NAM_HOC,
    })

    policies.append({
        "id": "vlvh_khoa_2027",
        "loai": "muc_hp_co_dinh",
        "mo_ta": "HP VLVH khóa tuyển sinh từ 2027: 731.000 đ/TC (cố định suốt thời gian thiết kế)",
        "he_so": None,
        "muc_hp": 731000,
        "don_vi_tinh": "dong/tin_chi",
        "doi_tuong": "VLVH khóa tuyển sinh 2027",
        "nam_hoc": NAM_HOC,
    })

    policies.append({
        "id": "vlvh_he_so_lop_it",
        "loai": "he_so",
        "mo_ta": "VLVH lớp <30 SV: thỏa thuận nhân hệ số điều chỉnh, tối đa 1,5 lần",
        "he_so": 1.5,
        "muc_hp": None,
        "don_vi_tinh": "",
        "doi_tuong": "VLVH lớp dưới 30 sinh viên",
        "nam_hoc": NAM_HOC,
    })

    # 6. Đào tạo từ xa
    policies.append({
        "id": "tu_xa_khoa_2026_truoc",
        "loai": "muc_hp_co_dinh",
        "mo_ta": "HP đào tạo từ xa khóa ≤2026: 495.000 đ/TC (từ HK2 năm 2026-2027)",
        "he_so": None,
        "muc_hp": 495000,
        "don_vi_tinh": "dong/tin_chi",
        "doi_tuong": "Đào tạo từ xa khóa ≤2026",
        "nam_hoc": NAM_HOC,
    })

    policies.append({
        "id": "tu_xa_khoa_2027",
        "loai": "muc_hp_co_dinh",
        "mo_ta": "HP đào tạo từ xa khóa 2027: 574.300 đ/TC (cố định suốt thời gian thiết kế)",
        "he_so": None,
        "muc_hp": 574300,
        "don_vi_tinh": "dong/tin_chi",
        "doi_tuong": "Đào tạo từ xa khóa 2027",
        "nam_hoc": NAM_HOC,
    })

    policies.append({
        "id": "tu_xa_he_so_lop_it",
        "loai": "he_so",
        "mo_ta": "Đào tạo từ xa lớp <25 SV: thỏa thuận nhân hệ số điều chỉnh, tối đa 1,5 lần",
        "he_so": 1.5,
        "muc_hp": None,
        "don_vi_tinh": "",
        "doi_tuong": "Đào tạo từ xa lớp dưới 25 sinh viên",
        "nam_hoc": NAM_HOC,
    })

    # 7. Thạc sĩ
    policies.append({
        "id": "thac_si_khoa_2025_truoc",
        "loai": "muc_hp_co_dinh",
        "mo_ta": "HP thạc sĩ khóa ≤2025: 1.010.000 đ/TC (30.300.000 đ/năm học)",
        "he_so": None,
        "muc_hp": 1010000,
        "don_vi_tinh": "dong/tin_chi",
        "doi_tuong": "Thạc sĩ khóa ≤2025",
        "nam_hoc": NAM_HOC,
    })

    policies.append({
        "id": "thac_si_khoa_2026",
        "loai": "muc_hp_co_dinh",
        "mo_ta": "HP thạc sĩ khóa 2026: 1.061.000 đ/TC (31.800.000 đ/năm học), cố định theo khóa",
        "he_so": None,
        "muc_hp": 1061000,
        "don_vi_tinh": "dong/tin_chi",
        "doi_tuong": "Thạc sĩ khóa 2026",
        "nam_hoc": NAM_HOC,
    })

    policies.append({
        "id": "thac_si_he_so_ngoai_gio",
        "loai": "he_so",
        "mo_ta": "Thạc sĩ học ngoài giờ hành chính hoặc ngoài thời gian thiết kế: HP nhân 1,5 (trừ Luận văn 15TC, Đề án 9TC, TTTN 6TC)",
        "he_so": 1.5,
        "muc_hp": None,
        "don_vi_tinh": "",
        "doi_tuong": "Thạc sĩ ngoài giờ/ngoài thiết kế",
        "nam_hoc": NAM_HOC,
    })

    policies.append({
        "id": "thac_si_cham_tien_do",
        "loai": "he_so",
        "mo_ta": "Thạc sĩ chậm tiến độ: đóng HP tốt nghiệp chậm tiến độ = 50% HP học kỳ trễ hạn",
        "he_so": 0.5,
        "muc_hp": None,
        "don_vi_tinh": "",
        "doi_tuong": "Thạc sĩ quá thời gian thiết kế CTĐT",
        "nam_hoc": NAM_HOC,
    })

    # 8. Tiến sĩ
    policies.append({
        "id": "tien_si_khoa_2025_truoc",
        "loai": "muc_hp_co_dinh",
        "mo_ta": "HP tiến sĩ khóa ≤2025: 1.700.000 đ/TC (51.000.000 đ/năm học)",
        "he_so": None,
        "muc_hp": 1700000,
        "don_vi_tinh": "dong/tin_chi",
        "doi_tuong": "Tiến sĩ khóa ≤2025",
        "nam_hoc": NAM_HOC,
    })

    policies.append({
        "id": "tien_si_khoa_2026",
        "loai": "muc_hp_co_dinh",
        "mo_ta": "HP tiến sĩ khóa 2026: 1.876.000 đ/TC (56.300.000 đ/năm học), cố định theo khóa",
        "he_so": None,
        "muc_hp": 1876000,
        "don_vi_tinh": "dong/tin_chi",
        "doi_tuong": "Tiến sĩ khóa 2026",
        "nam_hoc": NAM_HOC,
    })

    policies.append({
        "id": "tien_si_cham_tien_do",
        "loai": "he_so",
        "mo_ta": "Tiến sĩ chậm tiến độ: đóng HP tốt nghiệp chậm tiến độ = 50% HP học kỳ trễ hạn",
        "he_so": 0.5,
        "muc_hp": None,
        "don_vi_tinh": "",
        "doi_tuong": "Tiến sĩ quá thời gian đào tạo",
        "nam_hoc": NAM_HOC,
    })

    # 9. Bổ sung kiến thức thạc sĩ
    policies.append({
        "id": "bo_sung_kien_thuc_thac_si",
        "loai": "muc_hp_co_dinh",
        "mo_ta": "HP bổ sung kiến thức dự thi tuyển sinh thạc sĩ: tối đa 695.000 đ/TC",
        "he_so": None,
        "muc_hp": 695000,
        "don_vi_tinh": "dong/tin_chi",
        "doi_tuong": "Học bổ sung kiến thức dự thi thạc sĩ",
        "nam_hoc": NAM_HOC,
    })

    # 10. Sinh viên nước ngoài
    policies.append({
        "id": "sv_nuoc_ngoai",
        "loai": "quy_dinh",
        "mo_ta": "Sinh viên, học viên và nghiên cứu sinh có quốc tịch nước ngoài: thực hiện theo quy định hiện hành của ĐHCT",
        "he_so": None,
        "muc_hp": None,
        "don_vi_tinh": "",
        "doi_tuong": "SV/HV/NCS quốc tịch nước ngoài",
        "nam_hoc": NAM_HOC,
    })

    logger.info("  Parsed policies: %d TuitionPolicy nodes", len(policies))
    return policies


def parse_exemption_basis(filepath: Path) -> List[Dict[str, Any]]:
    """Parse MucHocPhi_2526_MienGiam.md → list of ExemptionBasisRate dicts.

    Bao gồm:
    - Bảng 2.1: GDQP-AN (451.000 đ/TC)
    - Bảng 2.2: Các Khối ngành I, III, IV, V, VI, VII
    - Mục 4: Tiên tiến Khóa 47 trở về trước (335.000 đ/TC)
    """
    NAM_MIEN_GIAM = "2025-2026"
    rates: List[Dict[str, Any]] = []

    # 1. Bảng 2.1 Đại cương chung - GDQP-AN
    rates.append({
        "id": "exemption_basis_gdqp_an_2025_2026",
        "khoi": "GDQP_AN",
        "ten_khoi": "Học phần Giáo dục quốc phòng và An ninh (8 tín chỉ)",
        "muc_hp": 451000,
        "don_vi_tinh": "dong/tin_chi",
        "nam_hoc": NAM_MIEN_GIAM,
        "loai_ct": "dai_cuong_chung",
        "ghi_chu": "Mức miễn, giảm học phần Giáo dục quốc phòng và An ninh (8 tín chỉ)",
    })

    # 2. Bảng 2.2 Các khối ngành
    rates.append({
        "id": "exemption_basis_khoi_i_2025_2026",
        "khoi": "I",
        "ten_khoi": "Khối ngành I: Khoa học giáo dục và đào tạo giáo viên",
        "muc_hp": 451000,
        "don_vi_tinh": "dong/tin_chi",
        "nam_hoc": NAM_MIEN_GIAM,
        "loai_ct": "chuan",
        "ghi_chu": "Chỉ áp dụng cho sinh viên không hưởng chính sách theo Nghị định 116/2020/NĐ-CP",
    })
    rates.append({
        "id": "exemption_basis_khoi_iii_2025_2026",
        "khoi": "III",
        "ten_khoi": "Khối ngành III: Kinh doanh và quản lý, pháp luật",
        "muc_hp": 451000,
        "don_vi_tinh": "dong/tin_chi",
        "nam_hoc": NAM_MIEN_GIAM,
        "loai_ct": "chuan",
        "ghi_chu": "",
    })
    rates.append({
        "id": "exemption_basis_khoi_iv_2025_2026",
        "khoi": "IV",
        "ten_khoi": "Khối ngành IV: Khoa học sự sống, khoa học tự nhiên",
        "muc_hp": 487000,
        "don_vi_tinh": "dong/tin_chi",
        "nam_hoc": NAM_MIEN_GIAM,
        "loai_ct": "chuan",
        "ghi_chu": "",
    })
    rates.append({
        "id": "exemption_basis_khoi_v_2025_2026",
        "khoi": "V",
        "ten_khoi": "Khối ngành V: Toán và thống kê, máy tính và CN thông tin, CN kỹ thuật, kỹ thuật, sản xuất và chế biến, kiến trúc và xây dựng, nông lâm nghiệp và thủy sản, thú y",
        "muc_hp": 538000,
        "don_vi_tinh": "dong/tin_chi",
        "nam_hoc": NAM_MIEN_GIAM,
        "loai_ct": "chuan",
        "ghi_chu": "",
    })
    rates.append({
        "id": "exemption_basis_khoi_vi_2025_2026",
        "khoi": "VI",
        "ten_khoi": "Khối ngành VI: Các khối ngành sức khỏe khác",
        "muc_hp": 753000,
        "don_vi_tinh": "dong/tin_chi",
        "nam_hoc": NAM_MIEN_GIAM,
        "loai_ct": "chuan",
        "ghi_chu": "",
    })
    rates.append({
        "id": "exemption_basis_khoi_vii_2025_2026",
        "khoi": "VII",
        "ten_khoi": "Khối ngành VII: Nhân văn, khoa học xã hội và hành vi, báo chí và thông tin, dịch vụ xã hội, du lịch, khách sạn, thể dục thể thao, dịch vụ vận tải, môi trường và bảo vệ môi trường",
        "muc_hp": 479000,
        "don_vi_tinh": "dong/tin_chi",
        "nam_hoc": NAM_MIEN_GIAM,
        "loai_ct": "chuan",
        "ghi_chu": "",
    })

    # 3. Mục 4: Tiên tiến Khóa 47 trở về trước
    rates.append({
        "id": "exemption_basis_tien_tien_k47_2025_2026",
        "khoi": "TIEN_TIEN_K47",
        "ten_khoi": "Chương trình Tiên tiến Khóa 47 trở về trước",
        "muc_hp": 335000,
        "don_vi_tinh": "dong/tin_chi",
        "nam_hoc": NAM_MIEN_GIAM,
        "loai_ct": "tien_tien",
        "ghi_chu": "Khoá 47 trở về trước: 335.000 đ/tín chỉ. Khoá 48 trở đi: tính theo Khối ngành tương ứng.",
    })

    logger.info("  Parsed exemption basis: %d ExemptionBasisRate nodes", len(rates))
    return rates


# ─────────────────────────────────────────────────────────────────────────────
# CLC/TT → Program mapping
# ─────────────────────────────────────────────────────────────────────────────

# Map tên ngành CLC/TT → mã ngành (để link HAS_TUITION tới Program)
CLC_TT_NGANH_MAP = {
    "Công nghệ thông tin": "7480201C",
    "Kinh doanh quốc tế": "7340120C",
    "Công nghệ kỹ thuật hóa học": "7510401C",
    "Kỹ thuật điện": "7520201C",
    "Công nghệ thực phẩm": "7540101C",
    "Ngôn ngữ Anh": "7220201C",
    "Tài chính – Ngân hàng": "7340201C",
    "Tài chính - Ngân hàng": "7340201C",
    "Kỹ thuật xây dựng": "7580201C",
    "Quản trị kinh doanh": "7340101C",
    "QT DV Du lịch và Lữ hành": "7810103C",
    "Kỹ thuật phần mềm": "7480103C",
    "KT điều khiển và TĐH": "7520216C",
    "Hệ thống thông tin": "7480104C",
    "Mạng máy tính và truyền thông dữ liệu": "7480102C",
    "Thú y": "7640101C",
    "Bảo vệ thực vật": "7620112C",
    "Kỹ thuật cơ khí": "7520103C",
    # Tiên tiến
    "Nuôi trồng thủy sản": "7620301T",
    "Công nghệ sinh học": "7420201T",
}


# ─────────────────────────────────────────────────────────────────────────────
# Neo4j Ingestion
# ─────────────────────────────────────────────────────────────────────────────


def _get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def ingest_tuition_fees(fees: List[Dict[str, Any]]) -> int:
    """Ingest TuitionFee nodes + HAS_TUITION relationships.

    Returns count of nodes created/updated.
    """
    driver = _get_driver()
    count = 0

    with driver.session() as session:
        for fee in fees:
            # MERGE TuitionFee node
            session.run(
                """
                MERGE (tf:TuitionFee {id: $id})
                SET tf.ma_nganh = $ma_nganh,
                    tf.khoa = $khoa,
                    tf.nam_hoc = $nam_hoc,
                    tf.loai_ct = $loai_ct,
                    tf.don_vi_tinh = $don_vi_tinh,
                    tf.muc_hp = $muc_hp,
                    tf.ten_nganh = $ten_nganh,
                    tf.don_vi = $don_vi,
                    tf.khoi = $khoi
                """,
                **fee,
            )

            # Link to Program if mã ngành exists
            ma_nganh = fee["ma_nganh"]
            if ma_nganh and ma_nganh != "dai_cuong_chung":
                # Try exact match first, then without suffix
                session.run(
                    """
                    MATCH (p:Program)
                    WHERE p.code = $ma_nganh
                       OR p.code = $ma_nganh_base
                    WITH p LIMIT 1
                    MATCH (tf:TuitionFee {id: $fee_id})
                    MERGE (p)-[:HAS_TUITION]->(tf)
                    """,
                    ma_nganh=ma_nganh,
                    ma_nganh_base=re.sub(r"[HCT]$", "", ma_nganh),
                    fee_id=fee["id"],
                )

            count += 1

    driver.close()
    return count


def ingest_clc_tt_fees(fees: List[Dict[str, Any]]) -> int:
    """Ingest CLC/TT TuitionFee nodes — link via tên ngành mapping.

    Returns count of nodes created/updated.
    """
    driver = _get_driver()
    count = 0

    with driver.session() as session:
        for fee in fees:
            # MERGE TuitionFee node
            session.run(
                """
                MERGE (tf:TuitionFee {id: $id})
                SET tf.ma_nganh = $ma_nganh,
                    tf.khoa = $khoa,
                    tf.nam_hoc = $nam_hoc,
                    tf.loai_ct = $loai_ct,
                    tf.don_vi_tinh = $don_vi_tinh,
                    tf.muc_hp = $muc_hp,
                    tf.ten_nganh = $ten_nganh,
                    tf.don_vi = $don_vi,
                    tf.khoi = $khoi
                """,
                **fee,
            )

            # Link to Program via name mapping
            ten_nganh = fee["ten_nganh"]
            mapped_code = CLC_TT_NGANH_MAP.get(ten_nganh)
            if mapped_code:
                session.run(
                    """
                    MATCH (p:Program)
                    WHERE p.code = $code
                    WITH p LIMIT 1
                    MATCH (tf:TuitionFee {id: $fee_id})
                    MERGE (p)-[:HAS_TUITION]->(tf)
                    """,
                    code=mapped_code,
                    fee_id=fee["id"],
                )

            count += 1

    driver.close()
    return count


def ingest_tuition_policies(policies: List[Dict[str, Any]]) -> int:
    """Ingest TuitionPolicy nodes.

    Returns count of nodes created/updated.
    """
    driver = _get_driver()
    count = 0

    with driver.session() as session:
        for policy in policies:
            session.run(
                """
                MERGE (tp:TuitionPolicy {id: $id})
                SET tp.loai = $loai,
                    tp.mo_ta = $mo_ta,
                    tp.he_so = $he_so,
                    tp.muc_hp = $muc_hp,
                    tp.don_vi_tinh = $don_vi_tinh,
                    tp.doi_tuong = $doi_tuong,
                    tp.nam_hoc = $nam_hoc
                """,
                **policy,
            )
            count += 1

    driver.close()
    return count


def link_fees_to_policies():
    """Create GOVERNED_BY relationships between TuitionFee and TuitionPolicy."""
    driver = _get_driver()

    with driver.session() as session:
        # K51 chương trình chuẩn → policy ngoài giờ thiết kế K51
        session.run(
            """
            MATCH (tf:TuitionFee)
            WHERE tf.loai_ct = 'chuan' AND tf.khoa = 'K51_ve_truoc'
            MATCH (tp:TuitionPolicy {id: 'ngoai_gio_thiet_ke_k51'})
            MERGE (tf)-[:GOVERNED_BY]->(tp)
            """
        )

        # K52 chương trình chuẩn → policy ngoài giờ thiết kế K52
        session.run(
            """
            MATCH (tf:TuitionFee)
            WHERE tf.loai_ct = 'chuan' AND tf.khoa = 'K52'
            MATCH (tp:TuitionPolicy {id: 'ngoai_gio_thiet_ke_k52'})
            MERGE (tf)-[:GOVERNED_BY]->(tp)
            """
        )

        # CLC/TT K50 trở về trước → hệ số 1.0
        clc_khoas_truoc = ["K44", "K45", "K46", "K47", "K48", "K49", "K50"]
        for khoa in clc_khoas_truoc:
            session.run(
                """
                MATCH (tf:TuitionFee)
                WHERE tf.loai_ct IN ['clc', 'tien_tien'] AND tf.khoa = $khoa
                MATCH (tp:TuitionPolicy {id: 'ngoai_gio_clc_k50_truoc'})
                MERGE (tf)-[:GOVERNED_BY]->(tp)
                """,
                khoa=khoa,
            )

        # CLC/TT K51 trở về sau → hệ số 1.3
        for khoa in ["K51", "K52"]:
            session.run(
                """
                MATCH (tf:TuitionFee)
                WHERE tf.loai_ct IN ['clc', 'tien_tien'] AND tf.khoa = $khoa
                MATCH (tp:TuitionPolicy {id: 'ngoai_gio_clc_k51_sau'})
                MERGE (tf)-[:GOVERNED_BY]->(tp)
                """,
                khoa=khoa,
            )

        # K51 chuẩn → policy HP đại cương chung K51
        session.run(
            """
            MATCH (tf:TuitionFee)
            WHERE tf.loai_ct = 'chuan' AND tf.khoa = 'K51_ve_truoc'
            MATCH (tp:TuitionPolicy {id: 'dai_cuong_chung_k51'})
            MERGE (tf)-[:GOVERNED_BY]->(tp)
            """
        )

        # K52 chuẩn → policy HP đại cương chung K52
        session.run(
            """
            MATCH (tf:TuitionFee)
            WHERE tf.loai_ct = 'chuan' AND tf.khoa = 'K52'
            MATCH (tp:TuitionPolicy {id: 'dai_cuong_chung_k52'})
            MERGE (tf)-[:GOVERNED_BY]->(tp)
            """
        )

    driver.close()
    logger.info("  ✓ GOVERNED_BY relationships created")


def ingest_exemption_basis_rates(rates: List[Dict[str, Any]]) -> int:
    """Ingest ExemptionBasisRate nodes + HAS_EXEMPTION_BASIS relationships.

    Returns count of nodes created/updated.
    """
    driver = _get_driver()
    count = 0

    with driver.session() as session:
        for rate in rates:
            session.run(
                """
                MERGE (e:ExemptionBasisRate {id: $id})
                SET e.khoi = $khoi,
                    e.ten_khoi = $ten_khoi,
                    e.muc_hp = $muc_hp,
                    e.don_vi_tinh = $don_vi_tinh,
                    e.nam_hoc = $nam_hoc,
                    e.loai_ct = $loai_ct,
                    e.ghi_chu = $ghi_chu
                """,
                **rate,
            )
            count += 1

        # Link Program -> ExemptionBasisRate via TuitionFee khoi property
        khoi_map = {
            "Khối I": "I",
            "Khối 1": "I",
            "Khối III": "III",
            "Khối 3": "III",
            "Khối IV": "IV",
            "Khối 4": "IV",
            "Khối V": "V",
            "Khối 5": "V",
            "Khối VI": "VI",
            "Khối 6": "VI",
            "Khối VII": "VII",
            "Khối 7": "VII",
        }
        for tf_khoi, target_khoi in khoi_map.items():
            session.run(
                """
                MATCH (p:Program)-[:HAS_TUITION]->(tf:TuitionFee)
                WHERE tf.khoi = $tf_khoi
                WITH DISTINCT p
                MATCH (e:ExemptionBasisRate {khoi: $target_khoi, loai_ct: 'chuan'})
                MERGE (p)-[:HAS_EXEMPTION_BASIS]->(e)
                """,
                tf_khoi=tf_khoi,
                target_khoi=target_khoi,
            )

        # Fallback linking for programs without HAS_TUITION by code prefix regex
        prefix_map = [
            ("^714", "I"),
            ("^73[148]", "III"),
            ("^74[246]", "IV"),
            ("^7(48|51|52|54|58|62|64|84)", "V"),
            ("^772", "VI"),
            ("^7(21|22|32|76|81|85)", "VII"),
        ]
        for pattern, target_khoi in prefix_map:
            session.run(
                """
                MATCH (p:Program)
                WHERE p.code =~ $pattern AND NOT (p)-[:HAS_EXEMPTION_BASIS]->()
                MATCH (e:ExemptionBasisRate {khoi: $target_khoi, loai_ct: 'chuan'})
                MERGE (p)-[:HAS_EXEMPTION_BASIS]->(e)
                """,
                pattern=pattern,
                target_khoi=target_khoi,
            )

    driver.close()
    logger.info("  ✓ HAS_EXEMPTION_BASIS relationships created")
    return count


# ─────────────────────────────────────────────────────────────────────────────
# Public API — called from graph_service.py
# ─────────────────────────────────────────────────────────────────────────────


def run_tuition_ingest(data_dir: Path | None = None) -> bool:
    """Run full tuition ingest pipeline.

    Called by graph_service.ensure_data_loaded() or standalone.
    """
    data_dir = data_dir or MARKDOWN_DIR

    try:
        print(f"\n{'='*60}")
        print("Ingesting Tuition Fee Data")
        print("=" * 60)

        total = 0

        # 1. K51 trở về trước
        k51_file = data_dir / "MucHocPhi_DaiHocChinhQuy_Khoa51_VeTruoc.md"
        if k51_file.exists():
            fees = parse_tuition_k51(k51_file)
            count = ingest_tuition_fees(fees)
            print(f"  ✓ K51 trở về trước: {count} TuitionFee nodes")
            total += count
        else:
            print(f"  ⚠ File not found: {k51_file.name}")

        # 2. K52
        k52_file = data_dir / "MucHocPhi_DaiHocChinhQuy_Khoa52.md"
        if k52_file.exists():
            fees = parse_tuition_k52(k52_file)
            count = ingest_tuition_fees(fees)
            print(f"  ✓ K52: {count} TuitionFee nodes")
            total += count
        else:
            print(f"  ⚠ File not found: {k52_file.name}")

        # 3. CLC/Tiên tiến
        clc_file = data_dir / "MucHocPhi_ChatLuongCao_TienTien.md"
        if clc_file.exists():
            fees = parse_tuition_clc_tt(clc_file)
            count = ingest_clc_tt_fees(fees)
            print(f"  ✓ CLC/TT: {count} TuitionFee nodes")
            total += count
        else:
            print(f"  ⚠ File not found: {clc_file.name}")

        # 4. Quy định chung → TuitionPolicy
        policy_file = data_dir / "MucHocPhi_QuyDinhChung.md"
        if policy_file.exists():
            policies = parse_tuition_policies(policy_file)
            count = ingest_tuition_policies(policies)
            print(f"  ✓ Policies: {count} TuitionPolicy nodes")
        else:
            print(f"  ⚠ File not found: {policy_file.name}")

        # 5. Link fees → policies
        link_fees_to_policies()

        # 6. Cơ sở tính miễn giảm học phí → ExemptionBasisRate
        exemption_file = data_dir / "MucHocPhi_2526_MienGiam.md"
        if exemption_file.exists():
            exemption_rates = parse_exemption_basis(exemption_file)
            exemption_count = ingest_exemption_basis_rates(exemption_rates)
            print(f"  ✓ Exemption Basis: {exemption_count} ExemptionBasisRate nodes")
        else:
            print(f"  ⚠ File not found: {exemption_file.name}")

        print(f"\n{'='*60}")
        print(f"✅ Tuition ingest complete: {total} TuitionFee nodes total")
        print("=" * 60)
        return True

    except Exception as exc:
        logger.error("❌ Tuition ingest failed: %s", exc, exc_info=True)
        print(f"❌ Tuition ingest failed: {exc}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_tuition_ingest()
