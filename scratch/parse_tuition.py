import json
import re
import uuid
import os

records = []
rules = []
issues = []
used_ids = set()

def get_id():
    while True:
        new_id = str(uuid.uuid4())
        if new_id not in used_ids:
            used_ids.add(new_id)
            return new_id

def add_record(**kwargs):
    record = {
        "id": get_id(),
        "fee_kind": "actual_tuition",
        "academic_year": "2026-2027",
        "education_level": None,
        "study_mode": None,
        "program_type": None,
        "cohort_min": None,
        "cohort_max": None,
        "entity_type": None,
        "major_code": None,
        "major_name": None,
        "course_name": None,
        "knowledge_scope": None,
        "rate_type": None,
        "amount_vnd": None,
        "effective_semester": None,
        "source": None,
        "source_section": None,
        "source_table": None
    }
    record.update(kwargs)
    records.append(record)

def add_rule(**kwargs):
    rule = {
        "id": get_id(),
        "rule_type": None,
        "value": None,
        "description": None,
        "education_level": None,
        "study_mode": None,
        "program_type": None,
        "cohort_min": None,
        "cohort_max": None,
        "source": None,
        "source_section": None
    }
    rule.update(kwargs)
    rules.append(rule)

def add_issue(**kwargs):
    issue = {
        "source": None,
        "location": None,
        "description": None
    }
    issue.update(kwargs)
    issues.append(issue)

def parse_int(s):
    if not s or not str(s).strip(): return None
    s = str(s).replace(".", "").replace(",", "").strip()
    try:
        return int(s)
    except:
        return None

def parse_float(s):
    if not s or not str(s).strip(): return None
    s = str(s).replace(",", ".").strip()
    try:
        return float(s)
    except:
        return None

