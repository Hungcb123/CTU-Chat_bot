import re
import os
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
DATA_DIR = Path(__file__).parent.parent / "data"

# ─────────────────────────────────────────────────────────────────────────────
# Static mappings (không có trong MD, phải hard-code theo kiến thức miền)
# ─────────────────────────────────────────────────────────────────────────────

PEO_PLO_MAP = {
    "PEO1": ["PLO1", "PLO2", "PLO3"],
    "PEO2": ["PLO4", "PLO5", "PLO6", "PLO7", "PLO8"],
    "PEO3": ["PLO3", "PLO10"],
    "PEO4": ["PLO9", "PLO11"],
    "PEO5": ["PLO11", "PLO12"],
}

TRACK_COURSE_MAP = {
    "Trí tuệ nhân tạo": ["CT223H", "CT226H", "CT227H"],
    "Phần mềm nhúng và IoT": ["CT295H"],
    "Phân tích dữ liệu lớn": ["CT224H"],
    "Chung (chuyên sâu)": ["CT228H", "CT305H", "CT225H", "CT255H"],
}

JOB_POSITIONS = [
    "Kỹ sư phát triển / kiểm thử / phân tích / bảo trì phần mềm",
    "Trưởng nhóm lập trình / Trưởng dự án phần mềm",
    "Chủ doanh nghiệp sản xuất phần mềm",
    "Cán bộ nghiên cứu và ứng dụng CNTT",
    "Giảng viên CNTT (đại học, cao đẳng, trung cấp)",
]


# ─────────────────────────────────────────────────────────────────────────────
# Parser
# ─────────────────────────────────────────────────────────────────────────────

