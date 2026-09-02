"""Script kiểm tra tính đúng đắn của Knowledge Graph cho Dữ liệu Miễn Giảm Học Phí."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "Graph_DB" / "app"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from app.services.graph_service import AcademicGraphService
from app.tools.tuition_graph import (
    tra_cuu_co_so_mien_giam_graph,
    tra_cuu_hoc_phi_graph,
    set_tuition_graph_service,
)
from app.tools.tuition import tinh_toan_hoc_phi
from ingest_tuition import run_tuition_ingest


def test_exemption_graph():
    print("=" * 70)
    print("BẮT ĐẦU TEST KNOWLEDGE GRAPH CHO MIỄN GIẢM HỌC PHÍ")
    print("=" * 70)

    # 1. Chạy Ingestion
    print("\n--- 1. Chạy Ingest Tuition & Exemption Data ---")
    ingest_success = run_tuition_ingest()
    assert ingest_success, "Ingest thất bại!"

    # 2. Khởi tạo Graph Service
    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "password")

    service = AcademicGraphService(uri=neo4j_uri, user=neo4j_user, password=neo4j_password)
    assert service.verify_connectivity(), "Không thể kết nối Neo4j!"
    set_tuition_graph_service(service)

    # 3. Kiểm tra số lượng node và relationship
    print("\n--- 2. Kiểm tra Node và Relationship trong Neo4j ---")
    with service._driver.session() as session:
        res_eb = session.run("MATCH (e:ExemptionBasisRate) RETURN count(e) AS cnt, collect(e.khoi) AS khois")
        record_eb = res_eb.single()
        cnt_eb = record_eb["cnt"]
        khois_eb = record_eb["khois"]
        print(f"  ✓ Số node ExemptionBasisRate: {cnt_eb}")
        print(f"  ✓ Danh sách khối: {khois_eb}")
        assert cnt_eb >= 8, f"Thiếu node ExemptionBasisRate (mong muốn >= 8, thực tế {cnt_eb})"

        res_rel = session.run("MATCH (p:Program)-[:HAS_EXEMPTION_BASIS]->(e:ExemptionBasisRate) RETURN count(p) AS cnt")
        cnt_rel = res_rel.single()["cnt"]
        print(f"  ✓ Số Program liên kết HAS_EXEMPTION_BASIS: {cnt_rel}")
        assert cnt_rel > 0, "Không có Program nào được liên kết HAS_EXEMPTION_BASIS!"

    # 4. Kiểm tra Cypher Queries qua Service
    print("\n--- 3. Kiểm tra Cypher Query qua AcademicGraphService ---")

    # Case A: Tra cứu theo tên ngành "Công nghệ thông tin" (Khối V -> 538.000)
    cntt_res = service.lookup_exemption_basis(query="Công nghệ thông tin")
    print(f"  ✓ Tra cứu 'Công nghệ thông tin': {len(cntt_res)} kết quả")
    assert len(cntt_res) > 0, "Không tìm thấy mức trần cho ngành Công nghệ thông tin!"
    assert cntt_res[0]["muc_hp"] == 538000, f"Sai mức trần CNTT (mong muốn 538000, thực tế {cntt_res[0]['muc_hp']})"
    print(f"    -> Mức trần: {cntt_res[0]['muc_hp']:,} đ/TC ({cntt_res[0]['ten_khoi']})")

    # Case B: Tra cứu theo ngành Luật / Kinh tế (Khối III -> 451.000)
    luat_res = service.lookup_exemption_basis(query="Luật")
    print(f"  ✓ Tra cứu 'Luật': {len(luat_res)} kết quả")
    assert len(luat_res) > 0, "Không tìm thấy mức trần cho ngành Luật!"
    assert luat_res[0]["muc_hp"] == 451000, f"Sai mức trần Luật (mong muốn 451000, thực tế {luat_res[0]['muc_hp']})"
    print(f"    -> Mức trần: {luat_res[0]['muc_hp']:,} đ/TC ({luat_res[0]['ten_khoi']})")

    # Case C: Tra cứu trực tiếp theo Khối ngành "Khối IV" (487.000)
    khoi4_res = service.lookup_exemption_basis(khoi="Khối IV")
    print(f"  ✓ Tra cứu 'Khối IV': {len(khoi4_res)} kết quả")
    assert len(khoi4_res) > 0, "Không tìm thấy Khối IV!"
    assert khoi4_res[0]["muc_hp"] == 487000, f"Sai mức trần Khối IV (mong muốn 487000, thực tế {khoi4_res[0]['muc_hp']})"
    print(f"    -> Mức trần: {khoi4_res[0]['muc_hp']:,} đ/TC")

    # Case D: Tra cứu GDQP-AN (451.000)
    gdqp_res = service.lookup_exemption_basis(query="Giáo dục quốc phòng")
    print(f"  ✓ Tra cứu 'Giáo dục quốc phòng': {len(gdqp_res)} kết quả")
    assert len(gdqp_res) > 0, "Không tìm thấy GDQP!"
    assert gdqp_res[0]["muc_hp"] == 451000, f"Sai mức trần GDQP (mong muốn 451000, thực tế {gdqp_res[0]['muc_hp']})"
    print(f"    -> Mức trần: {gdqp_res[0]['muc_hp']:,} đ/TC")

    # Case E: Tra cứu Tiên tiến K47 (335.000)
    tt47_res = service.lookup_exemption_basis(query="Tiên tiến K47")
    print(f"  ✓ Tra cứu 'Tiên tiến K47': {len(tt47_res)} kết quả")
    assert len(tt47_res) > 0, "Không tìm thấy Tiên tiến K47!"
    assert tt47_res[0]["muc_hp"] == 335000, f"Sai mức trần Tiên tiến K47 (mong muốn 335000, thực tế {tt47_res[0]['muc_hp']})"
    print(f"    -> Mức trần: {tt47_res[0]['muc_hp']:,} đ/TC")

    # 5. Kiểm tra Tool LangChain
    print("\n--- 4. Kiểm tra Tool LangChain ---")
    tool_output = tra_cuu_co_so_mien_giam_graph.invoke({"ten_nganh_hoac_khoi": "Công nghệ thông tin"})
    print("  ✓ Output Tool tra_cuu_co_so_mien_giam_graph('Công nghệ thông tin'):")
    print("    " + tool_output.replace("\n", "\n    "))
    assert "538.000" in tool_output or "538000" in tool_output

    # 6. Kiểm tra Tool Tính toán
    print("\n--- 5. Kiểm tra Tool tinh_toan_hoc_phi ---")
    # Học phí thực tế CNTT K52: 832.000, Mức trần: 538.000, Giảm 70%
    # Tiền giảm: 538.000 * 0.7 = 376.600
    # Tiền thực đóng: 832.000 - 376.600 = 455.400
    calc_output = tinh_toan_hoc_phi.invoke({
        "gia_hoc_phi_thuc_te": 832000,
        "muc_tran_mien_giam": 538000,
        "phan_tram_giam": 70,
    })
    print("  ✓ Output Tool tinh_toan_hoc_phi:")
    print("    " + calc_output.replace("\n", "\n    "))
    assert "455.400" in calc_output

    print("\n" + "=" * 70)
    print("✅ TẤT CẢ CÁC BƯỚC TEST ĐÃ THÀNH CÔNG 100%!")
    print("=" * 70)

    service.close()


if __name__ == "__main__":
    test_exemption_graph()
