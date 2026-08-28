"""Neo4j Graph Service cho chương trình đào tạo.

Cung cấp các phương thức truy vấn Cypher phục vụ 6 LLM tools
(tra_cuu_nganh, so_sanh_nganh, tim_nganh, xem_chuoi_tien_quyet,
mon_chung_giua_nganh, tim_nganh_co_mon).

Lazy init: lần đầu khởi động kiểm tra Neo4j rỗng → tự động ingest.
"""

from __future__ import annotations

import logging
import os
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH_DATA_DIR = PROJECT_ROOT / "data" / "markdown_graph"


def _normalize(text: str) -> str:
    """Lower-case, remove diacritics, collapse whitespace."""
    decomposed = unicodedata.normalize("NFD", text)
    without_marks = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    lowered = without_marks.casefold().replace("đ", "d")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", lowered)).strip()


class AcademicGraphService:
    """Singleton service kết nối Neo4j và expose truy vấn Cypher."""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "password",
    ):
        self.uri = uri
        self.user = user
        self.password = password
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("✅ Neo4j driver initialized: %s", uri)

    def close(self) -> None:
        if self._driver:
            self._driver.close()
            logger.info("🔒 Neo4j connection closed.")

    def verify_connectivity(self) -> bool:
        try:
            self._driver.verify_connectivity()
            return True
        except Exception as exc:
            logger.error("Neo4j connectivity check failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Lazy init: kiểm tra và nạp dữ liệu nếu Neo4j rỗng
    # ------------------------------------------------------------------

    def ensure_data_loaded(self, data_dir: Path | None = None) -> bool:
        """Kiểm tra Neo4j có dữ liệu không, nếu rỗng thì tự động ingest."""
        data_dir = data_dir or DEFAULT_GRAPH_DATA_DIR
        with self._driver.session() as session:
            result = session.run("MATCH (p:Program) RETURN count(p) AS cnt")
            count = result.single()["cnt"]

        if count > 0:
            logger.info(
                "✅ Neo4j đã có %d Programs, bỏ qua ingest.", count
            )
        else:
            logger.info("⚠️ Neo4j rỗng, bắt đầu ingest từ %s...", data_dir)
            if not self._run_ingest(data_dir):
                return False

        # Check tuition data
        self._ensure_tuition_loaded()
        return True

    def _ensure_tuition_loaded(self) -> None:
        """Kiểm tra và tự động ingest TuitionFee nếu chưa có."""
        with self._driver.session() as session:
            result = session.run("MATCH (t:TuitionFee) RETURN count(t) AS cnt")
            count = result.single()["cnt"]

        if count > 0:
            logger.info("✅ Neo4j đã có %d TuitionFee, bỏ qua ingest học phí.", count)
            return

        logger.info("⚠️ Chưa có TuitionFee, bắt đầu ingest học phí...")
        try:
            import sys
            ingest_path = PROJECT_ROOT / "Graph_DB" / "app"
            sys.path.insert(0, str(ingest_path))
            from ingest_tuition import run_tuition_ingest
            run_tuition_ingest()
        except Exception as exc:
            logger.error("❌ Tuition ingest thất bại: %s", exc, exc_info=True)

    def _run_ingest(self, data_dir: Path) -> bool:
        """Gọi ingest script để parse markdown → Neo4j."""
        try:
            # Import ingest module từ Graph_DB
            import sys
            ingest_path = PROJECT_ROOT / "Graph_DB" / "app"
            sys.path.insert(0, str(ingest_path))
            from ingest import parse_markdown, ingest_to_neo4j, clear_graph

            md_files = sorted(data_dir.glob("*.md"))
            if not md_files:
                logger.error("Không tìm thấy file .md trong %s", data_dir)
                return False

            clear_graph()
            success = 0
            for md_file in md_files:
                data = parse_markdown(md_file)
                if data is None:
                    continue
                ingest_to_neo4j(data)
                success += 1

            logger.info("✅ Neo4j ingest hoàn tất: %d programs.", success)
            return success > 0
        except Exception as exc:
            logger.error("❌ Neo4j ingest thất bại: %s", exc, exc_info=True)
            return False

    # ------------------------------------------------------------------
    # 1. lookup_program — cho tra_cuu_nganh
    # ------------------------------------------------------------------

    def lookup_program(self, query: str) -> Optional[Dict[str, Any]]:
        """Tìm ngành theo tên (fuzzy) hoặc mã ngành. Trả kèm blocks, courses, PLOs."""
        norm = _normalize(query)
        with self._driver.session() as session:
            # Thử exact match trên mã ngành trước
            result = session.run(
                """
                MATCH (p:Program)
                WHERE p.code = $q
                RETURN p
                LIMIT 1
                """,
                q=query.strip(),
            )
            record = result.single()

            # Fuzzy match trên tên nếu không tìm thấy bằng mã
            if not record:
                result = session.run(
                    """
                    MATCH (p:Program)
                    WHERE toLower(p.name) CONTAINS $norm
                    RETURN p
                    ORDER BY size(p.name) ASC
                    LIMIT 1
                    """,
                    norm=norm,
                )
                record = result.single()

            # Fallback: token overlap search
            if not record:
                result = session.run(
                    "MATCH (p:Program) RETURN p.name AS name, p.code AS code"
                )
                best_score = 0
                best_code = None
                query_tokens = set(norm.split())
                for row in result:
                    prog_norm = _normalize(row["name"] or "")
                    prog_tokens = set(prog_norm.split())
                    overlap = len(query_tokens & prog_tokens)
                    if overlap > best_score:
                        best_score = overlap
                        best_code = row["code"]

                if best_code and best_score > 0:
                    result = session.run(
                        "MATCH (p:Program {code: $code}) RETURN p",
                        code=best_code,
                    )
                    record = result.single()

            if not record:
                return None

            prog = dict(record["p"])

            # Fetch blocks + courses
            blocks_result = session.run(
                """
                MATCH (p:Program {code: $code})-[:HAS_BLOCK]->(b:Block)
                OPTIONAL MATCH (b)-[:CONTAINS]->(c:Course)
                RETURN b.name AS block_name,
                       b.total_credits AS block_credits,
                       b.tc_bat_buoc AS tc_bat_buoc,
                       b.tc_tu_chon AS tc_tu_chon,
                       collect({
                           name: c.name,
                           code: c.code,
                           credits: c.credits,
                           is_required: c.is_required
                       }) AS courses
                ORDER BY block_name
                """,
                code=prog["code"],
            )
            blocks = []
            total_courses = 0
            for row in blocks_result:
                courses = [c for c in row["courses"] if c["code"] is not None]
                total_courses += len(courses)
                blocks.append({
                    "name": row["block_name"],
                    "total_credits": row["block_credits"],
                    "tc_bat_buoc": row["tc_bat_buoc"],
                    "tc_tu_chon": row["tc_tu_chon"],
                    "courses": courses,
                })

            # Fetch PLOs
            plo_result = session.run(
                """
                MATCH (p:Program {code: $code})-[:HAS_PLO]->(plo:PLO)
                RETURN plo.id AS id, plo.description AS description
                ORDER BY plo.id
                """,
                code=prog["code"],
            )
            plos = [{"id": r["id"], "description": r["description"]} for r in plo_result]

            return {
                "program": prog,
                "blocks": blocks,
                "total_courses": total_courses,
                "plos": plos,
            }

    # ------------------------------------------------------------------
    # 2. compare_programs — cho so_sanh_nganh
    # ------------------------------------------------------------------

    def compare_programs(self, query1: str, query2: str) -> Optional[Dict[str, Any]]:
        """So sánh 2 ngành: thông tin chung + môn chung/riêng qua graph."""
        p1 = self.lookup_program(query1)
        p2 = self.lookup_program(query2)

        if not p1 or not p2:
            return {
                "error": True,
                "not_found": (
                    [query1] if not p1 else []
                ) + (
                    [query2] if not p2 else []
                ),
            }

        code1 = p1["program"]["code"]
        code2 = p2["program"]["code"]

        with self._driver.session() as session:
            # Tìm môn chung và riêng qua Cypher
            result = session.run(
                """
                MATCH (p1:Program {code: $code1})-[:HAS_BLOCK]->(:Block)-[:CONTAINS]->(c1:Course)
                WITH p1, collect(DISTINCT c1) AS courses1
                MATCH (p2:Program {code: $code2})-[:HAS_BLOCK]->(:Block)-[:CONTAINS]->(c2:Course)
                WITH courses1, collect(DISTINCT c2) AS courses2
                WITH courses1, courses2,
                     [c IN courses1 WHERE c IN courses2] AS common,
                     [c IN courses1 WHERE NOT c IN courses2] AS only1,
                     [c IN courses2 WHERE NOT c IN courses1] AS only2
                RETURN size(common) AS common_count,
                       size(only1) AS only1_count,
                       size(only2) AS only2_count,
                       [c IN common | {name: c.name, code: c.code, credits: c.credits}][..20] AS common_courses,
                       size(courses1) AS total1,
                       size(courses2) AS total2
                """,
                code1=code1,
                code2=code2,
            )
            row = result.single()

        return {
            "program1": p1["program"],
            "program2": p2["program"],
            "total_courses_1": row["total1"] if row else 0,
            "total_courses_2": row["total2"] if row else 0,
            "common_count": row["common_count"] if row else 0,
            "only1_count": row["only1_count"] if row else 0,
            "only2_count": row["only2_count"] if row else 0,
            "common_courses": row["common_courses"] if row else [],
        }

    # ------------------------------------------------------------------
    # 3. search_programs — cho tim_nganh
    # ------------------------------------------------------------------

    def search_programs(self, criteria: str) -> List[Dict[str, Any]]:
        """Tìm ngành theo tiêu chí tự do: match trên tên ngành, đơn vị, môn học."""
        norm = _normalize(criteria)
        tokens = set(norm.split())

        with self._driver.session() as session:
            # Strategy 1: match program name or unit
            result = session.run(
                """
                MATCH (p:Program)
                WHERE toLower(p.name) CONTAINS $norm
                   OR toLower(p.unit) CONTAINS $norm
                RETURN p.code AS code, p.name AS name, p.unit AS unit,
                       p.total_credits AS total_credits, p.duration AS duration
                ORDER BY p.name
                LIMIT 15
                """,
                norm=norm,
            )
            matches = [dict(r) for r in result]

            # Strategy 2: nếu ít kết quả, thử match trên Course
            if len(matches) < 5:
                result = session.run(
                    """
                    MATCH (c:Course)
                    WHERE toLower(c.name) CONTAINS $norm
                    WITH c
                    MATCH (p:Program)-[:HAS_BLOCK]->(:Block)-[:CONTAINS]->(c)
                    RETURN DISTINCT p.code AS code, p.name AS name, p.unit AS unit,
                           p.total_credits AS total_credits, p.duration AS duration,
                           collect(DISTINCT c.name)[..3] AS matched_courses
                    ORDER BY p.name
                    LIMIT 10
                    """,
                    norm=norm,
                )
                course_matches = [dict(r) for r in result]
                existing_codes = {m["code"] for m in matches}
                for cm in course_matches:
                    if cm["code"] not in existing_codes:
                        matches.append(cm)

            # Strategy 3: token overlap fallback
            if not matches:
                result = session.run(
                    """
                    MATCH (p:Program)
                    RETURN p.code AS code, p.name AS name, p.unit AS unit,
                           p.total_credits AS total_credits, p.duration AS duration
                    """
                )
                scored = []
                for row in result:
                    prog_norm = _normalize(
                        f"{row['name'] or ''} {row['unit'] or ''}"
                    )
                    prog_tokens = set(prog_norm.split())
                    overlap = len(tokens & prog_tokens)
                    if overlap > 0:
                        scored.append((overlap, dict(row)))
                scored.sort(key=lambda x: x[0], reverse=True)
                matches = [item for _, item in scored[:10]]

        return matches

    # ------------------------------------------------------------------
    # 4. get_prerequisite_chain — cho xem_chuoi_tien_quyet
    # ------------------------------------------------------------------

    def get_prerequisite_chain(self, course_query: str) -> Optional[Dict[str, Any]]:
        """Trả chuỗi tiên quyết đầy đủ của một môn học (variable-length path)."""
        with self._driver.session() as session:
            # Tìm môn theo mã hoặc tên
            result = session.run(
                """
                MATCH (c:Course)
                WHERE c.code = $q OR toLower(c.name) CONTAINS toLower($q)
                RETURN c.code AS code, c.name AS name
                LIMIT 1
                """,
                q=course_query.strip(),
            )
            target = result.single()
            if not target:
                return None

            code = target["code"]
            name = target["name"]

            # Chuỗi tiên quyết (REQUIRES) — depth up to 10
            result = session.run(
                """
                MATCH path = (start:Course {code: $code})-[:REQUIRES*1..10]->(pre:Course)
                WITH nodes(path) AS chain
                UNWIND range(0, size(chain)-1) AS i
                WITH chain[i] AS node, i AS depth
                RETURN DISTINCT node.code AS code, node.name AS name,
                       node.credits AS credits, depth
                ORDER BY depth
                """,
                code=code,
            )
            prereq_chain = [
                {"code": r["code"], "name": r["name"], "credits": r["credits"], "depth": r["depth"]}
                for r in result
            ]

            # Chuỗi song hành (PARALLEL_WITH)
            result = session.run(
                """
                MATCH (c:Course {code: $code})-[:PARALLEL_WITH]->(par:Course)
                RETURN par.code AS code, par.name AS name, par.credits AS credits
                """,
                code=code,
            )
            parallel = [
                {"code": r["code"], "name": r["name"], "credits": r["credits"]}
                for r in result
            ]

            # Ngành nào chứa môn này
            result = session.run(
                """
                MATCH (p:Program)-[:HAS_BLOCK]->(:Block)-[:CONTAINS]->(c:Course {code: $code})
                RETURN DISTINCT p.name AS name, p.code AS code
                """,
                code=code,
            )
            programs = [{"name": r["name"], "code": r["code"]} for r in result]

            return {
                "course": {"code": code, "name": name},
                "prerequisite_chain": prereq_chain,
                "parallel_courses": parallel,
                "belongs_to_programs": programs,
            }

    # ------------------------------------------------------------------
    # 5. get_shared_courses — cho mon_chung_giua_nganh
    # ------------------------------------------------------------------

    def get_shared_courses(
        self, query1: str, query2: str
    ) -> Optional[Dict[str, Any]]:
        """Tìm danh sách môn chung giữa 2 ngành (chi tiết hơn compare_programs)."""
        p1 = self.lookup_program(query1)
        p2 = self.lookup_program(query2)

        if not p1 or not p2:
            return {
                "error": True,
                "not_found": (
                    [query1] if not p1 else []
                ) + (
                    [query2] if not p2 else []
                ),
            }

        code1 = p1["program"]["code"]
        code2 = p2["program"]["code"]

        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (p1:Program {code: $code1})-[:HAS_BLOCK]->(b1:Block)-[:CONTAINS]->(c:Course)
                WITH c, b1
                MATCH (p2:Program {code: $code2})-[:HAS_BLOCK]->(b2:Block)-[:CONTAINS]->(c)
                RETURN c.code AS code, c.name AS name, c.credits AS credits,
                       c.is_required AS is_required,
                       b1.name AS block_in_prog1, b2.name AS block_in_prog2
                ORDER BY c.name
                """,
                code1=code1,
                code2=code2,
            )
            shared = [
                {
                    "code": r["code"],
                    "name": r["name"],
                    "credits": r["credits"],
                    "is_required": r["is_required"],
                    "block_in_prog1": r["block_in_prog1"],
                    "block_in_prog2": r["block_in_prog2"],
                }
                for r in result
            ]

        total_credits = sum(c["credits"] for c in shared if c["credits"])
        return {
            "program1": {"name": p1["program"]["name"], "code": code1},
            "program2": {"name": p2["program"]["name"], "code": code2},
            "shared_count": len(shared),
            "shared_credits": total_credits,
            "shared_courses": shared,
        }

    # ------------------------------------------------------------------
    # 6. find_programs_by_course — cho tim_nganh_co_mon
    # ------------------------------------------------------------------

    def find_programs_by_course(self, course_query: str) -> List[Dict[str, Any]]:
        """Tìm tất cả ngành chứa một môn học (reverse graph traversal)."""
        with self._driver.session() as session:
            # Tìm course theo mã hoặc tên
            result = session.run(
                """
                MATCH (c:Course)
                WHERE c.code = $q OR toLower(c.name) CONTAINS toLower($q)
                WITH c
                MATCH (p:Program)-[:HAS_BLOCK]->(b:Block)-[:CONTAINS]->(c)
                RETURN c.code AS course_code, c.name AS course_name,
                       c.credits AS credits,
                       collect(DISTINCT {
                           prog_name: p.name,
                           prog_code: p.code,
                           block: b.name,
                           unit: p.unit
                       }) AS programs
                LIMIT 5
                """,
                q=course_query.strip(),
            )
            results = []
            for row in result:
                results.append({
                    "course_code": row["course_code"],
                    "course_name": row["course_name"],
                    "credits": row["credits"],
                    "programs": row["programs"],
                })

            return results

    # ------------------------------------------------------------------
    # 7. lookup_tuition — tra cứu học phí theo ngành + khóa
    # ------------------------------------------------------------------

    def lookup_tuition(
        self, query: str, khoa: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Tra cứu học phí của ngành theo tên/mã ngành, có thể lọc theo khóa."""
        norm = _normalize(query)

        with self._driver.session() as session:
            # Strategy 1: Tìm qua Program → HAS_TUITION → TuitionFee
            cypher = """
                MATCH (p:Program)-[:HAS_TUITION]->(tf:TuitionFee)
                WHERE p.code = $query
                   OR toLower(p.name) CONTAINS $norm
            """
            params: Dict[str, Any] = {"query": query.strip(), "norm": norm}

            if khoa:
                cypher += "    AND tf.khoa = $khoa\n"
                params["khoa"] = khoa.strip()

            cypher += """
                RETURN tf.id AS id, tf.ma_nganh AS ma_nganh, tf.khoa AS khoa,
                       tf.nam_hoc AS nam_hoc, tf.loai_ct AS loai_ct,
                       tf.don_vi_tinh AS don_vi_tinh, tf.muc_hp AS muc_hp,
                       tf.ten_nganh AS ten_nganh, p.name AS program_name,
                       p.code AS program_code
                ORDER BY tf.khoa, tf.don_vi_tinh
            """

            result = session.run(cypher, **params)
            matches = [dict(r) for r in result]

            # Strategy 2: Tìm trực tiếp trên TuitionFee (cho CLC/TT không link Program)
            if not matches:
                cypher2 = """
                    MATCH (tf:TuitionFee)
                    WHERE toLower(tf.ten_nganh) CONTAINS $norm
                """
                params2: Dict[str, Any] = {"norm": norm}

                if khoa:
                    cypher2 += "    AND tf.khoa = $khoa\n"
                    params2["khoa"] = khoa.strip()

                cypher2 += """
                    RETURN tf.id AS id, tf.ma_nganh AS ma_nganh, tf.khoa AS khoa,
                           tf.nam_hoc AS nam_hoc, tf.loai_ct AS loai_ct,
                           tf.don_vi_tinh AS don_vi_tinh, tf.muc_hp AS muc_hp,
                           tf.ten_nganh AS ten_nganh,
                           '' AS program_name, '' AS program_code
                    ORDER BY tf.khoa, tf.don_vi_tinh
                """
                result = session.run(cypher2, **params2)
                matches = [dict(r) for r in result]

            # Strategy 3: Token overlap fallback
            if not matches:
                result = session.run(
                    "MATCH (tf:TuitionFee) RETURN tf"
                )
                query_tokens = set(norm.split())
                scored = []
                for row in result:
                    tf = dict(row["tf"])
                    tf_norm = _normalize(tf.get("ten_nganh", ""))
                    tf_tokens = set(tf_norm.split())
                    overlap = len(query_tokens & tf_tokens)
                    if overlap > 0:
                        scored.append((overlap, tf))
                scored.sort(key=lambda x: x[0], reverse=True)
                matches = [item for _, item in scored[:20]]

        return matches

    # ------------------------------------------------------------------
    # 8. get_tuition_policies — lấy danh sách quy định học phí
    # ------------------------------------------------------------------

    def get_tuition_policies(
        self, doi_tuong: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lấy tất cả TuitionPolicy, có thể lọc theo đối tượng."""
        with self._driver.session() as session:
            if doi_tuong:
                norm = _normalize(doi_tuong)
                result = session.run(
                    """
                    MATCH (tp:TuitionPolicy)
                    WHERE toLower(tp.doi_tuong) CONTAINS $norm
                       OR toLower(tp.mo_ta) CONTAINS $norm
                    RETURN tp.id AS id, tp.loai AS loai, tp.mo_ta AS mo_ta,
                           tp.he_so AS he_so, tp.muc_hp AS muc_hp,
                           tp.don_vi_tinh AS don_vi_tinh,
                           tp.doi_tuong AS doi_tuong, tp.nam_hoc AS nam_hoc
                    ORDER BY tp.id
                    """,
                    norm=norm,
                )
            else:
                result = session.run(
                    """
                    MATCH (tp:TuitionPolicy)
                    RETURN tp.id AS id, tp.loai AS loai, tp.mo_ta AS mo_ta,
                           tp.he_so AS he_so, tp.muc_hp AS muc_hp,
                           tp.don_vi_tinh AS don_vi_tinh,
                           tp.doi_tuong AS doi_tuong, tp.nam_hoc AS nam_hoc
                    ORDER BY tp.id
                    """
                )

            return [dict(r) for r in result]