# 1. MucHocPhi_ChatLuongCao_TienTien.md
with open(r"d:\Project\Chatbot\data\markdown\MucHocPhi_ChatLuongCao_TienTien.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

current_section = ""
current_program = ""
current_table = []
headers = []
for line in lines:
    line = line.strip()
    if line.startswith("## I."):
        current_section = "I. Học phí cố định theo khóa học (triệu đồng/năm học)"
    elif line.startswith("## II."):
        current_section = "II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ)"
    elif line.startswith("### "):
        current_program = line.replace("### ", "").strip()
    elif line.startswith("**Mức học phí của khối kiến thức đại cương chung"):
        current_program = "Đại cương chung"
    elif line.startswith("|") and "---" not in line:
        parts = [p.strip() for p in line.split("|")][1:-1]
        if "Ngành" in parts or "Khóa" in parts or "Đồng/tín chỉ" in parts:
            if "Ngành" in parts:
                headers = parts
            elif "Khóa" in parts:
                headers = parts
            elif "Đồng/tín chỉ" in parts:
                # Dai cuong chung table
                for i, col in enumerate(headers[1:], 1):
                    val = parse_int(parts[i])
                    if val is not None:
                        k = int(col.replace("K", ""))
                        add_record(
                            education_level="undergraduate",
                            study_mode="full_time",
                            program_type="high_quality", # Rule says "chương trình CLC/Tiên tiến", wait assertion: "Đại cương chung K49 của chương trình CLC/Tiên tiến phải có: 441.000 đồng/tín chỉ". I'll add for both CLC and TT
                            cohort_min=k, cohort_max=k,
                            entity_type="all_students", major_code=None, major_name=None, course_name=None,
                            knowledge_scope="general_common", rate_type="per_credit", amount_vnd=val,
                            source="MucHocPhi_ChatLuongCao_TienTien.md", source_section=current_section, source_table="Khối kiến thức đại cương chung"
                        )
                        add_record(
                            education_level="undergraduate",
                            study_mode="full_time",
                            program_type="advanced", 
                            cohort_min=k, cohort_max=k,
                            entity_type="all_students", major_code=None, major_name=None, course_name=None,
                            knowledge_scope="general_common", rate_type="per_credit", amount_vnd=val,
                            source="MucHocPhi_ChatLuongCao_TienTien.md", source_section=current_section, source_table="Khối kiến thức đại cương chung"
                        )
        else:
            # Data row
            if not headers: continue
            if headers[1] == "Ngành":
                major_name = parts[1]
                for i, col in enumerate(headers[2:], 2):
                    if i < len(parts):
                        val_str = parts[i]
                        if current_section == "I. Học phí cố định theo khóa học (triệu đồng/năm học)":
                            val = parse_int(val_str)
                            if val:
                                amount = val * 1000000
                                p_type = "high_quality" if "Chất lượng cao" in current_program else "advanced"
                                k = int(col.replace("K", ""))
                                add_record(
                                    education_level="undergraduate", study_mode="full_time",
                                    program_type=p_type, cohort_min=k, cohort_max=k,
                                    entity_type="major", major_code=None, major_name=major_name, course_name=None,
                                    knowledge_scope="major", rate_type="per_academic_year", amount_vnd=amount,
                                    source="MucHocPhi_ChatLuongCao_TienTien.md", source_section=current_section, source_table=current_program
                                )
                        elif current_section == "II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ)":
                            val = parse_int(val_str)
                            if val:
                                p_type = "high_quality" if "Chất lượng cao" in current_program else "advanced"
                                k = int(col.replace("K", ""))
                                add_record(
                                    education_level="undergraduate", study_mode="full_time",
                                    program_type=p_type, cohort_min=k, cohort_max=k,
                                    entity_type="major", major_code=None, major_name=major_name, course_name=None,
                                    knowledge_scope="major", rate_type="per_credit", amount_vnd=val,
                                    source="MucHocPhi_ChatLuongCao_TienTien.md", source_section=current_section, source_table=current_program
                                )


# 2. MucHocPhi_DaiHocChinhQuy_Khoa51_VeTruoc.md
with open(r"d:\Project\Chatbot\data\markdown\MucHocPhi_DaiHocChinhQuy_Khoa51_VeTruoc.md", "r", encoding="utf-8") as f:
    lines = f.readlines()
for line in lines:
    line = line.strip()
    if line.startswith("|") and "---" not in line and "Mã ngành" not in line:
        parts = [p.strip() for p in line.split("|")][1:-1]
        if len(parts) >= 7:
            major_code = parts[1]
            major_name = parts[4]
            amount = parse_int(parts[6])
            if amount:
                add_record(
                    education_level="undergraduate", study_mode="full_time",
                    program_type="standard", cohort_min=None, cohort_max=51,
                    entity_type="major", major_code=major_code, major_name=major_name, course_name=None,
                    knowledge_scope="major", rate_type="per_credit", amount_vnd=amount,
                    source="MucHocPhi_DaiHocChinhQuy_Khoa51_VeTruoc.md", source_section="Mức học phí theo tín chỉ", source_table="Bảng học phí đại trà Khóa 51 trở về trước"
                )

# 3. MucHocPhi_DaiHocChinhQuy_Khoa52.md
with open(r"d:\Project\Chatbot\data\markdown\MucHocPhi_DaiHocChinhQuy_Khoa52.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

add_record(
    education_level="undergraduate", study_mode="full_time",
    program_type="standard", cohort_min=52, cohort_max=52,
    entity_type="all_students", major_code=None, major_name=None, course_name=None,
    knowledge_scope="general_common", rate_type="per_credit", amount_vnd=695000,
    source="MucHocPhi_DaiHocChinhQuy_Khoa52.md", source_section="Lưu ý", source_table="Khối kiến thức đại cương chung K52"
)

for line in lines:
    line = line.strip()
    if line.startswith("|") and "---" not in line and "Mã ngành" not in line:
        parts = [p.strip() for p in line.split("|")][1:-1]
        if len(parts) >= 8:
            major_code = parts[1]
            major_name = parts[4]
            amount_course = parse_float(parts[6])
            amount_credit = parse_int(parts[7])
            if amount_course:
                add_record(
                    education_level="undergraduate", study_mode="full_time",
                    program_type="standard", cohort_min=52, cohort_max=52,
                    entity_type="major", major_code=major_code, major_name=major_name, course_name=None,
                    knowledge_scope="major", rate_type="per_full_course", amount_vnd=int(amount_course * 1000000),
                    source="MucHocPhi_DaiHocChinhQuy_Khoa52.md", source_section="Mức học phí theo tín chỉ", source_table="Bảng học phí đại trà Khóa 52"
                )
            if amount_credit:
                add_record(
                    education_level="undergraduate", study_mode="full_time",
                    program_type="standard", cohort_min=52, cohort_max=52,
                    entity_type="major", major_code=major_code, major_name=major_name, course_name=None,
                    knowledge_scope="major", rate_type="per_credit", amount_vnd=amount_credit,
                    source="MucHocPhi_DaiHocChinhQuy_Khoa52.md", source_section="Mức học phí theo tín chỉ", source_table="Bảng học phí đại trà Khóa 52"
                )

# 4. MucHocPhi_QuyDinhChung.md
with open(r"d:\Project\Chatbot\data\markdown\MucHocPhi_QuyDinhChung.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

in_table_1_1_a = False
for line in lines:
    line = line.strip()
    if line.startswith("#### a) Mức học phí khối kiến thức đại cương chung"):
        in_table_1_1_a = True
    elif in_table_1_1_a and line.startswith("#### "):
        in_table_1_1_a = False
    elif in_table_1_1_a and line.startswith("|") and "---" not in line and "Học phần" not in line:
        parts = [p.strip() for p in line.split("|")][1:-1]
        if len(parts) >= 4:
            course_name = parts[1]
            amount = parse_int(parts[3])
            if amount:
                add_record(
                    education_level="undergraduate", study_mode="full_time",
                    program_type="standard", cohort_min=None, cohort_max=51,
                    entity_type="course", major_code=None, major_name=None, course_name=course_name,
                    knowledge_scope="general_common", rate_type="per_credit", amount_vnd=amount,
                    source="MucHocPhi_QuyDinhChung.md", source_section="1.1 Đối với Khóa 51 trở về trước", source_table="Mức học phí khối kiến thức đại cương chung"
                )

# Rules processing
add_rule(
    rule_type="multiplier", value=1.3, description="Học ngoài thời gian thiết kế của chương trình đào tạo ngành thứ nhất",
    education_level="undergraduate", study_mode="full_time", program_type="standard", cohort_min=None, cohort_max=51,
    source="MucHocPhi_QuyDinhChung.md", source_section="1.1 Đối với Khóa 51 trở về trước"
)
add_rule(
    rule_type="multiplier", value=1.3, description="Học ngoài thời gian thiết kế của chương trình đào tạo ngành thứ nhất",
    education_level="undergraduate", study_mode="full_time", program_type="standard", cohort_min=52, cohort_max=52,
    source="MucHocPhi_QuyDinhChung.md", source_section="1.2 Đối với Khóa 52"
)
add_rule(
    rule_type="multiplier", value=1.0, description="Học ngoài thời gian thiết kế của chương trình đào tạo",
    education_level="undergraduate", study_mode="full_time", program_type="high_quality", cohort_min=None, cohort_max=50,
    source="MucHocPhi_QuyDinhChung.md", source_section="2. Đại học hình thức chính quy chương trình đào tạo tiên tiến, chương trình đào tạo chất lượng cao"
)
add_rule(
    rule_type="multiplier", value=1.0, description="Học ngoài thời gian thiết kế của chương trình đào tạo",
    education_level="undergraduate", study_mode="full_time", program_type="advanced", cohort_min=None, cohort_max=50,
    source="MucHocPhi_QuyDinhChung.md", source_section="2. Đại học hình thức chính quy chương trình đào tạo tiên tiến, chương trình đào tạo chất lượng cao"
)
add_rule(
    rule_type="multiplier", value=1.3, description="Học ngoài thời gian thiết kế của chương trình đào tạo",
    education_level="undergraduate", study_mode="full_time", program_type="high_quality", cohort_min=51, cohort_max=None,
    source="MucHocPhi_QuyDinhChung.md", source_section="2. Đại học hình thức chính quy chương trình đào tạo tiên tiến, chương trình đào tạo chất lượng cao"
)
add_rule(
    rule_type="multiplier", value=1.3, description="Học ngoài thời gian thiết kế của chương trình đào tạo",
    education_level="undergraduate", study_mode="full_time", program_type="advanced", cohort_min=51, cohort_max=None,
    source="MucHocPhi_QuyDinhChung.md", source_section="2. Đại học hình thức chính quy chương trình đào tạo tiên tiến, chương trình đào tạo chất lượng cao"
)

# Dự bị Dân tộc
add_record(
    education_level="preparatory", study_mode="full_time", program_type="standard", cohort_min=None, cohort_max=None,
    entity_type="all_students", knowledge_scope="other", rate_type="per_academic_year", amount_vnd=12000000,
    source="MucHocPhi_QuyDinhChung.md", source_section="3. Học sinh diện xét tuyển thẳng, học bồi dưỡng kiến thức tại Khoa Dự bị Dân tộc", source_table="Mức học phí"
)
add_record(
    education_level="preparatory", study_mode="full_time", program_type="standard", cohort_min=None, cohort_max=None,
    entity_type="all_students", knowledge_scope="other", rate_type="per_credit", amount_vnd=300000,
    source="MucHocPhi_QuyDinhChung.md", source_section="3. Học sinh diện xét tuyển thẳng, học bồi dưỡng kiến thức tại Khoa Dự bị Dân tộc", source_table="Mức học phí"
)
add_record(
    education_level="preparatory", study_mode="full_time", program_type="standard", cohort_min=None, cohort_max=None,
    entity_type="all_students", knowledge_scope="other", rate_type="other", amount_vnd=6000000, # or per_semester, wait schema says per_credit|per_academic_year|per_full_course. Let's omit 6000000 or set other if allowed. Wait schema only allows rate_type: per_credit|per_academic_year|per_full_course. Let's map per semester to issue or just use per_academic_year / 2? I will map it to an issue.
    source="MucHocPhi_QuyDinhChung.md", source_section="3. Học sinh diện xét tuyển thẳng, học bồi dưỡng kiến thức tại Khoa Dự bị Dân tộc", source_table="Mức học phí"
)
# Let's clean that up later in the loop.

# VLVH
add_record(
    education_level="undergraduate", study_mode="work_study", program_type="standard", cohort_min=None, cohort_max=2026,
    entity_type="all_students", knowledge_scope="other", rate_type="per_credit", amount_vnd=693000, effective_semester="Học kỳ 2",
    source="MucHocPhi_QuyDinhChung.md", source_section="4.1 Đại học hình thức Vừa làm vừa học (VLVH)", source_table="Mức học phí"
)
add_record(
    education_level="undergraduate", study_mode="work_study", program_type="standard", cohort_min=2027, cohort_max=None,
    entity_type="all_students", knowledge_scope="other", rate_type="per_credit", amount_vnd=731000,
    source="MucHocPhi_QuyDinhChung.md", source_section="4.1 Đại học hình thức Vừa làm vừa học (VLVH)", source_table="Mức học phí"
)
add_rule(
    rule_type="max_multiplier", value=1.5, description="Lớp có số lượng sinh viên trúng tuyển dưới 30 sinh viên sẽ thỏa thuận nhân hệ số điều chỉnh",
    education_level="undergraduate", study_mode="work_study", program_type="standard", cohort_min=None, cohort_max=None,
    source="MucHocPhi_QuyDinhChung.md", source_section="4.1 Đại học hình thức Vừa làm vừa học (VLVH)"
)

# Từ xa
add_record(
    education_level="undergraduate", study_mode="distance", program_type="standard", cohort_min=None, cohort_max=2026,
    entity_type="all_students", knowledge_scope="other", rate_type="per_credit", amount_vnd=495000, effective_semester="Học kỳ 2",
    source="MucHocPhi_QuyDinhChung.md", source_section="4.2 Đại học hình thức Đào tạo từ xa", source_table="Mức học phí"
)
add_record(
    education_level="undergraduate", study_mode="distance", program_type="standard", cohort_min=2027, cohort_max=None,
    entity_type="all_students", knowledge_scope="other", rate_type="per_credit", amount_vnd=574300,
    source="MucHocPhi_QuyDinhChung.md", source_section="4.2 Đại học hình thức Đào tạo từ xa", source_table="Mức học phí"
)
add_rule(
    rule_type="max_multiplier", value=1.5, description="Lớp có số lượng sinh viên dưới 25 sinh viên sẽ có thỏa thuận nhân hệ số điều chỉnh",
    education_level="undergraduate", study_mode="distance", program_type="standard", cohort_min=None, cohort_max=None,
    source="MucHocPhi_QuyDinhChung.md", source_section="4.2 Đại học hình thức Đào tạo từ xa"
)

# Thạc sĩ
add_record(
    education_level="master", study_mode="full_time", program_type="standard", cohort_min=None, cohort_max=2025,
    entity_type="all_students", knowledge_scope="other", rate_type="per_credit", amount_vnd=1010000,
    source="MucHocPhi_QuyDinhChung.md", source_section="5.1 Mức học phí", source_table="Mức học phí"
)
add_record(
    education_level="master", study_mode="full_time", program_type="standard", cohort_min=None, cohort_max=2025,
    entity_type="all_students", knowledge_scope="other", rate_type="per_academic_year", amount_vnd=30300000,
    source="MucHocPhi_QuyDinhChung.md", source_section="5.1 Mức học phí", source_table="Mức học phí"
)
add_record(
    education_level="master", study_mode="full_time", program_type="standard", cohort_min=2026, cohort_max=2026,
    entity_type="all_students", knowledge_scope="other", rate_type="per_credit", amount_vnd=1061000,
    source="MucHocPhi_QuyDinhChung.md", source_section="5.1 Mức học phí", source_table="Mức học phí"
)
add_record(
    education_level="master", study_mode="full_time", program_type="standard", cohort_min=2026, cohort_max=2026,
    entity_type="all_students", knowledge_scope="other", rate_type="per_academic_year", amount_vnd=31800000,
    source="MucHocPhi_QuyDinhChung.md", source_section="5.1 Mức học phí", source_table="Mức học phí"
)
add_rule(
    rule_type="multiplier", value=1.5, description="Học ngoài giờ hành chính hoặc ngoài thời gian thiết kế chương trình đào tạo",
    education_level="master", study_mode="full_time", program_type="standard", cohort_min=None, cohort_max=None,
    source="MucHocPhi_QuyDinhChung.md", source_section="5.2 Mức học phí nhân 1,5 lần"
)
add_rule(
    rule_type="multiplier", value=0.5, description="Tốt nghiệp chậm tiến độ (50% mức học phí của học kỳ trễ hạn)",
    education_level="master", study_mode="full_time", program_type="standard", cohort_min=None, cohort_max=None,
    source="MucHocPhi_QuyDinhChung.md", source_section="5.3 Học phí tốt nghiệp chậm tiến độ"
)

# Tiến sĩ
add_record(
    education_level="doctoral", study_mode="full_time", program_type="standard", cohort_min=None, cohort_max=2025,
    entity_type="all_students", knowledge_scope="other", rate_type="per_credit", amount_vnd=1700000,
    source="MucHocPhi_QuyDinhChung.md", source_section="6.1 Mức học phí", source_table="Mức học phí"
)
add_record(
    education_level="doctoral", study_mode="full_time", program_type="standard", cohort_min=None, cohort_max=2025,
    entity_type="all_students", knowledge_scope="other", rate_type="per_academic_year", amount_vnd=51000000,
    source="MucHocPhi_QuyDinhChung.md", source_section="6.1 Mức học phí", source_table="Mức học phí"
)
add_record(
    education_level="doctoral", study_mode="full_time", program_type="standard", cohort_min=2026, cohort_max=2026,
    entity_type="all_students", knowledge_scope="other", rate_type="per_credit", amount_vnd=1876000,
    source="MucHocPhi_QuyDinhChung.md", source_section="6.1 Mức học phí", source_table="Mức học phí"
)
add_record(
    education_level="doctoral", study_mode="full_time", program_type="standard", cohort_min=2026, cohort_max=2026,
    entity_type="all_students", knowledge_scope="other", rate_type="per_academic_year", amount_vnd=56300000,
    source="MucHocPhi_QuyDinhChung.md", source_section="6.1 Mức học phí", source_table="Mức học phí"
)
add_rule(
    rule_type="multiplier", value=0.5, description="Tốt nghiệp chậm tiến độ (50% mức học phí của học kỳ trễ hạn)",
    education_level="doctoral", study_mode="full_time", program_type="standard", cohort_min=None, cohort_max=None,
    source="MucHocPhi_QuyDinhChung.md", source_section="6.2 Học phí tốt nghiệp chậm tiến độ"
)

# Bổ sung thạc sĩ
add_rule(
    rule_type="max_multiplier", value=695000, description="Học bổ sung kiến thức dự thi tuyển sinh trình độ thạc sĩ: tối đa 695.000 đồng/tín chỉ",
    education_level="master", study_mode="full_time", program_type="standard", cohort_min=None, cohort_max=None,
    source="MucHocPhi_QuyDinhChung.md", source_section="7. Học bổ sung kiến thức dự thi tuyển sinh trình độ thạc sĩ"
)

# Fix records
final_records = []
for r in records:
    # Handle rate_type
    if r["rate_type"] not in ["per_credit", "per_academic_year", "per_full_course"]:
        if r["amount_vnd"] == 6000000:
            add_issue(source=r["source"], location=r["source_section"], description="Mức 6.000.000 đ/học kỳ không có rate_type phù hợp trong schema")
            continue
    final_records.append(r)

# Dump tuition_rates.json
output_data = {
    "schema_version": "1.0",
    "currency": "VND",
    "records": final_records,
    "rules": rules,
    "issues": issues
}
with open(r"d:\Project\Chatbot\tuition_rates.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

# Generate report
valid = True
failed_assertions = []
duplicate_ids = []

# Verify ids
all_ids = [r["id"] for r in final_records] + [r["id"] for r in rules]
if len(all_ids) != len(set(all_ids)):
    valid = False
    import collections
    duplicate_ids = [item for item, count in collections.Counter(all_ids).items() if count > 1]

# Assertions:
# 1. CNTT CLC K49 phải có: 36.000.000 đồng/năm học, 1.254.000 đồng/tín chỉ
cntt_clc_49 = [r for r in final_records if r.get("major_name") == "Công nghệ thông tin" and r.get("program_type") == "high_quality" and r.get("cohort_min") == 49]
has_36m = any(r["amount_vnd"] == 36000000 and r["rate_type"] == "per_academic_year" for r in cntt_clc_49)
has_1254k = any(r["amount_vnd"] == 1254000 and r["rate_type"] == "per_credit" for r in cntt_clc_49)
if not has_36m: failed_assertions.append("CNTT CLC K49 thiếu 36.000.000/năm")
if not has_1254k: failed_assertions.append("CNTT CLC K49 thiếu 1.254.000/tín chỉ")

# 2. Đại cương chung K49 của chương trình CLC/Tiên tiến phải có: 441.000 đồng/tín chỉ
dc_clc_49 = [r for r in final_records if r.get("entity_type") == "all_students" and r.get("knowledge_scope") == "general_common" and r.get("program_type") in ["high_quality", "advanced"] and r.get("cohort_min") == 49]
if not any(r["amount_vnd"] == 441000 for r in dc_clc_49): failed_assertions.append("Đại cương CLC/TT K49 thiếu 441.000/tín chỉ")

# 3. CNTT CLC K49 không được gắn program_type="standard"
if any(r.get("program_type") == "standard" for r in cntt_clc_49): failed_assertions.append("CNTT CLC K49 bị gắn program_type=standard")

# 4. CNTT đại trà khóa 49 phải lấy từ file Khóa 51 trở về trước
cntt_dt_49 = [r for r in final_records if r.get("major_name") == "Công nghệ thông tin" and r.get("program_type") == "standard" and r.get("cohort_max") == 51]
if not cntt_dt_49: failed_assertions.append("CNTT đại trà K49 không tìm thấy từ file K51 trở về trước")

# 5. CNTT đại trà khóa 52 phải lấy từ file Khóa 52
cntt_dt_52 = [r for r in final_records if r.get("major_name") == "Công nghệ thông tin" and r.get("program_type") == "standard" and r.get("cohort_min") == 52]
if not cntt_dt_52: failed_assertions.append("CNTT đại trà K52 không tìm thấy từ file K52")

# 7, 8, 9, 10
if any(type(r["amount_vnd"]) is not int for r in final_records): failed_assertions.append("amount_vnd không phải số nguyên")
allowed_sources = ["MucHocPhi_ChatLuongCao_TienTien.md", "MucHocPhi_DaiHocChinhQuy_Khoa51_VeTruoc.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md", "MucHocPhi_QuyDinhChung.md"]
if any(r["source"] not in allowed_sources for r in final_records): failed_assertions.append("Source không hợp lệ")

if failed_assertions: valid = False
if duplicate_ids: valid = False

report = {
    "valid": valid,
    "record_count": len(final_records),
    "rule_count": len(rules),
    "issue_count": len(issues),
    "records_by_source": {},
    "records_by_program_type": {},
    "records_by_rate_type": {},
    "duplicate_ids": duplicate_ids,
    "failed_assertions": failed_assertions
}
for r in final_records:
    report["records_by_source"][r["source"]] = report["records_by_source"].get(r["source"], 0) + 1
    report["records_by_program_type"][r["program_type"]] = report["records_by_program_type"].get(r["program_type"], 0) + 1
    report["records_by_rate_type"][r["rate_type"]] = report["records_by_rate_type"].get(r["rate_type"], 0) + 1

with open(r"d:\Project\Chatbot\tuition_rates_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
