import re
import os
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
# Trỏ tới thư mục chứa 114 file CTĐT
DATA_DIR = Path(
    os.getenv(
        "GRAPH_DATA_DIR",
        str(Path(__file__).resolve().parent.parent.parent / "data" / "markdown_graph"),
    )
)

# ─────────────────────────────────────────────────────────────────────────────
# Static mappings — chỉ áp dụng cho ngành cụ thể (không có trong MD)
# ─────────────────────────────────────────────────────────────────────────────

# PEO→PLO mapping — key = mã ngành
PEO_PLO_MAP = {
    "7480103C": {
        "PEO1": ["PLO1", "PLO2", "PLO3"],
        "PEO2": ["PLO4", "PLO5", "PLO6", "PLO7", "PLO8"],
        "PEO3": ["PLO3", "PLO10"],
        "PEO4": ["PLO9", "PLO11"],
        "PEO5": ["PLO11", "PLO12"],
    },
}

# Specialization tracks — key = mã ngành
TRACK_COURSE_MAP = {
    "7480103C": {
        "Trí tuệ nhân tạo": ["CT223H", "CT226H", "CT227H"],
        "Phần mềm nhúng và IoT": ["CT295H"],
        "Phân tích dữ liệu lớn": ["CT224H"],
        "Chung (chuyên sâu)": ["CT228H", "CT305H", "CT225H", "CT255H"],
    },
}

