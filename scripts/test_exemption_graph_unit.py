"""Unit test cho Parser, Tool và Logic tính toán Exemption Basis Graph."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "Graph_DB" / "app"))

from ingest_tuition import parse_exemption_basis
from app.tools.tuition_graph import (
    _format_exemption_results,
    tra_cuu_co_so_mien_giam_graph,
)
from app.tools.tuition import tinh_toan_hoc_phi


def test_unit_exemption_pipeline():
    print("=" * 70)
    print("BẮT ĐẦU UNIT TEST CHO PARSER & TOOLS MIỄN GIẢM HỌC PHÍ")
    print("=" * 70)

    # 1. Test Parser MucHocPhi_2526_MienGiam.md
    print("\n--- 1. Kiểm tra parse_exemption_basis() ---")
    md_path = ROOT / "data" / "markdown" / "MucHocPhi_2526_MienGiam.md"
    assert md_path.exists(), f"Không tìm thấy file {md_path}"

    rates = parse_exemption_basis(md_path)
    print(f"  ✓ Đã parse thành công {len(rates)} ExemptionBasisRate nodes:")
    for r in rates:
        print(f"    - [{r['khoi']}] {r['ten_khoi']}: {r['muc_hp']:,} {r['don_vi_tinh']}")

    assert len(rates) == 8, f"Kỳ vọng 8 nodes, nhận được {len(rates)}"

    # Kiểm tra từng khối ngành quan trọng
    rates_by_khoi = {r["khoi"]: r for r in rates}
    assert "I" in rates_by_khoi and rates_by_khoi["I"]["muc_hp"] == 451000
    assert "III" in rates_by_khoi and rates_by_khoi["III"]["muc_hp"] == 451000
    assert "IV" in rates_by_khoi and rates_by_khoi["IV"]["muc_hp"] == 487000
    assert "V" in rates_by_khoi and rates_by_khoi["V"]["muc_hp"] == 538000
    assert "VI" in rates_by_khoi and rates_by_khoi["VI"]["muc_hp"] == 753000
    assert "VII" in rates_by_khoi and rates_by_khoi["VII"]["muc_hp"] == 479000
    assert "GDQP_AN" in rates_by_khoi and rates_by_khoi["GDQP_AN"]["muc_hp"] == 451000
    assert "TIEN_TIEN_K47" in rates_by_khoi and rates_by_khoi["TIEN_TIEN_K47"]["muc_hp"] == 335000
    print("  ✓ Dữ liệu mức trần các Khối ngành chính xác 100%!")

    # 2. Test Format Output
    print("\n--- 2. Kiểm tra _format_exemption_results() ---")
    mock_results = [
        {
            "program_name": "Công nghệ thông tin",
            "program_code": "7480201",
            "ten_khoi": "Khối ngành V: Toán và CNTT, kỹ thuật...",
            "muc_hp": 538000,
            "don_vi_tinh": "dong/tin_chi",
            "ghi_chu": "",
        }
    ]
    formatted = _format_exemption_results(mock_results)
    print("  ✓ Output Formatted:")
    print("    " + formatted.replace("\n", "\n    "))
    assert "Công nghệ thông tin" in formatted
    assert "538.000" in formatted

    # 3. Test Tool Schemas
    print("\n--- 3. Kiểm tra Tool Schema ---")
    assert tra_cuu_co_so_mien_giam_graph.name == "tra_cuu_co_so_mien_giam_graph"
    assert "ten_nganh_hoac_khoi" in tra_cuu_co_so_mien_giam_graph.args
    print(f"  ✓ Tool {tra_cuu_co_so_mien_giam_graph.name} schema hợp lệ.")

    # 4. Test Tool tinh_toan_hoc_phi với nhiều tình huống
    print("\n--- 4. Kiểm tra Tool tinh_toan_hoc_phi() ---")
    # Tình huống 1: CNTT K52 (832k), trần Khối V (538k), giảm 70%
    # Giảm: 538k * 0.7 = 376.600 -> Thực đóng: 832k - 376.600 = 455.400
    out1 = tinh_toan_hoc_phi.invoke({
        "gia_hoc_phi_thuc_te": 832000,
        "muc_tran_mien_giam": 538000,
        "phan_tram_giam": 70,
    })
    print("  ✓ Tình huống 1 (Giảm 70% CNTT K52):")
    print("    " + out1.replace("\n", "\n    "))
    assert "455.400" in out1

    # Tình huống 2: Luật K51 (695k), trần Khối III (451k), giảm 100% (miễn 100%)
    # Giảm: 451k -> Thực đóng: 695k - 451k = 244.000
    out2 = tinh_toan_hoc_phi.invoke({
        "gia_hoc_phi_thuc_te": 695000,
        "muc_tran_mien_giam": 451000,
        "phan_tram_giam": 100,
    })
    print("  ✓ Tình huống 2 (Miễn 100% Luật K51):")
    print("    " + out2.replace("\n", "\n    "))
    assert "244.000" in out2

    # Tình huống 3: Giảm 50%
    out3 = tinh_toan_hoc_phi.invoke({
        "gia_hoc_phi_thuc_te": 695000,
        "muc_tran_mien_giam": 451000,
        "phan_tram_giam": 50,
    })
    print("  ✓ Tình huống 3 (Giảm 50% Luật K51):")
    print("    " + out3.replace("\n", "\n    "))
    assert "469.500" in out3

    print("\n" + "=" * 70)
    print("✅ TẤT CẢ CÁC UNIT TEST ĐÃ PASSED 100%!")
    print("=" * 70)


if __name__ == "__main__":
    test_unit_exemption_pipeline()