def parse_markdown(filepath: Path) -> dict:
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")

    # --- Parse YAML frontmatter ---
    metadata = {}
    in_frontmatter = False
    content_start = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                content_start = i + 1
                break
        if in_frontmatter and ":" in line:
            key, val = line.split(":", 1)
            metadata[key.strip()] = val.strip().strip('"')

    # --- Program node ---
    program = {
        "name": metadata.get("nganh_hoc", ""),
        "code": metadata.get("ma_nganh", ""),
        "level": metadata.get("trinh_do", ""),
        "unit": metadata.get("don_vi", ""),
        "year": int(metadata.get("nam_ban_hanh", 0)),
        "total_credits": 0,
        "duration": "",
        "degree_type": "",
        "training_forms": "",
    }

    total_credits_m = re.search(r"TỔNG CỘNG CHƯƠNG TRÌNH:\s*(\d+)\s*TC", text)
    if total_credits_m:
        program["total_credits"] = int(total_credits_m.group(1))

    duration_m = re.search(r"Thời gian đào tạo:\s*(.+)", text)
    if duration_m:
        program["duration"] = duration_m.group(1).strip()

    degree_m = re.search(r"Loại văn bằng:\s*(.+)", text)
    if degree_m:
        program["degree_type"] = degree_m.group(1).strip()

    # Mã ngành từ nội dung nếu frontmatter không có
    if not program["code"]:
        code_m = re.search(r"Mã ngành:\s*([\w]+)", text)
        if code_m:
            program["code"] = code_m.group(1).strip()

    training_m = re.search(r"Hình thức đào tạo:\s*(.+)", text)
    if training_m:
        program["training_forms"] = training_m.group(1).strip()

    # ─── Patterns ───
    # Block header:  ### Khối kiến thức Tiếng Anh tăng cường
    block_pattern = re.compile(r"^###\s+(.+?)$")

    # Block total credits line:  **Tổng cộng:** 17 TC (Bắt buộc: 17 TC; Tự chọn: 0 TC)
    block_credits_pattern = re.compile(
        r"\*\*Tổng cộng:\*\*\s*(\d+)\s*TC.*?Bắt buộc:\s*(\d+)\s*TC.*?Tự chọn:\s*(\d+)\s*TC"
    )

    # Course header:  * **Lập trình căn bản A (*)** (Mã số: CT054H)
    # Captures: name (possibly ending with (*)), code
    course_pattern = re.compile(
        r"^\*\s+\*\*(.+?)\*\*\s*\(Mã số:\s*([\w-]+)\)"
    )

    credit_pattern = re.compile(r"Số tín chỉ:\s*(\d+)\s*\((Bắt buộc|Tự chọn)\)")
    tiet_pattern = re.compile(r"Số tiết:\s*(\d+)\s*LT,\s*(\d+)\s*TH")
    prereq_pattern = re.compile(r"Học phần tiên quyết:\s*(.+)")
    parallel_pattern = re.compile(r"Học phần song hành:\s*(.+)")

    # PLO line:  - a. Mô tả... (PLO1)
    plo_line_pattern = re.compile(r"^\s*-\s+\w+\.\s+(.+?)\s+\(PLO(\d+)\)\s*$")
    # PEO line:  - a. Mô tả... (PEO1)
    peo_line_pattern = re.compile(r"^\s*-\s+\w+\.\s+(.+?)\s+\(PEO(\d+)\)\s*$")

    # ─── Iterate lines ───
    blocks = []
    courses = []
    plos = []
    peos = []
    current_block = None
    current_course = None

    content_lines = lines[content_start:]

    for line in content_lines:
        # Check block header (### ...)
        block_m = block_pattern.match(line)
        if block_m:
            block_raw = block_m.group(1).strip()
            # Skip non-block headings (## level handled by lower heading level)
            # Only treat as block if starts with "Khối" or is known curriculum block
            is_curriculum_block = (
                block_raw.startswith("Khối")
                or "kỹ năng mềm" in block_raw.lower()
            )
            if is_curriculum_block:
                current_block = {
                    "name": block_raw,
                    "total_credits": 0,
                    "tc_bat_buoc": 0,
                    "tc_tu_chon": 0,
                }
                blocks.append(current_block)
                current_course = None
            continue

        # Block credits line  **Tổng cộng:** ...
        if current_block is not None:
            bc_m = block_credits_pattern.search(line)
            if bc_m:
                current_block["total_credits"] = int(bc_m.group(1))
                current_block["tc_bat_buoc"] = int(bc_m.group(2))
                current_block["tc_tu_chon"] = int(bc_m.group(3))
                continue

        # PLO line
        plo_m = plo_line_pattern.match(line)
        if plo_m:
            plos.append({
                "id": f"PLO{plo_m.group(2)}",
                "description": plo_m.group(1).strip(),
            })
            continue

        # PEO line
        peo_m = peo_line_pattern.match(line)
        if peo_m:
            peos.append({
                "id": f"PEO{peo_m.group(2)}",
                "description": peo_m.group(1).strip(),
            })
            continue

        # Course header line
        course_m = course_pattern.match(line)
        if course_m and current_block is not None:
            raw_name = course_m.group(1).strip()
            # MD escapes (*) as (\*) — normalize first
            raw_name = raw_name.replace("(\\*)", "(*)").replace("\\*", "*")
            # Check dấu (*) — học phần điều kiện
            is_condition = raw_name.endswith("(*)")
            # Remove trailing (*) and any leftover backslashes
            clean_name = re.sub(r"\s*\(\\?\*\)\s*$", "", raw_name).strip()

            current_course = {
                "name": clean_name,
                "code": course_m.group(2).strip(),
                "block": current_block["name"],
                "credits": 0,
                "is_required": True,
                "so_tiet_lt": 0,
                "so_tiet_th": 0,
                "la_dieu_kien": is_condition,
                "prerequisites": [],
                "parallel": [],
            }
            courses.append(current_course)
            continue

        # Sub-fields of current course
        if current_course is not None:
            # Số tín chỉ: X (Bắt buộc|Tự chọn)
            cr_m = credit_pattern.search(line)
            if cr_m:
                current_course["credits"] = int(cr_m.group(1))
                current_course["is_required"] = (cr_m.group(2) == "Bắt buộc")

            # Số tiết: X LT, Y TH
            tiet_m = tiet_pattern.search(line)
            if tiet_m:
                current_course["so_tiet_lt"] = int(tiet_m.group(1))
                current_course["so_tiet_th"] = int(tiet_m.group(2))

            # Học phần tiên quyết
            pre_m = prereq_pattern.search(line)
            if pre_m:
                raw = pre_m.group(1).strip()
                # Some prereqs are "≥120TC" — not a course code, store as-is
                prereqs = [p.strip() for p in re.split(r"[,;]", raw) if p.strip()]
                current_course["prerequisites"] = prereqs

            # Học phần song hành
            par_m = parallel_pattern.search(line)
            if par_m:
                raw = par_m.group(1).strip()
                parallels = [p.strip() for p in re.split(r"[,;]", raw) if p.strip()]
                current_course["parallel"] = parallels

    return {
        "program": program,
        "blocks": blocks,
        "courses": courses,
        "plos": sorted(plos, key=lambda x: int(x["id"][3:])),
        "peos": sorted(peos, key=lambda x: int(x["id"][3:])),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Neo4j Ingestion
# ─────────────────────────────────────────────────────────────────────────────

def ingest_to_neo4j(data: dict):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")
        print("  ✓ Cleared existing graph")

        p = data["program"]

        # ── Program ──────────────────────────────────────────────────────────
        session.run(
            """
            MERGE (prog:Program {code: $code})
            SET prog.name = $name,
                prog.level = $level,
                prog.unit = $unit,
                prog.year = $year,
                prog.total_credits = $total_credits,
                prog.duration = $duration,
                prog.degree_type = $degree_type,
                prog.training_forms = $training_forms
            """,
            **p,
        )
        print(f"  ✓ Program: {p['name']} ({p['code']})")

        # ── Blocks ───────────────────────────────────────────────────────────
        for block in data["blocks"]:
            session.run(
                """
                MERGE (b:Block {name: $name})
                SET b.total_credits = $total_credits,
                    b.tc_bat_buoc = $tc_bat_buoc,
                    b.tc_tu_chon = $tc_tu_chon
                WITH b
                MATCH (prog:Program {code: $prog_code})
                MERGE (prog)-[:HAS_BLOCK]->(b)
                """,
                name=block["name"],
                total_credits=block["total_credits"],
                tc_bat_buoc=block["tc_bat_buoc"],
                tc_tu_chon=block["tc_tu_chon"],
                prog_code=p["code"],
            )
        print(f"  ✓ Blocks: {len(data['blocks'])}")

        # ── Courses ──────────────────────────────────────────────────────────
        course_codes = set()
        for course in data["courses"]:
            session.run(
                """
                MERGE (c:Course {code: $code})
                SET c.name = $name,
                    c.credits = $credits,
                    c.is_required = $is_required,
                    c.so_tiet_lt = $so_tiet_lt,
                    c.so_tiet_th = $so_tiet_th,
                    c.la_dieu_kien = $la_dieu_kien
                WITH c
                MATCH (b:Block {name: $block})
                MERGE (b)-[:CONTAINS]->(c)
                """,
                code=course["code"],
                name=course["name"],
                credits=course["credits"],
                is_required=course["is_required"],
                so_tiet_lt=course["so_tiet_lt"],
                so_tiet_th=course["so_tiet_th"],
                la_dieu_kien=course["la_dieu_kien"],
                block=course["block"],
            )
            course_codes.add(course["code"])
        print(f"  ✓ Courses: {len(data['courses'])}")

        # ── Prerequisites & Parallel ─────────────────────────────────────────
        req_count = 0
        par_count = 0
        for course in data["courses"]:
            for prereq in course["prerequisites"]:
                # Skip non-course-code prereqs like "≥120TC"
                if not re.match(r"^[A-Z]{2}\d+\w*$", prereq):
                    continue
                session.run(
                    """
                    MATCH (c:Course {code: $code})
                    MERGE (pre:Course {code: $prereq})
                    MERGE (c)-[:REQUIRES]->(pre)
                    """,
                    code=course["code"],
                    prereq=prereq,
                )
                req_count += 1

            for par in course["parallel"]:
                if not re.match(r"^[A-Z]{2}\d+\w*$", par):
                    continue
                session.run(
                    """
                    MATCH (c:Course {code: $code})
                    MERGE (p:Course {code: $parallel})
                    MERGE (c)-[:PARALLEL_WITH]->(p)
                    """,
                    code=course["code"],
                    parallel=par,
                )
                par_count += 1
        print(f"  ✓ REQUIRES relationships: {req_count}")
        print(f"  ✓ PARALLEL_WITH relationships: {par_count}")

        # ── PLOs ─────────────────────────────────────────────────────────────
        for plo in data["plos"]:
            session.run(
                """
                MERGE (plo:PLO {id: $id})
                SET plo.description = $description
                WITH plo
                MATCH (prog:Program {code: $prog_code})
                MERGE (prog)-[:HAS_PLO]->(plo)
                """,
                id=plo["id"],
                description=plo["description"],
                prog_code=p["code"],
            )
        print(f"  ✓ PLOs: {len(data['plos'])}")

        # ── PEOs ─────────────────────────────────────────────────────────────
        for peo in data["peos"]:
            session.run(
                """
                MERGE (peo:PEO {id: $id})
                SET peo.description = $description
                WITH peo
                MATCH (prog:Program {code: $prog_code})
                MERGE (prog)-[:HAS_PEO]->(peo)
                """,
                id=peo["id"],
                description=peo["description"],
                prog_code=p["code"],
            )
        print(f"  ✓ PEOs: {len(data['peos'])}")

        # ── PEO → PLO relationships (REALIZED_BY) ────────────────────────────
        rel_count = 0
        for peo_id, plo_ids in PEO_PLO_MAP.items():
            for plo_id in plo_ids:
                session.run(
                    """
                    MATCH (peo:PEO {id: $peo_id})
                    MATCH (plo:PLO {id: $plo_id})
                    MERGE (peo)-[:REALIZED_BY]->(plo)
                    """,
                    peo_id=peo_id,
                    plo_id=plo_id,
                )
                rel_count += 1
        print(f"  ✓ REALIZED_BY relationships (PEO→PLO): {rel_count}")

        # ── SpecializationTrack nodes ─────────────────────────────────────────
        for track_name, course_list in TRACK_COURSE_MAP.items():
            session.run(
                """
                MERGE (t:SpecializationTrack {name: $name})
                WITH t
                MATCH (prog:Program {code: $prog_code})
                MERGE (prog)-[:HAS_TRACK]->(t)
                """,
                name=track_name,
                prog_code=p["code"],
            )
            track_rel_count = 0
            for code in course_list:
                session.run(
                    """
                    MERGE (c:Course {code: $code})
                    MATCH (t:SpecializationTrack {name: $track_name})
                    MERGE (c)-[:BELONGS_TO_TRACK]->(t)
                    """,
                    code=code,
                    track_name=track_name,
                )
                track_rel_count += 1
        print(f"  ✓ SpecializationTrack nodes: {len(TRACK_COURSE_MAP)}")

        # ── JobPosition nodes ─────────────────────────────────────────────────
        for position in JOB_POSITIONS:
            session.run(
                """
                MERGE (j:JobPosition {name: $name})
                WITH j
                MATCH (prog:Program {code: $prog_code})
                MERGE (prog)-[:HAS_JOB_POSITION]->(j)
                """,
                name=position,
                prog_code=p["code"],
            )
        print(f"  ✓ JobPosition nodes: {len(JOB_POSITIONS)}")

    driver.close()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    md_files = list(DATA_DIR.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {DATA_DIR}")
    for md_file in md_files:
        print(f"\n{'='*60}")
        print(f"Ingesting: {md_file.name}")
        print("="*60)
        data = parse_markdown(md_file)
        print(f"  Parsed: {len(data['courses'])} courses, "
              f"{len(data['blocks'])} blocks, "
              f"{len(data['plos'])} PLOs, "
              f"{len(data['peos'])} PEOs")
        ingest_to_neo4j(data)
        print(f"\n✅ Done: {md_file.name}")