# Job positions — key = mã ngành
JOB_POSITIONS_MAP = {
    "7480103C": [
        "Kỹ sư phát triển / kiểm thử / phân tích / bảo trì phần mềm",
        "Trưởng nhóm lập trình / Trưởng dự án phần mềm",
        "Chủ doanh nghiệp sản xuất phần mềm",
        "Cán bộ nghiên cứu và ứng dụng CNTT",
        "Giảng viên CNTT (đại học, cao đẳng, trung cấp)",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# Parser
# ─────────────────────────────────────────────────────────────────────────────


def parse_markdown(filepath: Path) -> dict | None:
    """Parse một file markdown CTĐT thành dict có cấu trúc.

    Returns None nếu file không phải CTĐT (ví dụ: quy chế học vụ).
    """
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

    # --- Kiểm tra loại tài liệu — bỏ qua file không phải CTĐT ---
    loai_tai_lieu = metadata.get("loai_tai_lieu", "")
    if loai_tai_lieu and "chương trình đào tạo" not in loai_tai_lieu.lower():
        return None

    # --- Program node ---
    # Ưu tiên mã ngành từ tên file (có suffix C cho CLC)
    # Format tên file: "66_7480201_CongNgheThongTin.md" hoặc "67_7480201C_CongNgheThongTin_CTCLC.md"
    filename_code = ""
    fname_m = re.match(r"\d+_(\d{7}C?)_", filepath.name)
    if fname_m:
        filename_code = fname_m.group(1)

    # Most CTĐT files store the Vietnamese program name in the body instead
    # of YAML frontmatter: ``- Ngành: **...** (English name)``.
    name_match = re.search(
        r"^\s*-\s*Ngành:\s*\*\*(.+?)\*\*",
        text,
        re.MULTILINE,
    )
    if name_match:
        body_name = name_match.group(1).strip()
    else:
        line_match = re.search(
            r"^\s*-\s*Ngành:\s*(.+?)\s*$",
            text,
            re.MULTILINE,
        )
        body_name = ""
        if line_match:
            body_name = re.sub(r"\*\*", "", line_match.group(1)).strip()
            body_name = body_name.split(" (", 1)[0].strip()

    program = {
        "name": metadata.get("nganh_hoc", "").strip() or body_name,
        "code": filename_code or metadata.get("ma_nganh", ""),
        "level": metadata.get("trinh_do", ""),
        "unit": metadata.get("don_vi", ""),
        "year": int(metadata.get("nam_ban_hanh", 0)),
        "total_credits": 0,
        "duration": "",
        "degree_type": "",
        "training_forms": "",
    }

    # Tổng tín chỉ — hỗ trợ cả "TỔNG CỘNG CHƯƠNG TRÌNH:" và "### Tổng cộng:"
    total_credits_m = re.search(
        r"(?:TỔNG CỘNG CHƯƠNG TRÌNH|^###?\s+Tổng cộng):\s*(\d+)\s*TC",
        text,
        re.MULTILINE,
    )
    if total_credits_m:
        program["total_credits"] = int(total_credits_m.group(1))

    duration_m = re.search(r"Thời gian đào tạo:\s*(.+)", text)
    if duration_m:
        program["duration"] = duration_m.group(1).strip()

    degree_m = re.search(r"Loại văn bằng:\s*(.+)", text)
    if degree_m:
        program["degree_type"] = degree_m.group(1).strip()

    # Mã ngành từ nội dung nếu vẫn chưa có — hỗ trợ **bold**
    if not program["code"]:
        code_m = re.search(r"Mã ngành:\s*\**\s*([\w]+)\**", text)
        if code_m:
            program["code"] = code_m.group(1).strip()

    training_m = re.search(r"Hình thức đào tạo:\s*(.+)", text)
    if training_m:
        program["training_forms"] = training_m.group(1).strip()

    # Non-CTĐT Markdown (for example quychehocvu.md) has no program identity.
    if not program["code"] or not program["name"]:
        return None

    # ─── Patterns ───

    # Block header:  ### Khối kiến thức Tiếng Anh tăng cường
    block_pattern = re.compile(r"^###\s+(.+?)$")

    # Block total credits:  **Tổng cộng:** 17 TC (Bắt buộc: 17 TC; Tự chọn: 0 TC)
    # Colon sau "Bắt buộc"/"Tự chọn" là optional
    block_credits_pattern = re.compile(
        r"\*\*Tổng cộng:\*\*\s*(\d+)\s*TC.*?"
        r"Bắt buộc:?\s*(\d+)\s*TC.*?"
        r"Tự chọn:?\s*(\d+)\s*TC"
    )

    # Course header:  * **Lập trình căn bản A (*)** (Mã số: CT054H)
    course_pattern = re.compile(
        r"^\*\s+\*\*(.+?)\*\*\s*\(Mã số:\s*([\w-]+)\)"
    )

    # Số tín chỉ — loại (Bắt buộc/Tự chọn) giờ là optional
    credit_pattern = re.compile(
        r"Số tín chỉ:\s*(\d+)(?:\s*\((Bắt buộc|Tự chọn)\))?"
    )

    # Số tiết — tách riêng LT và TH để xử lý linh hoạt
    tiet_lt_pattern = re.compile(r"(\d+)\s*LT")
    tiet_th_pattern = re.compile(r"(\d+)\s*TH")

    prereq_pattern = re.compile(r"Học phần tiên quyết:\s*(.+)")
    parallel_pattern = re.compile(r"Học phần song hành:\s*(.+)")

    # PLO/PEO line — cho phép khoảng trắng giữa PEO/PLO và số
    # Ví dụ: (PLO1), (PLO 1), (PEO 2), (PEO2)
    # Cũng cho phép dấu ; hoặc . ở cuối dòng
    plo_line_pattern = re.compile(
        r"^\s*-\s+\w+\.\s+(.+?)\s*\(PLO\s*(\d+)\)\s*[;.]*\s*$"
    )
    peo_line_pattern = re.compile(
        r"^\s*-\s+\w+\.\s+(.+?)\s*\(PEO\s*(\d+)\)\s*[;.]*\s*$"
    )

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
            # Skip non-block headings
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

        # PLO line (có id trong ngoặc)
        plo_m = plo_line_pattern.match(line)
        if plo_m:
            plos.append({
                "id": f"PLO{plo_m.group(2)}",
                "description": plo_m.group(1).strip(),
            })
            continue

        # PEO line (có id trong ngoặc)
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
            # MD escapes (*) as (\*) — normalize
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
            # Số tín chỉ: X (optional: Bắt buộc|Tự chọn)
            cr_m = credit_pattern.search(line)
            if cr_m:
                current_course["credits"] = int(cr_m.group(1))
                if cr_m.group(2):
                    current_course["is_required"] = cr_m.group(2) == "Bắt buộc"
                # Nếu không ghi loại → giữ default is_required=True

            # Số tiết — hỗ trợ chỉ LT, chỉ TH, hoặc cả hai
            if "Số tiết:" in line:
                lt_m = tiet_lt_pattern.search(line)
                th_m = tiet_th_pattern.search(line)
                if lt_m:
                    current_course["so_tiet_lt"] = int(lt_m.group(1))
                if th_m:
                    current_course["so_tiet_th"] = int(th_m.group(1))

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

    # ─── Fallback: PEO parsing cho ngành không ghi id (PEOx) ───
    if not peos:
        in_peo_section = False
        peo_counter = 0
        item_pattern = re.compile(r"^\s*-\s+\w+\.\s+(.+)")
        for line in content_lines:
            # Vào section 2.2 Mục tiêu đào tạo cụ thể
            if re.match(r"^###\s+2\.2\b", line):
                in_peo_section = True
                continue
            # Thoát khi gặp heading mới (## hoặc ### khác section)
            if in_peo_section and re.match(r"^#{2,3}\s+(?!2\.2)", line):
                break
            if in_peo_section:
                m = item_pattern.match(line)
                if m:
                    peo_counter += 1
                    desc = m.group(1).strip().rstrip(";.")
                    peos.append({
                        "id": f"PEO{peo_counter}",
                        "description": desc,
                    })

    # ─── Fallback: PLO parsing cho ngành không ghi id (PLOx) ───
    if not plos:
        in_plo_section = False
        plo_counter = 0
        item_pattern = re.compile(r"^\s*-\s+(?:\w+\.\s+)?(.+)")
        for line in content_lines:
            # Vào section 3. Chuẩn đầu ra
            if re.match(r"^##\s+3\.\s+Chuẩn đầu ra", line):
                in_plo_section = True
                continue
            # Thoát khi gặp section 4
            if in_plo_section and re.match(r"^##\s+4\.", line):
                break
            # Bỏ qua heading con (###, ####) — chúng chỉ là label
            if in_plo_section and re.match(r"^#{3,4}\s+", line):
                continue
            # Bỏ qua dòng trống hoặc paragraph (không bắt đầu bằng -)
            if in_plo_section:
                m = item_pattern.match(line)
                if m:
                    plo_counter += 1
                    desc = m.group(1).strip().rstrip(";.")
                    plos.append({
                        "id": f"PLO{plo_counter}",
                        "description": desc,
                    })

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


def clear_graph():
    """Xóa toàn bộ graph — gọi MỘT LẦN trước khi ingest tất cả file."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    driver.close()
    print("✓ Cleared existing graph")


def ingest_to_neo4j(data: dict):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
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
        # MERGE key bao gồm prog_code để tránh xung đột giữa các ngành
        for block in data["blocks"]:
            session.run(
                """
                MERGE (b:Block {name: $name, prog_code: $prog_code})
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
        # Course MERGE trên code duy nhất — cùng một môn có thể thuộc nhiều ngành
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
                MATCH (b:Block {name: $block, prog_code: $prog_code})
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
                prog_code=p["code"],
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
        # PLO key bao gồm prog_code — PLO1 của CNTT ≠ PLO1 của KHMT
        for plo in data["plos"]:
            session.run(
                """
                MERGE (plo:PLO {id: $id, prog_code: $prog_code})
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
                MERGE (peo:PEO {id: $id, prog_code: $prog_code})
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

        # ── PEO → PLO relationships (REALIZED_BY) — chỉ cho ngành có mapping ─
        peo_plo = PEO_PLO_MAP.get(p["code"], {})
        if peo_plo:
            rel_count = 0
            for peo_id, plo_ids in peo_plo.items():
                for plo_id in plo_ids:
                    session.run(
                        """
                        MATCH (peo:PEO {id: $peo_id, prog_code: $prog_code})
                        MATCH (plo:PLO {id: $plo_id, prog_code: $prog_code})
                        MERGE (peo)-[:REALIZED_BY]->(plo)
                        """,
                        peo_id=peo_id,
                        plo_id=plo_id,
                        prog_code=p["code"],
                    )
                    rel_count += 1
            print(f"  ✓ REALIZED_BY relationships (PEO→PLO): {rel_count}")

        # ── SpecializationTrack — chỉ cho ngành có mapping ────────────────────
        tracks = TRACK_COURSE_MAP.get(p["code"], {})
        if tracks:
            for track_name, course_list in tracks.items():
                session.run(
                    """
                    MERGE (t:SpecializationTrack {name: $name, prog_code: $prog_code})
                    WITH t
                    MATCH (prog:Program {code: $prog_code})
                    MERGE (prog)-[:HAS_TRACK]->(t)
                    """,
                    name=track_name,
                    prog_code=p["code"],
                )
                for code in course_list:
                    session.run(
                        """
                        MERGE (c:Course {code: $code})
                        WITH c
                        MATCH (t:SpecializationTrack {name: $track_name, prog_code: $prog_code})
                        MERGE (c)-[:BELONGS_TO_TRACK]->(t)
                        """,
                        code=code,
                        track_name=track_name,
                        prog_code=p["code"],
                    )
            print(f"  ✓ SpecializationTrack nodes: {len(tracks)}")

        # ── JobPosition — chỉ cho ngành có mapping ────────────────────────────
        positions = JOB_POSITIONS_MAP.get(p["code"], [])
        if positions:
            for position in positions:
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
            print(f"  ✓ JobPosition nodes: {len(positions)}")

    driver.close()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    md_files = sorted(DATA_DIR.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {DATA_DIR}")
        exit(1)

    print(f"Found {len(md_files)} markdown files in {DATA_DIR}")

    # Xóa graph MỘT LẦN trước khi ingest tất cả file
    clear_graph()

    success = 0
    skipped = 0
    for md_file in md_files:
        print(f"\n{'='*60}")
        print(f"Processing: {md_file.name}")
        print("=" * 60)

        data = parse_markdown(md_file)
        if data is None:
            print("  ⏭ Skipped (not a CTĐT file)")
            skipped += 1
            continue

        print(
            f"  Parsed: {len(data['courses'])} courses, "
            f"{len(data['blocks'])} blocks, "
            f"{len(data['plos'])} PLOs, "
            f"{len(data['peos'])} PEOs"
        )
        ingest_to_neo4j(data)
        success += 1
        print(f"\n✅ Done: {md_file.name}")

    print(f"\n{'='*60}")
    print(f"Summary: {success} programs ingested, {skipped} files skipped")
    print("=" * 60)
