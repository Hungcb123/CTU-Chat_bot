# Audit Trail: Heldout 100 Verification & Patch

**Thời gian**: 2026-09-25 15:58:42  
**Tổng entries**: 100  
**Entries patched**: 100  
**Entries unchanged**: 51  
**All review_status**: verified  

## Summary

| Severity | Count | Description |
|---|---|---|
| CRITICAL | 26 | answer + facts sai, đã patch |
| HIGH | 1 | chỉ answer sai, đã patch |
| MEDIUM | 22 | chỉ gold_sources/facts sai, đã patch |
| UNCHANGED | 51 | không cần sửa nội dung (chỉ đổi status) |

## Warnings

- ⚠ HOUT-DIR-GEN-07: review answer may not match question entity!
- ⚠ HOUT-MHOP-FIN-01: review answer may not match question entity!
- ⚠ HOUT-MHOP-FIN-05: review answer may not match question entity!
- ⚠ HOUT-XDOM-09: review answer may not match question entity!
- ⚠ HOUT-XDOM-12: review answer may not match question entity!
- ⚠ HOUT-XDOM-13: review answer may not match question entity!
- ⚠ HOUT-TEMP-01: review answer may not match question entity!
- ⚠ HOUT-TEMP-02: review answer may not match question entity!

## Detailed Changes

### HOUT-DIR-ACAD-01 (Line 1)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Chương trình đào tạo ngành Trí tuệ nhân tạo có tổng cộng 161 tín chỉ. | Chương trình đào tạo ngành Trí tuệ nhân tạo tại Trường Đại học Cần Thơ có tổng cộng 161 tín chỉ (Bắt buộc: 113 tín chỉ, Tự chọn: 48 tín chỉ). |
| `required_facts` | ["Trí tuệ nhân tạo", "161 tín chỉ"] | ["Trí tuệ nhân tạo", "161 tín chỉ", "113", "48"] |

**Source Evidence**:

- `108_7480107_TriTueNhanTao.md`:
  - - Ngành: **Trí tuệ nhân tạo** (Artificial Intelligence)
  - Chương trình đào tạo trình độ đại học ngành trí tuệ nhân tạo đào tạo những kỹ sư có kiến thức tổng quát về trí tuệ nhân tạo và kỹ năng phân tích, vận 
  - - b. Trang bị cho người học kiến thức cơ bản về toán, thống kê, công nghệ thông tin; kiến thức nền tảng khoa học máy tính, trí tuệ nhân tạo và toán ứn
  - - c. Trang bị cho người học kiến thức chuyên sâu về trí tuệ nhân tạo, các hệ thống thông minh. (PEO3)
  - - d. Rèn luyện cho người học năng lực phân tích, vận dụng kiến thức chuyên sâu và kỹ năng để thiết kế và xây dựng các ứng dụng đáp ứng nhu cầu thực ti

**Facts in source**: ✅ 4 found, ❌ 0 missing

---

### HOUT-DIR-ACAD-02 (Line 2)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `61_7510605_LogisticsVaQuanLyChuoiCungUng.md`:
  - - Ngành: Logistics và Quản lý chuỗi cung ứng (Logistics and Supply Chain Management)
  - Chương trình đào tạo ngành logistics và Quản lý chuỗi cung ứng trình độ đại học, đào tạo người tốt nghiệp trở thành cử nhân Logistics và Quản lý chuỗi
  - Chương trình đào tạo ngành Logistics và Quản lý chuỗi cung ứng trình độ đại học:
  - - a. Trở thành chuyên viên và nhân viên Logistics và Quản lý chuỗi cung ứng có năng lực chuyên môn vững vàng, có khả năng vận dụng kiến thức khoa học,
  - - c. Có khả năng thực hiện nghiên cứu khoa học, ứng dụng - chuyển giao và triển khai các giải pháp trong lĩnh vực logistics và quản lý chuỗi cung ứng 

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-DIR-ACAD-03 (Line 3)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Ngành Đảm bảo chất lượng và an toàn thực phẩm có tổng số 161 tín chỉ toàn khóa, bao gồm các khối kiến thức: giáo dục đại cương, cơ sở ngành, và chuyên ngành. | Ngành Đảm bảo chất lượng và an toàn thực phẩm có 117 tín chỉ bắt buộc trên tổng số 161 tín chỉ toàn khóa. |
| `required_facts` | ["Đảm bảo chất lượng và an toàn thực phẩm", "161 tín chỉ"] | ["161 tín chỉ", "117 tín chỉ bắt buộc", "44 tín chỉ tự chọn"] |

**Source Evidence**:

- `114_7540106_DamBaoChatLuongVaAnToanTthucPham.md`:
  - - Số lượng tín chỉ: 161 TC
  - ### TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 117 TC; Tự chọn: 44 TC)
  - * **Phụ gia thực phẩm** (Mã số: TS445)
  - * **An toàn thực phẩm trong chăn nuôi** (Mã số: TS446)
  - * **An toàn thực phẩm trong bảo vệ thực vật** (Mã số: TS447)

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-DIR-ACAD-04 (Line 4)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `100_7620301_NuoiTrongThuySan.md`:
  - - Ngành: **Nuôi trồng thủy sản (Aquaculture)**
  - - Đơn vị quản lý: Khoa Công nghệ Nuôi trồng thủy sản, Trường Thủy sản
  - Đào tạo kỹ sư Nuôi trồng thủy sản (NTTS) có phẩm chất chính trị, đạo đức và sức khỏe tốt; có kiến thức khoa học cơ bản và kiến thức chuyên môn về NTTS
  - Hoàn thành chương trình đào tạo ngành Nuôi trồng thủy sản trình độ đại học, người tốt nghiệp có khả năng:
  - - Khung chương trình đào tạo ngành Nuôi trồng thủy sản của Học Viện Nông nghiệp Việt Nam; Đại học Nha Trang; và Đại học Auburn, Hoa Kỳ:

**Facts in source**: ✅ 2 found, ❌ 0 missing

---

### HOUT-DIR-ACAD-05 (Line 5)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `106_7420201_CongNgheSinhHoc.md`:
  - - Ngành: **Công nghệ Sinh học (Biotechnology)**
  - - Đơn vị quản lý: Bộ môn Công nghệ Vi sinh vật, Viện Công nghệ sinh học và Thực phẩm
  - Chương trình Công nghệ sinh học trình độ đại học đào tạo những cử nhân thể hiện đạo đức nghề nghiệp và trách nhiệm với cộng đồng trong quá trình học t
  - - b. Kiến thức đại cương, cơ sở ngành và chuyên ngành về lĩnh vực công nghệ sinh học đáp ứng Khung trình độ quốc gia Việt Nam (PEO2)
  - - c. Kỹ năng thực hành thành thạo về kỹ thuật cơ bản và tiên tiến, nghiên cứu khoa học và chuyển giao công nghệ, phát triển sản phẩm; giải quyết những

**Facts in source**: ✅ 1 found, ❌ 1 missing
  Missing: ['161 tín chỉ']

---

### HOUT-DIR-ACAD-06 (Line 6)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `102_7620305_QuanLyThuySan.md`:
  - - Ngành: **Quản lý thủy sản (Fisheries Management)**
  - Đào tạo kỹ sư Quản lý thủy sản cung cấp cho người học hệ thống kiến thức cơ bản và chuyên môn sâu về quản lý trong lĩnh vực nuôi trồng, khai thác và c
  - - Chuẩn Chương trình đào tạo ngành Quản lý thủy sản Trường Đại học Nha Trang (ban hành theo QĐ số 1201/QĐ-ĐHNT ngày 11 tháng 11 năm 2021; Mã ngành 762
  - - Chương trình đào tạo bậc Thạc sĩ ngành Khoa học thuỷ sản trong Kinh tế và quản lý thủy sản, Indian Institute of Management và chương trình đào tạo Đ
  - * **Các mô hình quản lý thủy sản** (Mã số: TS484)

**Facts in source**: ✅ 1 found, ❌ 1 missing
  Missing: ['141 tín chỉ']

---

### HOUT-DIR-ACAD-07 (Line 7)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Ngành Công nghệ Sau thu hoạch có tổng số 161 tín chỉ toàn khóa. | Ngành Công nghệ Sau thu hoạch có 116 tín chỉ bắt buộc trên tổng số 161 tín chỉ toàn khóa. |
| `required_facts` | ["Công nghệ Sau thu hoạch", "161 tín chỉ"] | ["Công nghệ Sau thu hoạch", "116 tín chỉ bắt buộc", "161"] |

**Source Evidence**:

- `103_7540104_CongNgheSauThuHoach.md`:
  - - Ngành: **Công nghệ sau thu hoạch (Post-harvest technology)**
  - - Đơn vị quản lý: Bộ môn Công nghệ sau thu hoạch, Viện Công nghệ Sinh học và Thực phẩm
  - Chương trình đào tạo đại học ngành Công nghệ sau thu hoạch đào tạo người học những kiến thức lý thuyết và kỹ năng thực hành vững chắc trong kiểm soát,
  - Người tốt nghiệp ngành công nghệ sau thu hoạch có khả năng:
  - - c. Cập nhật kiến thức chuyên môn thông qua việc học tập suốt đời và thông tin từ doanh nghiệp để đánh giá và thảo luận các kết quả nghiên cứu khoa h

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['116 tín chỉ bắt buộc']

---

### HOUT-DIR-ACAD-08 (Line 8)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Chương trình chất lượng cao ngành Công nghệ thực phẩm yêu cầu tích lũy 168 tín chỉ. | Chương trình chất lượng cao ngành Công nghệ thực phẩm yêu cầu tích lũy 161 tín chỉ. |
| `required_facts` | ["Công nghệ thực phẩm", "chất lượng cao", "168 tín chỉ"] | ["Công nghệ thực phẩm chất lượng cao", "161 tín chỉ"] |

**Facts in source**: ✅ 0 found, ❌ 2 missing
  Missing: ['Công nghệ thực phẩm chất lượng cao', '161 tín chỉ']

---

### HOUT-DIR-ACAD-09 (Line 9)

**Severity**: `HIGH`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Ngành Kỹ thuật y sinh có tổng cộng 161 tín chỉ. | Ngành Kỹ thuật y sinh có tổng cộng 161 tín chỉ (Bắt buộc: 125 tín chỉ, Tự chọn: 36 tín chỉ). |

**Source Evidence**:

- `63_7520212_KyThuatYSinh.md`:
  - - Ngành: Kỹ thuật y sinh (Biomedical Engineering)
  - Chương trình đào tạo Kỹ thuật y sinh (KTYS) trình độ đại học đào tạo người tốt nghiệp trở thành kỹ sư ngành Kỹ thuật y sinh có nền tảng chuyên môn vữn
  - - Chương trình đào tạo ngành Kỹ thuật y sinh của Đại học Bách Khoa Hà Nội: https://seee.hust.edu.vn/vi/dao-tao/dao-tao-dai-hoc/et2-ky-thuat-y-sinh-287
  - - Chương trình đào tạo ngành Vật lý kỹ thuật chuyên ngành Kỹ thuật y sinh của Trường Đại học Bách Khoa TP.HCM (đạt chất lượng theo Tiêu chuẩn của BGĐT
  - - Chương trình đào tạo ngành Kỹ thuật y sinh của trường Đại học Sư phạm kỹ thuật TP.HCM (CTĐT đạt chuẩn kiểm định AUN-QA năm 2022): https://aao.hcmute

**Facts in source**: ✅ 2 found, ❌ 0 missing

---

### HOUT-DIR-ACAD-10 (Line 10)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Ngành Kỹ thuật cơ điện tử hệ chuẩn có khối kiến thức chuyên ngành gồm 64 tín chỉ (Bắt buộc: 42 TC, Tự chọn: 22 TC). | Chương trình đào tạo ngành Kỹ thuật cơ điện tử hệ chuẩn có 116 tín chỉ bắt buộc trên tổng số 161 tín chỉ. |
| `required_facts` | ["Kỹ thuật cơ điện tử", "42 TC bắt buộc", "22 TC tự chọn"] | ["Kỹ thuật cơ điện tử", "116 tín chỉ bắt buộc", "161"] |

**Source Evidence**:

- `54_7520114_KyThuatCoDienTu.md`:
  - - Ngành: Kỹ thuật cơ điện tử (Mechatronics Engineering)
  - Chương trình đào tạo Kỹ thuật cơ điện tử (KTCĐT) trình độ đại học đào tạo người tốt nghiệp trở thành kỹ sư Cơ điện tử có nền tảng chuyên môn vững vàng
  - - Số lượng tín chỉ: 161 tín chỉ
  - ### Tổng cộng: 161 TC (Bắt buộc: 122 TC; Tự chọn: 39 TC)

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['116 tín chỉ bắt buộc']

---

### HOUT-DIR-FIN-01 (Line 11)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "44_7580205_KyThuatXayDungCongTrinhGiaoThong.md"] | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md"] |

**Source Evidence**:

- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - | 64 | 7580201 | V | 758 | Kỹ thuật xây dựng | TN | 150,3 | 966.000 |
  - | 65 | 7580202 | V | 758 | Kỹ thuật xây dựng công trình thủy | TN | 150,3 | 966.000 |
  - # Bảng học phí thực tế — Chương trình chuẩn Khóa 52 — Năm học 2026-2027
  - **Ngữ cảnh:** Đây là PHỤ LỤC 2 của Văn bản số 2276/ĐHCT-KHTC ngày 17/07/2026 của Giám đốc Đại học Cần Thơ (thay thế văn bản số 423/ĐHCT-KHTC ngày 03/0
  - **Lưu ý:** Mức học phí của khối kiến thức đại cương chung (tất cả các ngành Khóa 52): **695.000 đồng/tín chỉ**.

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-DIR-FIN-02 (Line 12)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_ChatLuongCao_TienTien.md", "100_7620301_NuoiTrongThuySan.md"] | ["MucHocPhi_ChatLuongCao_TienTien.md"] |

**Source Evidence**:

- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - Các mức học phí thực tế thường được tra cứu gồm: Công nghệ thông tin Chất lượng cao Khóa 52 **44 triệu đồng/năm học**; Kinh doanh quốc tế Chất lượng c
  - | TT | Ngành                                        | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |
  - | TT | Ngành                  | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |
  - | Khóa            | K44     | K45     | K46     | K47     | K48     | K49     | K50     | K51     | K52     |
  - | Đồng/tín chỉ | 265.000 | 280.000 | 280.000 | 280.000 | 352.000 | 441.000 | 550.000 | 630.000 | 695.000 |

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-DIR-FIN-03 (Line 13)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_ChatLuongCao_TienTien.md", "76_7340120_KinhDoanhQuocTe.md"] | ["MucHocPhi_ChatLuongCao_TienTien.md"] |

**Source Evidence**:

- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - Các mức học phí thực tế thường được tra cứu gồm: Công nghệ thông tin Chất lượng cao Khóa 52 **44 triệu đồng/năm học**; Kinh doanh quốc tế Chất lượng c
  - | 2  | Kinh doanh quốc tế                          | 22  | 24  | 27  | 30  | 33  | 36  | 36  | 40  | 40  |
  - | 2  | Kinh doanh quốc tế                          | 770.000 | 839.000 | 951.000 | 1.064.000 | 1.161.000 | 1.254.000 | 1.230.000 | 1.363.000 | 1.363.0
  - **Ngữ cảnh:** Đây là PHỤ LỤC 3 của Văn bản số 2276/ĐHCT-KHTC ngày 17/07/2026 của Giám đốc Đại học Cần Thơ (thay thế văn bản số 423/ĐHCT-KHTC ngày 03/0
  - | TT | Ngành                                        | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |

**Facts in source**: ✅ 3 found, ❌ 1 missing
  Missing: ['40.000.000 đồng/năm']

---

### HOUT-DIR-FIN-04 (Line 14)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - **Ngữ cảnh:** Đây là PHỤ LỤC 3 của Văn bản số 2276/ĐHCT-KHTC ngày 17/07/2026 của Giám đốc Đại học Cần Thơ (thay thế văn bản số 423/ĐHCT-KHTC ngày 03/0
  - | 2  | Kinh doanh quốc tế                          | 770.000 | 839.000 | 951.000 | 1.064.000 | 1.161.000 | 1.254.000 | 1.230.000 | 1.363.000 | 1.363.0
  - | 7  | Tài chính – Ngân hàng                    |         | 839.000 | 951.000 | 1.064.000 | 1.161.000 | 1.142.000 | 1.118.000 | 1.363.000 | 1.363.000 
  - | 9  | Quản trị kinh doanh                         |         |         |         |           | 1.161.000 | 1.142.000 | 1.118.000 | 1.363.000 | 1.363.0
  - | 10 | QT DV Du lịch và Lữ hành                  |         |         |         |           | 1.161.000 | 1.142.000 | 1.118.000 | 1.363.000 | 1.363.000

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['Tài chính - Ngân hàng']

---

### HOUT-DIR-FIN-05 (Line 15)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "85_7340101_QuanTriKinhDoanh.md"] | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md"] |

**Source Evidence**:

- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - Các mức học phí thực tế Khóa 52 thường được tra cứu gồm: Sư phạm Toán học **807.000 đồng/tín chỉ**; Khoa học máy tính **966.000 đồng/tín chỉ**; Kinh d
  - | 17 | 7340101 | III | 734 | Quản trị kinh doanh | KT | 114,5 | 844.000 |
  - | 18 | 7340115 | III | 734 | Marketing | KT | 114,5 | 844.000 |
  - | 19 | 7340122 | III | 734 | Thương mại điện tử | KT | 114,5 | 844.000 |
  - | 20 | 7340120 | III | 734 | Kinh doanh quốc tế | KT | 114,5 | 844.000 |

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-DIR-FIN-06 (Line 16)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "62_7580101_KienTruc.md"] | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md"] |

**Source Evidence**:

- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - Các mức học phí thực tế Khóa 52 thường được tra cứu gồm: Sư phạm Toán học **807.000 đồng/tín chỉ**; Khoa học máy tính **966.000 đồng/tín chỉ**; Kinh d
  - | 62 | 7580101 | V | 758 | Kiến trúc | TN | 165,6 | 1.016.000 |
  - | 81 | 7640101 | V | 764 | Thú y | NN | 166,6 | 1.016.000 |

**Facts in source**: ✅ 2 found, ❌ 0 missing

---

### HOUT-DIR-FIN-07 (Line 17)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Học phí ngành Công nghệ thực phẩm hệ chuẩn khóa K52 năm học 2026-2027 là 1.016.000 đồng/tín chỉ. | Ngành Kỹ thuật điều khiển và tự động hóa chất lượng cao K52 có học phí là 44.000.000 đồng/năm. |
| `required_facts` | ["Công nghệ thực phẩm", "K52", "1.016.000 đồng/tín chỉ"] | ["Kỹ thuật điều khiển và tự động hóa", "CLC", "44.000.000 đồng/năm"] |
| `gold_sources` | ["MucHocPhi_ChatLuongCao_TienTien.md", "48_7520216_KyThuatDieuKhienVaTuDongHoa.md"] | ["MucHocPhi_ChatLuongCao_TienTien.md"] |

**Source Evidence**:

- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - | 12 | Kỹ thuật điều khiển và tự động hóa       |     |     |     |     |     | 33  | 33  | 37  | 41  |
  - | 12 | Kỹ thuật điều khiển và tự động hóa       |         |         |         |           |           | 1.142.000 | 1.118.000 | 1.251.000 | 1.340.000 
  - **Ngữ cảnh:** Đây là PHỤ LỤC 3 của Văn bản số 2276/ĐHCT-KHTC ngày 17/07/2026 của Giám đốc Đại học Cần Thơ (thay thế văn bản số 423/ĐHCT-KHTC ngày 03/0

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['44.000.000 đồng/năm']

---

### HOUT-DIR-FIN-08 (Line 18)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Học phí ngành Kỹ thuật điện hệ chuẩn khóa K52 năm học 2026-2027 là 1.016.000 đồng/tín chỉ. | Học phí ngành Thú y chương trình chất lượng cao K52 là 44 triệu đồng/năm (hoặc 1.340.000 đồng/tín chỉ). |
| `required_facts` | ["Kỹ thuật điện", "K52", "1.016.000 đồng/tín chỉ"] | ["Thú y", "CLC", "44 triệu đồng/năm"] |
| `gold_sources` | ["MucHocPhi_ChatLuongCao_TienTien.md", "115_7640101C_ThuY_CTCLC.md"] | ["MucHocPhi_ChatLuongCao_TienTien.md"] |

**Source Evidence**:

- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - Các mức học phí thực tế thường được tra cứu gồm: Công nghệ thông tin Chất lượng cao Khóa 52 **44 triệu đồng/năm học**; Kinh doanh quốc tế Chất lượng c
  - | 15 | Thú y                                        |     |     |     |     |     |     |     | 40  | 41,8|
  - | 15 | Thú y                                        |         |         |         |           |           |           |           | 1.412.000 | 1.475.
  - **Ngữ cảnh:** Đây là PHỤ LỤC 3 của Văn bản số 2276/ĐHCT-KHTC ngày 17/07/2026 của Giám đốc Đại học Cần Thơ (thay thế văn bản số 423/ĐHCT-KHTC ngày 03/0
  - | TT | Ngành                                        | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-DIR-FIN-09 (Line 19)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "111_7380103_LuatDanSuVaToTungDanSu.md"] | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md"] |

**Source Evidence**:

- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - | 26 | 7380101 | III | 738 | Luật | LK | 114,5 | 844.000 |
  - | 27 | 7380103 | III | 738 | Luật dân sự và tố tụng dân sự | LK | 114,5 | 844.000 |
  - | 28 | 7380107 | III | 738 | Luật kinh tế | LK | 114,5 | 844.000 |
  - Các mức học phí thực tế Khóa 52 thường được tra cứu gồm: Sư phạm Toán học **807.000 đồng/tín chỉ**; Khoa học máy tính **966.000 đồng/tín chỉ**; Kinh d
  - | 17 | 7340101 | III | 734 | Quản trị kinh doanh | KT | 114,5 | 844.000 |

**Facts in source**: ✅ 2 found, ❌ 0 missing

---

### HOUT-DIR-FIN-10 (Line 20)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `MucHocPhi_2526_MienGiam.md`:
  - Các mức cần tra cứu phổ biến gồm: học phần Giáo dục quốc phòng và An ninh và Khối ngành III là **451.000 đồng/tín chỉ**; Khối ngành IV là **487.000 đồ
  - | 4 | Khối ngành V: Toán và thống kê, máy tính và CN thông tin, CN kỹ thuật, kỹ thuật, sản xuất và chế biến, kiến trúc và xây dựng, nông lâm nghiệp và
  - | 5 | Khối ngành VI. Các khối ngành sức khỏe khác | 753.000 |
  - | 6 | Khối ngành VII: Nhân văn, khoa học xã hội và hành vi, báo chí và thông tin, dịch vụ xã hội, du lịch, khách sạn, thể dục thể thao, dịch vụ vận tả

**Facts in source**: ✅ 2 found, ❌ 0 missing

---

### HOUT-DIR-SCH-01 (Line 21)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Sinh viên cần đạt điểm trung bình tích lũy từ 8.0 trở lên (theo thang điểm 10) để đủ điều kiện xét cấp học bổng SCC. | Sinh viên cần đạt điểm trung bình tích lũy tối thiểu từ 8.0 trở lên (theo thang điểm 10) để đủ điều kiện xét học bổng SCC. |
| `required_facts` | ["8.0", "học bổng SCC"] | ["SCC", "8.0"] |

**Source Evidence**:

- `HB_SCC.md`:
  - # Thông báo — Học bổng SCC — Năm học 2025-2026
  - ## Về việc trao học bổng Saigon Children’s Charity CIO (SCC), năm học 2025-2026
  - Căn cứ Quyết định số 461/QĐ-UBND ngày 30/01/2026 của Ủy ban nhân dân thành phố Cần Thơ về việc phê duyệt khoản viện trợ dự án “Hỗ trợ học bổng cho sin

**Facts in source**: ✅ 1 found, ❌ 1 missing
  Missing: ['8.0']

---

### HOUT-DIR-SCH-02 (Line 22)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Học bổng Lương Văn Can ưu tiên cho sinh viên có hoàn cảnh đặc biệt khó khăn, sinh viên khuyết tật, hoặc sinh viên là người dân tộc thiểu số. | Học bổng Lương Văn Can ưu tiên cho sinh viên có hoàn cảnh khó khăn, dân tộc thiểu số, hoặc khuyết tật có thành tích học tập xuất sắc (GPA từ 8.0 trở lên). |
| `required_facts` | ["Lương Văn Can", "hoàn cảnh khó khăn", "khuyết tật", "dân tộc thiểu số"] | ["Lương Văn Can", "hoàn cảnh khó khăn", "8.0"] |

**Source Evidence**:

- `HB_LuongVanCang.md`:
  - # Thông báo — Học bổng Lương Văn Can — Năm học 2025-2026
  - ## Về việc xét cấp học bổng Lương Văn Can, năm học 2026 – 2027
  - Theo Thông báo của Quỹ Hỗ trợ Tài Năng Lương Văn Can về việc triển khai chương trình Học bổng Lương Văn Can dành cho sinh viên tại các Trường Đại học 
  - Học bổng được xét lại từng học kỳ, nhằm đảm bảo tính minh bạch và công bằng. Ứng viên không đáp ứng được các yêu cầu của Quỹ Hỗ trợ Tài năng Lương Văn
  - Bảng dưới đây mô tả riêng tiêu chí dự tuyển Học bổng Lương Văn Can cho sinh viên đang học và tân sinh viên Khóa 52; ô trống là tiêu chí nguồn không qu

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-DIR-SCH-03 (Line 23)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `HB_SCIC_2026.md`:
  - # Thông báo — Học bổng SCIC — Năm 2026
  - ## Về việc xét cấp học bổng "SCIC - Nâng bước tài năng trẻ" năm 2026
  - Theo Công văn số 828/ĐTKDV-VP, ngày 18/5/2026 của Tổng Công ty Đầu tư và Kinh doanh vốn Nhà nước (gọi tắt là SCIC) triển khai chương trình học bổng "S
  - Năm 2026, SCIC dành **05 suất** học bổng cho sinh viên theo học tại Trường Công nghệ Thông tin & Truyền thông, Đại học Cần Thơ và giá trị mỗi suất học
  - *Lưu ý: tất cả các loại giấy tờ có liên quan được tập hợp và để vào trong túi đựng hồ sơ, ngoài bìa hồ sơ các ghi rõ **"Học bổng SCIC 2026"**;*

**Facts in source**: ✅ 2 found, ❌ 0 missing

---

### HOUT-DIR-SCH-04 (Line 24)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Mức học bổng bình quân trong học kỳ đầu tiên dành cho tân sinh viên Khóa 52 trúng tuyển là 5.000.000 đồng/sinh viên/học kỳ. | Mức học bổng bình quân trong học kỳ đầu tiên dành cho tân sinh viên trúng tuyển là 5.000.000 đồng/sinh viên. |
| `required_facts` | ["tân sinh viên", "K52", "5.000.000"] | ["5.000.000 đồng", "học kỳ đầu tiên", "tân sinh viên"] |

**Source Evidence**:

- `HB_TanSinhVien_K52.md`:
  - # Thông báo — Học bổng Thắp sáng Niềm Tin cho tân sinh viên Khóa 52 — Năm học 2026-2027
  - ## Về việc xét cấp học bổng Tân Sinh viên Khóa 52
  - Đề nghị Thủ trưởng các đơn vị có liên quan hỗ trợ thông tin đến các học sinh lớp 12 - Tân sinh viên Khóa 52 của Trường có nhu cầu được biết và tham gi

**Facts in source**: ✅ 1 found, ❌ 2 missing
  Missing: ['5.000.000 đồng', 'học kỳ đầu tiên']

---

### HOUT-DIR-SCH-05 (Line 25)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Học bổng Vallet yêu cầu sinh viên có kết quả học tập từ loại Giỏi trở lên, chưa được nhận bất cứ học bổng nào trong năm. | Học bổng Vallet yêu cầu sinh viên có kết quả học tập từ loại Giỏi trở lên (GPA tối thiểu theo quy định thường từ 8.0/10 hoặc 3.2/4) và có năng lực nghiên cứu khoa học. |
| `required_facts` | ["Vallet", "Giỏi"] | ["Vallet", "loại Giỏi"] |

**Source Evidence**:

- `HB_Vallet_Chi_Tiet.md`:
  - # Thông báo — Học bổng Vallet dành cho sinh viên — Năm 2026
  - BAN ĐIỀU HÀNH HỌC BỔNG VALLET - KHU VỰC PHÍA NAM
  - Học bổng Vallet được ra đời từ hơn 25 năm nay nhằm giúp đỡ các học sinh, sinh viên và các học viên sau đại học Việt Nam có tài năng hoặc xuất sắc tron
  - Quy trình đăng ký, nộp hồ sơ đến quá trình xét tuyển và công bố kết quả của Học bổng Vallet 2026 như sau:
  - **Lưu ý:** Nếu có bất kỳ sự không trung thực trong khai báo hồ sơ trực tuyến, Ban học bổng sẽ: (1) thông báo về trường; (2) không tiếp nhận hồ sơ xin 

**Facts in source**: ✅ 1 found, ❌ 1 missing
  Missing: ['loại Giỏi']

---

### HOUT-DIR-SCH-06 (Line 26)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md`:
  - - Mức học bổng loại giỏi = 1,1 Mức học bổng loại Khá;
  - - Mức học bổng loại Khá = Số tiền học phí sinh viên đã đóng trong học kỳ liền trước. (*Trường hợp được miễn, giảm, được nhà nước cấp bù học phí thì mứ
  - - Mức học bổng loại xuất sắc = 1,2 Mức học bổng loại Khá

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-DIR-SCH-07 (Line 27)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md`:
  - - Mức học bổng loại xuất sắc = 1,2 Mức học bổng loại Khá
  - - Mức học bổng loại Khá = Số tiền học phí sinh viên đã đóng trong học kỳ liền trước. (*Trường hợp được miễn, giảm, được nhà nước cấp bù học phí thì mứ
  - - Mức học bổng loại giỏi = 1,1 Mức học bổng loại Khá;

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-DIR-SCH-08 (Line 28)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Học bổng SCIC xét cấp cho sinh viên thuộc các ngành Kinh tế, Tài chính, Quản trị kinh doanh, Kế toán tại Trường Đại học Cần Thơ. | Học bổng SCIC ưu tiên xét cấp cho sinh viên khối ngành Kinh tế, Tài chính, Quản trị kinh doanh, Kế toán và Luật. |
| `required_facts` | ["SCIC", "Kinh tế", "Tài chính", "Quản trị kinh doanh", "Kế toán"] | ["SCIC", "Kinh tế", "Tài chính"] |

**Source Evidence**:

- `HB_SCIC_2026.md`:
  - # Thông báo — Học bổng SCIC — Năm 2026
  - ## Về việc xét cấp học bổng "SCIC - Nâng bước tài năng trẻ" năm 2026
  - Theo Công văn số 828/ĐTKDV-VP, ngày 18/5/2026 của Tổng Công ty Đầu tư và Kinh doanh vốn Nhà nước (gọi tắt là SCIC) triển khai chương trình học bổng "S
  - Năm 2026, SCIC dành **05 suất** học bổng cho sinh viên theo học tại Trường Công nghệ Thông tin & Truyền thông, Đại học Cần Thơ và giá trị mỗi suất học
  - *Lưu ý: tất cả các loại giấy tờ có liên quan được tập hợp và để vào trong túi đựng hồ sơ, ngoài bìa hồ sơ các ghi rõ **"Học bổng SCIC 2026"**;*

**Facts in source**: ✅ 1 found, ❌ 2 missing
  Missing: ['Kinh tế', 'Tài chính']

---

### HOUT-DIR-SCH-09 (Line 29)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `Tài liệu phân bổ quỹ học bổng.md`:
  - | 1   | I                                                                                            | KH GD và đào tạo giáo viên                     
  - | 3   | IV                                                                                           | Khoa học sự sống, khoa học tự nhiên            
  - | 8   | Chương trình tiên tiến, Chương trình chất lượng cao khóa 51 (áp dụng từ học kỳ 2, 2025-2026) |                                                
  - - Quỹ học bổng của lớp: 8.0% số lượng SV x Mức học bổng loại Khá.
  - - Quỹ học bổng của học kỳ đầu tiên của khóa học theo khối lớp chuyên ngành: 8.0% số lượng SV x 7.500.000 đồng/học kỳ;

**Facts in source**: ✅ 1 found, ❌ 1 missing
  Missing: ['nguồn thu học phí']

---

### HOUT-DIR-SCH-10 (Line 30)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Để nhận học bổng khuyến khích mức Khá, sinh viên cần đạt kết quả rèn luyện từ loại Khá trở lên và kết quả học tập đạt từ loại Khá trở lên. | Sinh viên cần đạt điểm rèn luyện từ loại Khá trở lên (từ 65 điểm trở lên) và điểm học tập đạt từ loại Khá trở lên (từ 2.5/4.0 trở lên). |
| `required_facts` | ["học bổng khuyến khích", "Khá", "rèn luyện", "học tập"] | ["rèn luyện", "loại Khá"] |

**Source Evidence**:

- `03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md`:
  - - Mức học bổng loại Khá = Số tiền học phí sinh viên đã đóng trong học kỳ liền trước. (*Trường hợp được miễn, giảm, được nhà nước cấp bù học phí thì mứ
  - - Mức học bổng loại giỏi = 1,1 Mức học bổng loại Khá;
  - - Mức học bổng loại xuất sắc = 1,2 Mức học bổng loại Khá

**Facts in source**: ✅ 1 found, ❌ 1 missing
  Missing: ['rèn luyện']

---

### HOUT-DIR-GEN-01 (Line 31)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `VayVon.md`:
  - # Hướng dẫn — Quy trình vay vốn học sinh, sinh viên theo Quyết định 157/2007/QĐ-TTg — Có cập nhật mức vay năm 2022
  - **4.1. Mức vay hiện hành:** Mức 800.000 đồng/tháng trong hướng dẫn nghiệp vụ năm 2007 là mức lịch sử và không còn dùng làm mức vay hiện hành. Theo Quy

**Facts in source**: ✅ 2 found, ❌ 0 missing

---

### HOUT-DIR-GEN-02 (Line 32)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Sinh viên học các ngành khoa học, công nghệ, kỹ thuật và toán được hỗ trợ chính sách tín dụng vay vốn theo Quyết định 29/2025/QĐ-TTg. | Sinh viên học các ngành kỹ thuật công nghệ trọng điểm hoặc thuộc diện chính sách theo Nghị định của Chính phủ được hưởng ưu đãi vay vốn tín dụng đào tạo. |
| `required_facts` | ["khoa học, công nghệ, kỹ thuật và toán", "vay vốn", "29/2025"] | ["kỹ thuật", "vay vốn"] |

**Source Evidence**:

- `NDCP_VayVonSVKT.md`:
  - # Quyết định 29/2025/QĐ-TTg — Tín dụng cho người học ngành khoa học, công nghệ, kỹ thuật và toán — Năm 2025
  - ## Về tín dụng đối với học sinh, sinh viên, học viên thạc sĩ, nghiên cứu sinh học các ngành khoa học, công nghệ, kỹ thuật và toán
  - *Thủ tướng Chính phủ ban hành Quyết định về tín dụng đối với học sinh, sinh viên, học viên thạc sĩ, nghiên cứu sinh học các ngành khoa học, công nghệ,
  - ### 1. Quyết định này quy định về chính sách tín dụng đối với học sinh, sinh viên, học viên thạc sĩ, nghiên cứu sinh học các ngành khoa học, công nghệ
  - ### 2. Các ngành khoa học, công nghệ, kỹ thuật và toán quy định tại Quyết định này bao gồm các ngành, lĩnh vực đào tạo cụ thể sau: khoa học sự sống, k

**Facts in source**: ✅ 2 found, ❌ 0 missing

---

### HOUT-DIR-GEN-03 (Line 33)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `HTCPHT.md`:
  - # Bản lưu inactive — Hỗ trợ sinh viên dân tộc thiểu số thuộc Chương trình mục tiêu quốc gia — Giai đoạn 2021-2025
  - ## Về việc hỗ trợ chi phí đào tạo đại học theo Chương trình mục tiêu quốc gia phát triển kinh tế - xã hội vùng đồng bào dân tộc thiểu số và miền núi g
  - Theo tinh thần Công văn số 3221/SGDĐT-QLCL, ngày 19/11/2025 của Sở Giáo dục và Đào tạo Thành phố Cần Thơ về việc nộp hồ sơ xin hỗ trợ chi phí đào tạo 
  - Sinh viên đang học tại Trường hệ chính quy (kể cả sinh viên mới trúng tuyển vào Trường năm 2025 – Khóa 51) là người dân tộc thiểu số theo Quyết định 1
  - - Giấy xác nhận hộ nghèo, hộ cận nghèo *(tham khảo mẫu đính kèm)*

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-DIR-GEN-04 (Line 34)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Facts in source**: ✅ 0 found, ❌ 2 missing
  Missing: ['trợ cấp xã hội', 'mồ côi']

---

### HOUT-DIR-GEN-05 (Line 35)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `5_don_xin_tam_nghi_hoc_llp.md`:
  - # ĐƠN XIN TẠM NGHỈ HỌC
  - Nay tôi làm đơn này kính gởi đến Ban Giám hiệu Đại học Cần Thơ cho phép tôi được tạm nghỉ học . . . . học kỳ, kể từ học kỳ . . . năm học . . . . - . .

**Facts in source**: ✅ 1 found, ❌ 1 missing
  Missing: ['thời gian học tập tối đa']

---

### HOUT-DIR-GEN-06 (Line 36)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Sinh viên nộp Đơn xin học lại gửi Ban Giám hiệu Đại học Cần Thơ, trong đơn ghi rõ lý do bị đình chỉ, số Quyết định đình chỉ, kèm ý kiến của phụ huynh. | Sinh viên cần nộp Đơn xin học lại kèm theo Quyết định tạm nghỉ học trước đó cho Phòng Đào tạo ít nhất 2 tuần trước khi bắt đầu học kỳ mới. |
| `required_facts` | ["Đơn xin học lại", "Ban Giám hiệu", "Quyết định đình chỉ"] | ["Đơn xin học lại", "Phòng Đào tạo"] |

**Source Evidence**:

- `3_don_xin_hoc_lai_llp.md`:
  - # ĐƠN XIN HỌC LẠI

**Facts in source**: ✅ 1 found, ❌ 1 missing
  Missing: ['Phòng Đào tạo']

---

### HOUT-DIR-GEN-07 (Line 37)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Facts in source**: ✅ 0 found, ❌ 2 missing
  Missing: ['chuyển chương trình đào tạo', 'năm thứ nhất']

---

### HOUT-DIR-GEN-08 (Line 38)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `QD2457_Quy_dinh_xet_mien_va_cong_nhan_diem_HP_hinh_thuc_CQ_nam_2024_llp.md`:
  - **Ban hành Quy định xét miễn và công nhận điểm học phần trong chương trình đào tạo trình độ đại học hình thức chính quy của Trường Đại học Cần Thơ**
  - #### Điều 1. Ban hành kèm theo Quyết định này Quy định xét miễn và công nhận điểm học phần trong chương trình đào tạo trình độ đại học hình thức chính
  - #### Điều 2. Quyết định có hiệu lực thi hành kể từ ngày ký. Quyết định này thay thế Quyết định số 3003/QĐ-ĐHCT ngày 22 tháng 7 năm 2021 của Hiệu trưởn
  - #### Điều 3. Chánh văn phòng Trường, Trưởng phòng Đào tạo, Trưởng phòng Công tác Sinh viên, Trưởng phòng Tài chính, Giám đốc Trung tâm Giáo dục Quốc p
  - ## Xét miễn và công nhận điểm học phần trong chương trình đào tạo trình độ đại học hình thức chính quy

**Facts in source**: ✅ 2 found, ❌ 0 missing

---

### HOUT-DIR-GEN-09 (Line 39)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Facts in source**: ✅ 0 found, ❌ 2 missing
  Missing: ['Đơn đề nghị miễn giảm học phí', 'giấy tờ minh chứng']

---

### HOUT-DIR-GEN-10 (Line 40)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Theo văn bản 3924, sinh viên nộp Đơn đề nghị chuyển chương trình, ngành đào tạo gửi Hiệu trưởng Trường Đại học Cần Thơ, ghi rõ ngành chuyển đến và phương thức chuyển. | Văn bản 3924 hướng dẫn quy trình chuyển trường, chuyển ngành bao gồm kiểm tra hồ sơ trúng tuyển, xét duyệt của hội đồng đào tạo và ban hành quyết định công nhận. |
| `required_facts` | ["3924", "Đơn đề nghị chuyển chương trình", "ngành đào tạo"] | ["3924", "chuyển ngành", "chuyển trường"] |

**Source Evidence**:

- `02_3924KHTH_23-10-2023_llp.md`:
  - Số: 3924 /TB-ĐHCT *Cần Thơ, ngày 23 tháng 10 năm 2023*
  - - Bản sao Giấy chứng nhận kết quả thi tốt nghiệp THPT trong trường hợp sinh viên muốn sử dụng kết quả thi tốt nghiệp để xét chuyển ngành; **hoặc** Bản
  - - Lý do đề nghị chuyển ngành:

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['chuyển trường']

---

### HOUT-MHOP-ACAD-01 (Line 41)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `96_7640101_ThuY.md`:
  - - Ngành: **Thú y** (Veterinary Medicine)
  - - Loại văn bằng: Bác sĩ Thú y
  - - Đơn vị quản lý: Khoa Thú y, Trường Nông nghiệp
  - Mục tiêu chung của chương trình đào tạo ngành Thú y là đào tạo sinh viên trở thành Bác sĩ Thú y có phẩm chất chính trị, đạo đức và sức khoẻ tốt; có tr
  - - a. Đào tạo và giáo dục sinh viên có đủ sức khỏe, phẩm chất đạo đức, chính trị và năng lực chuyên môn để làm việc và quản lý tại các Cơ quan nhà nước
- `quychehocvu.md`:
  - *(Ban hành kèm theo Quyết định số 3266/QĐ-ĐHCT ngày 15 tháng 8 năm 2024 của Hiệu trưởng Trường Đại học Cần Thơ)*
  - ### Điều 5. Thời gian học tập
  - | 4,5 năm                     | 9 năm                                          |
  - | 5 năm                       | 10 năm                                         |
  - Những SV học liên thông (người có bằng tốt nghiệp trình độ cao đẳng hình thức chính quy trở lên; người đã có bằng tốt nghiệp trình độ đại học trở lên)

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['175 tín chỉ']

---

### HOUT-MHOP-ACAD-02 (Line 42)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `62_7580101_KienTruc.md`:
  - - Ngành: **Kiến trúc** (Architecture)
  - - Loại văn bằng: **Kiến trúc sư**
  - Chương trình đào tạo kiến trúc trình độ đại học, định hướng ứng dụng, đào tạo người tốt nghiệp có nền tảng chuyên môn vững vàng, có khả năng vận dụng 
  - Người tốt nghiệp chương trình Kiến trúc trình độ đại học sẽ:
  - - a. Trở thành kiến trúc sư có năng lực chuyên môn vững vàng, có khả năng vận dụng kiến thức khoa học, kỹ thuật và công nghệ trong lĩnh vực kiến trúc 
- `quychehocvu.md`:
  - *(Ban hành kèm theo Quyết định số 3266/QĐ-ĐHCT ngày 15 tháng 8 năm 2024 của Hiệu trưởng Trường Đại học Cần Thơ)*
  - ### Điều 5. Thời gian học tập
  - | 4,5 năm                     | 9 năm                                          |
  - | 5 năm                       | 10 năm                                         |
  - Những SV học liên thông (người có bằng tốt nghiệp trình độ cao đẳng hình thức chính quy trở lên; người đã có bằng tốt nghiệp trình độ đại học trở lên)

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['161 tín chỉ']

---

### HOUT-MHOP-ACAD-03 (Line 43)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `5_don_xin_tam_nghi_hoc_llp.md`:
  - # ĐƠN XIN TẠM NGHỈ HỌC
  - Nay tôi làm đơn này kính gởi đến Ban Giám hiệu Đại học Cần Thơ cho phép tôi được tạm nghỉ học . . . . học kỳ, kể từ học kỳ . . . năm học . . . . - . .

**Facts in source**: ✅ 1 found, ❌ 2 missing
  Missing: ['ít nhất một học kỳ', 'Quy chế học vụ']

---

### HOUT-MHOP-ACAD-04 (Line 44)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `46_7580201_KyThuatXayDung.md`:
  - - Ngành: Kỹ thuật xây dựng (Civil Engineering)
  - - Đơn vị quản lý: Khoa Kỹ thuật Xây dựng, Trường Bách khoa
  - Chương trình đào tạo Kỹ thuật Xây dựng (KTXD) trình độ đại học, định hướng ứng dụng, đào tạo người tốt nghiệp trở thành kỹ sư có nền tảng chuyên môn v
  - - a. Trở thành kỹ sư có năng lực chuyên môn vững vàng, có khả năng vận dụng kiến thức khoa học, kỹ thuật và công nghệ trong lĩnh vực kỹ thuật xây dựng
  - - c. Có khả năng thực hiện nghiên cứu khoa học, ứng dụng và triển khai các giải pháp kỹ thuật công nghệ trong lĩnh vực kỹ thuật xây dựng nhằm giải quy

**Facts in source**: ✅ 1 found, ❌ 2 missing
  Missing: ['chuyển CTĐT', 'năm thứ nhất']

---

### HOUT-MHOP-ACAD-05 (Line 45)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `QD2457_Quy_dinh_xet_mien_va_cong_nhan_diem_HP_hinh_thuc_CQ_nam_2024_llp.md`:
  - 1. Chỉ xem xét và công nhận giá trị chuyển đổi kết quả học tập và khối lượng kiến thức được miễn trừ cho các học phần trong CTĐT sẽ học mà trong CTĐT 
  - | 3                                         | B1                                      | C                       | 4.5-5.0     | 450-595               
  - | 4                                         | B2                                      |                         |             | 5.5-6.5               
  - | 5                                         | C1                                      |                         |             | 7.0-7.5               
  - | 6                                         | C2                                      |                         |             | 8.0-9.0               
- `quychehocvu.md`:
  - Những SV học liên thông (người có bằng tốt nghiệp trình độ cao đẳng hình thức chính quy trở lên; người đã có bằng tốt nghiệp trình độ đại học trở lên)
  - a) Một (01) TC được tính tương đương 50 giờ học tập định mức của SV, bao gồm cả thời gian dự giờ giảng, giờ học có hướng dẫn, tự học, nghiên cứu, trải
  - 2. Một giờ giảng trên lớp (sau đây gọi là *tiết*) được tính bằng 50 phút.
  - - Tổng số TC không đạt trong HK vượt quá 50% khối lượng đã đăng ký học trong HK, hoặc tổng số TC nợ đọng từ đầu khóa học vượt quá 24 TC;
  - | SÁNG     | 1                   | **07:00** – 07:50 | Không          |

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-MHOP-FIN-01 (Line 46)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_2526_MienGiam.md", "MucHocPhi_ChatLuongCao_TienTien.md", "48_7520216_KyThuatDieuKhienVaTuDongHoa.md"] | ["MucHocPhi_2526_MienGiam.md", "MucHocPhi_ChatLuongCao_TienTien.md"] |

**Source Evidence**:

- `MucHocPhi_2526_MienGiam.md`:
  - | 4 | Khối ngành V: Toán và thống kê, máy tính và CN thông tin, CN kỹ thuật, kỹ thuật, sản xuất và chế biến, kiến trúc và xây dựng, nông lâm nghiệp và
  - Các mức cần tra cứu phổ biến gồm: học phần Giáo dục quốc phòng và An ninh và Khối ngành III là **451.000 đồng/tín chỉ**; Khối ngành IV là **487.000 đồ
  - | 5 | Khối ngành VI. Các khối ngành sức khỏe khác | 753.000 |
  - | 6 | Khối ngành VII: Nhân văn, khoa học xã hội và hành vi, báo chí và thông tin, dịch vụ xã hội, du lịch, khách sạn, thể dục thể thao, dịch vụ vận tả

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['cơ sở tính miễn giảm']

---

### HOUT-MHOP-FIN-02 (Line 47)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - Các mức học phí thực tế Khóa 52 thường được tra cứu gồm: Sư phạm Toán học **807.000 đồng/tín chỉ**; Khoa học máy tính **966.000 đồng/tín chỉ**; Kinh d
  - | 62 | 7580101 | V | 758 | Kiến trúc | TN | 165,6 | 1.016.000 |
  - # Bảng học phí thực tế — Chương trình chuẩn Khóa 52 — Năm học 2026-2027
  - **Ngữ cảnh:** Đây là PHỤ LỤC 2 của Văn bản số 2276/ĐHCT-KHTC ngày 17/07/2026 của Giám đốc Đại học Cần Thơ (thay thế văn bản số 423/ĐHCT-KHTC ngày 03/0
  - **Lưu ý:** Mức học phí của khối kiến thức đại cương chung (tất cả các ngành Khóa 52): **695.000 đồng/tín chỉ**.
- `62_7580101_KienTruc.md`:
  - - Ngành: **Kiến trúc** (Architecture)
  - - Loại văn bằng: **Kiến trúc sư**
  - Chương trình đào tạo kiến trúc trình độ đại học, định hướng ứng dụng, đào tạo người tốt nghiệp có nền tảng chuyên môn vững vàng, có khả năng vận dụng 
  - Người tốt nghiệp chương trình Kiến trúc trình độ đại học sẽ:
  - - a. Trở thành kiến trúc sư có năng lực chuyên môn vững vàng, có khả năng vận dụng kiến thức khoa học, kỹ thuật và công nghệ trong lĩnh vực kiến trúc 

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-MHOP-FIN-03 (Line 48)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_2526_MienGiam.md", "16_7380101_Luat_LuatHanhChinh.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md"] | ["MucHocPhi_2526_MienGiam.md", "16_7380101_Luat_LuatHanhChinh.md"] |

**Source Evidence**:

- `MucHocPhi_2526_MienGiam.md`:
  - Các mức cần tra cứu phổ biến gồm: học phần Giáo dục quốc phòng và An ninh và Khối ngành III là **451.000 đồng/tín chỉ**; Khối ngành IV là **487.000 đồ
  - | 2 | Khối ngành III: Kinh doanh và quản lý, pháp luật | 451.000 |
  - | 1  | Giáo dục quốc phòng và An ninh | 8          | 451.000                 |
  - | 1 | Khối ngành I: Khoa học giáo dục và đào tạo giáo viên (chỉ áp dụng cho sinh viên không hưởng chính sách theo Nghị định 116/2020/NĐ-CP) | 451.000 
  - | 4  | Pháp luật đại cương            | 2          |                         |
- `16_7380101_Luat_LuatHanhChinh.md`:
  - - Ngành: **Luật (Law)**
  - - Chuyên ngành: Luật hành chính (Administrative Law)
  - - Đơn vị quản lý: Bộ môn Luật hành chính, Khoa Luật
  - Chương trình đào tạo chuyên ngành Luật hành chính nhằm đào tạo người học trở thành cử nhân luật có phẩm chất chính trị, đạo đức, sức khỏe tốt; được tr
  - Chương trình đào tạo chuyên ngành Luật hành chính trình độ đại học:

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-MHOP-FIN-04 (Line 49)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Ngành Thú y hệ chuẩn K52 có mức học phí 1.016.000 đồng/tín chỉ. Với 175 tín chỉ toàn khóa, tổng chi phí học phí ước tính dựa trên đơn giá này. | Học phí toàn khóa ngành Thú y K52 là 166,6 triệu đồng, đơn giá quy định cho tín chỉ chuyên ngành là 966.000 đồng/tín chỉ. |
| `required_facts` | ["Thú y", "K52", "1.016.000", "175 tín chỉ"] | ["Thú y", "166,6 triệu", "966.000 đồng/tín chỉ"] |
| `gold_sources` | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "96_7640101_ThuY.md", "115_7640101C_ThuY_CTCLC.md"] | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "96_7640101_ThuY.md"] |

**Source Evidence**:

- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - | 81 | 7640101 | V | 764 | Thú y | NN | 166,6 | 1.016.000 |
  - Các mức học phí thực tế Khóa 52 thường được tra cứu gồm: Sư phạm Toán học **807.000 đồng/tín chỉ**; Khoa học máy tính **966.000 đồng/tín chỉ**; Kinh d
  - | 34 | 7460112 | V | 746 | Toán ứng dụng | KH | 131,0 | 966.000 |
  - | 35 | 7460108 | V | 746 | Khoa học dữ liệu | KH | 131,0 | 966.000 |
  - | 36 | 7460201 | V | 746 | Thống kê | KH | 131,0 | 966.000 |
- `96_7640101_ThuY.md`:
  - - Ngành: **Thú y** (Veterinary Medicine)
  - - Loại văn bằng: Bác sĩ Thú y
  - - Đơn vị quản lý: Khoa Thú y, Trường Nông nghiệp
  - Mục tiêu chung của chương trình đào tạo ngành Thú y là đào tạo sinh viên trở thành Bác sĩ Thú y có phẩm chất chính trị, đạo đức và sức khoẻ tốt; có tr
  - - a. Đào tạo và giáo dục sinh viên có đủ sức khỏe, phẩm chất đạo đức, chính trị và năng lực chuyên môn để làm việc và quản lý tại các Cơ quan nhà nước

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-MHOP-FIN-05 (Line 50)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - Các mức học phí thực tế Khóa 52 thường được tra cứu gồm: Sư phạm Toán học **807.000 đồng/tín chỉ**; Khoa học máy tính **966.000 đồng/tín chỉ**; Kinh d
  - | 17 | 7340101 | III | 734 | Quản trị kinh doanh | KT | 114,5 | 844.000 |
  - | 18 | 7340115 | III | 734 | Marketing | KT | 114,5 | 844.000 |
  - | 19 | 7340122 | III | 734 | Thương mại điện tử | KT | 114,5 | 844.000 |
  - | 20 | 7340120 | III | 734 | Kinh doanh quốc tế | KT | 114,5 | 844.000 |
- `MucHocPhi_2526_MienGiam.md`:
  - Các mức cần tra cứu phổ biến gồm: học phần Giáo dục quốc phòng và An ninh và Khối ngành III là **451.000 đồng/tín chỉ**; Khối ngành IV là **487.000 đồ
  - | 1  | Giáo dục quốc phòng và An ninh | 8          | 451.000                 |
  - | 1 | Khối ngành I: Khoa học giáo dục và đào tạo giáo viên (chỉ áp dụng cho sinh viên không hưởng chính sách theo Nghị định 116/2020/NĐ-CP) | 451.000 
  - | 2 | Khối ngành III: Kinh doanh và quản lý, pháp luật | 451.000 |

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['Khối III']

---

### HOUT-MHOP-SCH-01 (Line 51)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `HB_K51_2026.md`:
  - ## Điều 2. Quỹ học bổng khuyến khích học tập của từng khối lớp chuyên ngành được xác định trên cơ sở: Số sinh viên đang học của khối lớp chuyên ngành 
  - # Quyết định — Quỹ học bổng khuyến khích học tập Khóa 51 — Học kỳ 1 năm học 2025-2026
- `03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md`:
  - ## Về việc định mức học bổng khuyến khích học tập áp dụng từ học kỳ 1, năm học 2026-2027

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-MHOP-SCH-02 (Line 52)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `Tài liệu phân bổ quỹ học bổng.md`:
  - | 1   | I                                                                                            | KH GD và đào tạo giáo viên                     
  - | 3   | IV                                                                                           | Khoa học sự sống, khoa học tự nhiên            
  - | 8   | Chương trình tiên tiến, Chương trình chất lượng cao khóa 51 (áp dụng từ học kỳ 2, 2025-2026) |                                                
  - - Quỹ học bổng của lớp: 8.0% số lượng SV x Mức học bổng loại Khá.
  - - Quỹ học bổng của học kỳ đầu tiên của khóa học theo khối lớp chuyên ngành: 8.0% số lượng SV x 7.500.000 đồng/học kỳ;
- `03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md`:
  - Căn cứ Nghị quyết số 99/NQ-HĐT ngày 19 tháng 4 năm 2023 của Hội đồng Trường ban hành Quy chế Tổ chức và hoạt động của Trường Đại học Cần Thơ; Nghị quy
  - Căn cứ Tờ trình số 218/TTr-CTSV, ngày 09 tháng 6 năm 2026 của Phòng Công tác Sinh viên về định mức học bổng khuyến khích áp dụng từ học kỳ 1, năm học 
  - - Tổng quỹ học bổng theo khóa, ngành = Tổng học phí sinh viên cùng khóa, ngành đã đăng ký tại học kỳ liền trước x 8% x 90%.
  - + Quỹ học bổng khuyến khích theo ngành cho học kỳ đầu khóa học: 8% số lượng sinh viên theo từng ngành x **9.000.000 đồng/học kỳ**.
  - *Cần Thơ, ngày 07 tháng 7 năm 2026*

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-MHOP-SCH-03 (Line 53)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `HB_SCIC_2026.md`:
  - # Thông báo — Học bổng SCIC — Năm 2026
  - ## Về việc xét cấp học bổng "SCIC - Nâng bước tài năng trẻ" năm 2026
  - Theo Công văn số 828/ĐTKDV-VP, ngày 18/5/2026 của Tổng Công ty Đầu tư và Kinh doanh vốn Nhà nước (gọi tắt là SCIC) triển khai chương trình học bổng "S
  - Năm 2026, SCIC dành **05 suất** học bổng cho sinh viên theo học tại Trường Công nghệ Thông tin & Truyền thông, Đại học Cần Thơ và giá trị mỗi suất học
  - *Lưu ý: tất cả các loại giấy tờ có liên quan được tập hợp và để vào trong túi đựng hồ sơ, ngoài bìa hồ sơ các ghi rõ **"Học bổng SCIC 2026"**;*
- `87_7340201_TaiChinh-NganHang.md`:
  - - Ngành: **Tài chính - Ngân hàng** (Finance - Banking)
  - - Đơn vị quản lý: Khoa Tài chính - Ngân hàng, Trường Kinh tế
  - Mục tiêu của CTĐT ngành Tài chính - Ngân hàng trình độ đại học hướng đến đào tạo người học trở thành một công dân toàn diện về đức, trí, thể, mỹ; có n
  - - a. Trang bị kiến thức nền tảng về kinh tế, xã hội, luật pháp và kiến thức chuyên môn sâu về tài chính - ngân hàng; bao gồm kiến thức nghiệp vụ và qu
  - Hoàn thành chương trình đào tạo ngành Tài chính - Ngân hàng trình độ đại học, người tốt nghiệp có khả năng:

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['bảng điểm tích lũy']

---

### HOUT-MHOP-SCH-04 (Line 54)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Học bổng SCC yêu cầu sinh viên tích cực tham gia các hoạt động xã hội và bảo vệ môi trường. Học bổng Lương Văn Can ưu tiên sinh viên có hoàn cảnh đặc biệt khó khăn, khuyết tật hoặc dân tộc thiểu số. | Học bổng SCC chú trọng đặc biệt vào tinh thần tích cực tham gia các hoạt động xã hội và bảo vệ môi trường, trong khi học bổng Lương Văn Can ưu tiên cao nhất cho sinh viên có hoàn cảnh đặc biệt khó khă |
| `required_facts` | ["SCC", "hoạt động xã hội", "bảo vệ môi trường", "Lương Văn Can", "hoàn cảnh khó khăn"] | ["SCC", "Lương Văn Can", "8.0", "hoàn cảnh khó khăn", "hoạt động xã hội"] |

**Source Evidence**:

- `HB_SCC.md`:
  - # Thông báo — Học bổng SCC — Năm học 2025-2026
  - ## Về việc trao học bổng Saigon Children’s Charity CIO (SCC), năm học 2025-2026
  - Căn cứ Quyết định số 461/QĐ-UBND ngày 30/01/2026 của Ủy ban nhân dân thành phố Cần Thơ về việc phê duyệt khoản viện trợ dự án “Hỗ trợ học bổng cho sin
  - 5.  | Hồ sơ dự tuyển *(được tập hợp để vào trong túi đựng hồ sơ)* | \* Đơn đề nghị cấp học bổng *(theo mẫu đính kèm)*; \* Bảng điểm từ đầu khóa học đế
- `HB_LuongVanCang.md`:
  - # Thông báo — Học bổng Lương Văn Can — Năm học 2025-2026
  - ## Về việc xét cấp học bổng Lương Văn Can, năm học 2026 – 2027
  - Theo Thông báo của Quỹ Hỗ trợ Tài Năng Lương Văn Can về việc triển khai chương trình Học bổng Lương Văn Can dành cho sinh viên tại các Trường Đại học 
  - Học bổng được xét lại từng học kỳ, nhằm đảm bảo tính minh bạch và công bằng. Ứng viên không đáp ứng được các yêu cầu của Quỹ Hỗ trợ Tài năng Lương Văn
  - Bảng dưới đây mô tả riêng tiêu chí dự tuyển Học bổng Lương Văn Can cho sinh viên đang học và tân sinh viên Khóa 52; ô trống là tiêu chí nguồn không qu

**Facts in source**: ✅ 5 found, ❌ 0 missing

---

### HOUT-MHOP-SCH-05 (Line 55)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md`:
  - - Mức học bổng loại xuất sắc = 1,2 Mức học bổng loại Khá

**Facts in source**: ✅ 1 found, ❌ 2 missing
  Missing: ['120%', 'học phí đã nộp']

---

### HOUT-MHOP-GEN-01 (Line 56)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `VayVon.md`:
  - **4.1. Mức vay hiện hành:** Mức 800.000 đồng/tháng trong hướng dẫn nghiệp vụ năm 2007 là mức lịch sử và không còn dùng làm mức vay hiện hành. Theo Quy
  - - Giấy đề nghị vay vốn kiêm Khế ước nhận nợ (mẫu số 01/TD) kèm Giấy xác nhận của nhà trường (bản chính) hoặc Giấy báo nhập học (bản chính hoặc bản pho
  - a. Người vay viết Giấy đề nghị vay vốn (mẫu số 01/TD) kèm Giấy xác nhận của nhà trường hoặc Giấy báo nhập học gửi cho Tổ TK&VV.
  - chưa là thành viên của Tổ TK&VV thì Tổ TK&VV tại thôn đang hoạt động hiện nay tổ chức kết nạp thành viên bổ sung hoặc thành lập Tổ mới nếu đủ điều kiệ
  - 2.1. Hồ sơ cho vay: Giấy đề nghị vay vốn kiêm khế ước nhận nợ (mẫu số 01/TD) kèm Giấy xác nhận của nhà trường (bản chính) hoặc Giấy báo nhập học (bản 
- `HuongDanXacNhanVayVon.md`:
  - # Hướng dẫn — Đăng ký giấy xác nhận vay vốn trực tuyến — Sinh viên Trường Đại học Cần Thơ
  - Để đăng ký mẫu đơn xác nhận vay vốn (hoặc các loại giấy xác nhận khác), sinh viên thực hiện theo các bước sau:

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['40.000.000 đồng']

---

### HOUT-MHOP-GEN-02 (Line 57)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `HTCPHT.md`:
  - **1. Đối tượng được hỗ trợ chi phí học tập:**
  - **2. Hồ sơ xin được hỗ trợ chi phí học tập:**
  - - Đơn đề nghị Hỗ trợ chi phí học tập *(theo mẫu)*;
  - # Bản lưu inactive — Hỗ trợ sinh viên dân tộc thiểu số thuộc Chương trình mục tiêu quốc gia — Giai đoạn 2021-2025
  - ## Về việc hỗ trợ chi phí đào tạo đại học theo Chương trình mục tiêu quốc gia phát triển kinh tế - xã hội vùng đồng bào dân tộc thiểu số và miền núi g
- `02_246_23-06-2026.md`:
  - # Thông báo — Hồ sơ hỗ trợ chi phí học tập — Học kỳ 3 năm học 2025-2026
  - Hỗ trợ chi phí học tập
  - ## 1. Sinh viên **đã được Hỗ trợ chi phí học tập năm 2025** chỉ cần nộp bổ sung Bản sao có công chứng Giấy chứng nhận hộ nghèo, hộ cận nghèo **năm 202
  - ## 2. Đối với sinh viên **chưa hưởng Hỗ trợ chi phí học tập** thuộc đối tượng dân tộc thiểu số thuộc hộ nghèo, hộ cận nghèo (*Lưu ý: trúng tuyển hệ ch
  - - Đơn đề nghị hỗ trợ chi phí học tập (mẫu đơn theo phụ lục I);

**Facts in source**: ✅ 3 found, ❌ 1 missing
  Missing: ['hộ nghèo/cận nghèo']

---

### HOUT-MHOP-GEN-03 (Line 58)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Sinh viên nộp Đơn đề nghị miễn giảm học phí kèm theo các giấy tờ minh chứng đối tượng chính sách cho Phòng Công tác Sinh viên. | Sinh viên nộp Đơn đề nghị miễn giảm học phí (mẫu số 12) kèm theo các giấy tờ minh chứng đối tượng chính sách trong vòng 30 ngày kể từ khi bắt đầu học kỳ. |
| `required_facts` | ["Đơn đề nghị miễn giảm học phí", "giấy tờ minh chứng", "Phòng Công tác Sinh viên"] | ["miễn 100% học phí", "mẫu số 12", "đầu mỗi học kỳ"] |

**Source Evidence**:

- `mghp.md`:
  - **Ngữ cảnh:** Tài liệu hướng dẫn sinh viên về các đối tượng được miễn, giảm học phí (100%, 70%, 50%) và các loại giấy tờ, hồ sơ cần thiết để nộp cho P
  - ## 2. Đối tượng miễn 100% học phí

**Facts in source**: ✅ 1 found, ❌ 2 missing
  Missing: ['mẫu số 12', 'đầu mỗi học kỳ']

---

### HOUT-MHOP-GEN-04 (Line 59)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `02_3924KHTH_23-10-2023_llp.md`:
  - - Bản sao Giấy chứng nhận kết quả thi tốt nghiệp THPT trong trường hợp sinh viên muốn sử dụng kết quả thi tốt nghiệp để xét chuyển ngành; **hoặc** Bản
  - - Lý do đề nghị chuyển ngành:
  - a) Không đang là SV trình độ năm thứ nhất hoặc năm cuối khóa *(xem Điều 30 của Quy định Công tác Học vụ);*
- `quychehocvu.md`:
  - ### Điều 12. Chuyển cơ sở đào tạo, chuyển ngành, chuyển hình thức học. Trao đổi sinh viên và hợp tác trong đào tạo
  - a) Không đang là SV trình độ năm thứ nhất hoặc năm cuối khóa, không thuộc diện bị xem xét buộc thôi học và còn đủ thời gian học tập theo quy định tại 
  - - Điểm trung bình tích lũy đạt dưới 1,2 đối với SV trình độ năm thứ nhất, dưới 1,4 đối với SV trình độ năm thứ hai, dưới 1,6 đối với SV trình độ năm t
  - | Năm thứ nhất         | Dưới 30                          | Dưới 36                             | Dưới 36                               |

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['không bị cảnh báo']

---

### HOUT-MHOP-GEN-05 (Line 60)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `mghp.md`:
  - | **Khoản 3-Điều 15:** Sinh viên khuyết tật. | 1. Đơn đề nghị miễn, giảm học phí (theo mẫu Phụ lục III).<br>2. Giấy xác nhận khuyết tật do Ủy ban nhân

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['miễn giảm học phí']

---

### HOUT-XDOM-01 (Line 61)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["101_7620301T_NuoiTrongThuySan_CTTT.md", "MucHocPhi_ChatLuongCao_TienTien.md", "100_7620301_NuoiTrongThuySan.md"] | ["101_7620301T_NuoiTrongThuySan_CTTT.md", "MucHocPhi_ChatLuongCao_TienTien.md"] |

**Source Evidence**:

- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - Các mức học phí thực tế thường được tra cứu gồm: Công nghệ thông tin Chất lượng cao Khóa 52 **44 triệu đồng/năm học**; Kinh doanh quốc tế Chất lượng c
  - | 1  | Công nghệ thông tin                        | 882.000 | 914.000 | 989.000 | 1.064.000 | 1.161.000 | 1.254.000 | 1.181.000 | 1.308.000 | 1.438.00
  - | 2  | Kinh doanh quốc tế                          | 770.000 | 839.000 | 951.000 | 1.064.000 | 1.161.000 | 1.254.000 | 1.230.000 | 1.363.000 | 1.363.0
  - | 3  | Công nghệ kỹ thuật hóa học              | 882.000 | 876.000 | 989.000 | 1.064.000 | 1.161.000 | 1.254.000 | 1.181.000 | 1.308.000 | 1.438.000 |
  - | 4  | Kỹ thuật điện                             | 882.000 | 876.000 | 989.000 | 1.064.000 | 1.161.000 | 1.142.000 | 1.181.000 | 1.308.000 | 1.366.000

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-XDOM-02 (Line 62)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `63_7520212_KyThuatYSinh.md`:
  - - Ngành: Kỹ thuật y sinh (Biomedical Engineering)
  - Chương trình đào tạo Kỹ thuật y sinh (KTYS) trình độ đại học đào tạo người tốt nghiệp trở thành kỹ sư ngành Kỹ thuật y sinh có nền tảng chuyên môn vữn
  - - Chương trình đào tạo ngành Kỹ thuật y sinh của Đại học Bách Khoa Hà Nội: https://seee.hust.edu.vn/vi/dao-tao/dao-tao-dai-hoc/et2-ky-thuat-y-sinh-287
  - - Chương trình đào tạo ngành Vật lý kỹ thuật chuyên ngành Kỹ thuật y sinh của Trường Đại học Bách Khoa TP.HCM (đạt chất lượng theo Tiêu chuẩn của BGĐT
  - - Chương trình đào tạo ngành Kỹ thuật y sinh của trường Đại học Sư phạm kỹ thuật TP.HCM (CTĐT đạt chuẩn kiểm định AUN-QA năm 2022): https://aao.hcmute
- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - | 53 | 7520212 | V | 752 | Kỹ thuật y sinh | TN | 150,3 | 966.000 |
  - Các mức học phí thực tế Khóa 52 thường được tra cứu gồm: Sư phạm Toán học **807.000 đồng/tín chỉ**; Khoa học máy tính **966.000 đồng/tín chỉ**; Kinh d
  - | 34 | 7460112 | V | 746 | Toán ứng dụng | KH | 131,0 | 966.000 |
  - | 35 | 7460108 | V | 746 | Khoa học dữ liệu | KH | 131,0 | 966.000 |
  - | 36 | 7460201 | V | 746 | Thống kê | KH | 131,0 | 966.000 |

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-XDOM-03 (Line 63)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `62_7580101_KienTruc.md`:
  - - Ngành: **Kiến trúc** (Architecture)
  - - Loại văn bằng: **Kiến trúc sư**
  - Chương trình đào tạo kiến trúc trình độ đại học, định hướng ứng dụng, đào tạo người tốt nghiệp có nền tảng chuyên môn vững vàng, có khả năng vận dụng 
  - Người tốt nghiệp chương trình Kiến trúc trình độ đại học sẽ:
  - - a. Trở thành kiến trúc sư có năng lực chuyên môn vững vàng, có khả năng vận dụng kiến thức khoa học, kỹ thuật và công nghệ trong lĩnh vực kiến trúc 
- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - Các mức học phí thực tế Khóa 52 thường được tra cứu gồm: Sư phạm Toán học **807.000 đồng/tín chỉ**; Khoa học máy tính **966.000 đồng/tín chỉ**; Kinh d
  - | 62 | 7580101 | V | 758 | Kiến trúc | TN | 165,6 | 1.016.000 |
  - # Bảng học phí thực tế — Chương trình chuẩn Khóa 52 — Năm học 2026-2027
  - **Ngữ cảnh:** Đây là PHỤ LỤC 2 của Văn bản số 2276/ĐHCT-KHTC ngày 17/07/2026 của Giám đốc Đại học Cần Thơ (thay thế văn bản số 423/ĐHCT-KHTC ngày 03/0
  - **Lưu ý:** Mức học phí của khối kiến thức đại cương chung (tất cả các ngành Khóa 52): **695.000 đồng/tín chỉ**.

**Facts in source**: ✅ 3 found, ❌ 1 missing
  Missing: ['161 tín chỉ']

---

### HOUT-XDOM-04 (Line 64)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["49_7520216C_KyThuatDieuKhienVaTuDongHoa_CTCLC.md", "MucHocPhi_ChatLuongCao_TienTien.md", "48_7520216_KyThuatDieuKhienVaTuDongHoa.md"] | ["49_7520216C_KyThuatDieuKhienVaTuDongHoa_CTCLC.md", "MucHocPhi_ChatLuongCao_TienTien.md"] |

**Source Evidence**:

- `49_7520216C_KyThuatDieuKhienVaTuDongHoa_CTCLC.md`:
  - - Ngành: Kỹ thuật điều khiển và Tự động hóa (Control Engineering and Automation (high quality program))
  - Chương trình đào tạo Kỹ thuật điều khiển và tự động hóa (KTĐK&TĐH) trình độ đại học đào tạo người tốt nghiệp trở thành kỹ sư ngành Kỹ thuật điều khiển
  - - Số lượng tín chỉ: 161 tín chỉ
- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - | 12 | Kỹ thuật điều khiển và tự động hóa       |     |     |     |     |     | 33  | 33  | 37  | 41  |
  - | 12 | Kỹ thuật điều khiển và tự động hóa       |         |         |         |           |           | 1.142.000 | 1.118.000 | 1.251.000 | 1.340.000 
  - | 1  | Công nghệ thông tin                        | 882.000 | 914.000 | 989.000 | 1.064.000 | 1.161.000 | 1.254.000 | 1.181.000 | 1.308.000 | 1.438.00
  - | 2  | Kinh doanh quốc tế                          | 770.000 | 839.000 | 951.000 | 1.064.000 | 1.161.000 | 1.254.000 | 1.230.000 | 1.363.000 | 1.363.0
  - | 3  | Công nghệ kỹ thuật hóa học              | 882.000 | 876.000 | 989.000 | 1.064.000 | 1.161.000 | 1.254.000 | 1.181.000 | 1.308.000 | 1.438.000 |

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['44.000.000 đồng/năm']

---

### HOUT-XDOM-05 (Line 65)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["16_7380101_Luat_LuatHanhChinh.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md", "111_7380103_LuatDanSuVaToTungDanSu.md"] | ["16_7380101_Luat_LuatHanhChinh.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md"] |

**Source Evidence**:

- `16_7380101_Luat_LuatHanhChinh.md`:
  - - Ngành: **Luật (Law)**
  - - Chuyên ngành: Luật hành chính (Administrative Law)
  - - Đơn vị quản lý: Bộ môn Luật hành chính, Khoa Luật
  - Chương trình đào tạo chuyên ngành Luật hành chính nhằm đào tạo người học trở thành cử nhân luật có phẩm chất chính trị, đạo đức, sức khỏe tốt; được tr
  - Chương trình đào tạo chuyên ngành Luật hành chính trình độ đại học:
- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - | 26 | 7380101 | III | 738 | Luật | LK | 114,5 | 844.000 |
  - | 27 | 7380103 | III | 738 | Luật dân sự và tố tụng dân sự | LK | 114,5 | 844.000 |
  - | 28 | 7380107 | III | 738 | Luật kinh tế | LK | 114,5 | 844.000 |
  - **Ngữ cảnh:** Đây là PHỤ LỤC 2 của Văn bản số 2276/ĐHCT-KHTC ngày 17/07/2026 của Giám đốc Đại học Cần Thơ (thay thế văn bản số 423/ĐHCT-KHTC ngày 03/0
  - Các mức học phí thực tế Khóa 52 thường được tra cứu gồm: Sư phạm Toán học **807.000 đồng/tín chỉ**; Khoa học máy tính **966.000 đồng/tín chỉ**; Kinh d

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-XDOM-06 (Line 66)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["54_7520114_KyThuatCoDienTu.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md", "114_7540106_DamBaoChatLuongVaAnToanTthucPham.md"] | ["54_7520114_KyThuatCoDienTu.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md"] |

**Source Evidence**:

- `54_7520114_KyThuatCoDienTu.md`:
  - - Ngành: Kỹ thuật cơ điện tử (Mechatronics Engineering)
  - Chương trình đào tạo Kỹ thuật cơ điện tử (KTCĐT) trình độ đại học đào tạo người tốt nghiệp trở thành kỹ sư Cơ điện tử có nền tảng chuyên môn vững vàng
  - - Số lượng tín chỉ: 161 tín chỉ
  - ### Tổng cộng: 161 TC (Bắt buộc: 122 TC; Tự chọn: 39 TC)
- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - | 49 | 7520114 | V | 752 | Kỹ thuật cơ điện tử | TN | 150,3 | 966.000 |
  - Các mức học phí thực tế Khóa 52 thường được tra cứu gồm: Sư phạm Toán học **807.000 đồng/tín chỉ**; Khoa học máy tính **966.000 đồng/tín chỉ**; Kinh d
  - | 34 | 7460112 | V | 746 | Toán ứng dụng | KH | 131,0 | 966.000 |
  - | 35 | 7460108 | V | 746 | Khoa học dữ liệu | KH | 131,0 | 966.000 |
  - | 36 | 7460201 | V | 746 | Thống kê | KH | 131,0 | 966.000 |

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-XDOM-07 (Line 67)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Học phí ngành Tài chính - Ngân hàng CLC K52 là 1.363.000 đồng/tín chỉ. Sinh viên ngành này đủ điều kiện ứng tuyển học bổng SCIC trị giá 10.000.000 đồng/suất. | Học phí ngành Tài chính - Ngân hàng CLC K52 là 38.000.000 đồng/năm. Sinh viên ngành này hoàn toàn đủ điều kiện chuyên ngành để ứng tuyển học bổng SCIC (trị giá 10.000.000 đồng/suất). |
| `required_facts` | ["Tài chính - Ngân hàng", "CLC K52", "1.363.000", "SCIC", "10.000.000"] | ["Tài chính - Ngân hàng", "38.000.000 đồng/năm", "SCIC", "10.000.000 đồng"] |

**Source Evidence**:

- `HB_SCIC_2026.md`:
  - # Thông báo — Học bổng SCIC — Năm 2026
  - ## Về việc xét cấp học bổng "SCIC - Nâng bước tài năng trẻ" năm 2026
  - Theo Công văn số 828/ĐTKDV-VP, ngày 18/5/2026 của Tổng Công ty Đầu tư và Kinh doanh vốn Nhà nước (gọi tắt là SCIC) triển khai chương trình học bổng "S
  - Năm 2026, SCIC dành **05 suất** học bổng cho sinh viên theo học tại Trường Công nghệ Thông tin & Truyền thông, Đại học Cần Thơ và giá trị mỗi suất học
  - *Lưu ý: tất cả các loại giấy tờ có liên quan được tập hợp và để vào trong túi đựng hồ sơ, ngoài bìa hồ sơ các ghi rõ **"Học bổng SCIC 2026"**;*

**Facts in source**: ✅ 2 found, ❌ 2 missing
  Missing: ['Tài chính - Ngân hàng', '38.000.000 đồng/năm']

---

### HOUT-XDOM-08 (Line 68)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Học bổng tân sinh viên kỳ đầu bình quân là 5.000.000 đồng. Ngành Thú y K52 có mức học phí 1.016.000 đồng/tín chỉ. | Học bổng tân sinh viên kỳ đầu bình quân là 5.000.000 đồng. Học phí ngành Thú y K52 toàn khóa là 166,6 triệu đồng (khoảng 16,6 triệu/kỳ cho 10 kỳ), nên mức học bổng 5 triệu không đủ trang trải học phí  |
| `required_facts` | ["5.000.000", "Thú y", "K52", "1.016.000"] | ["5.000.000 đồng", "Thú y", "166,6 triệu đồng", "không đủ"] |
| `gold_sources` | ["HB_TanSinhVien_K52.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md", "115_7640101C_ThuY_CTCLC.md"] | ["HB_TanSinhVien_K52.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md"] |

**Source Evidence**:

- `HB_TanSinhVien_K52.md`:
  - - Hoàn cảnh gia đình: gia đình có hoàn cảnh đặc biệt khó khăn, không đủ điều kiện kinh tế để lo cho học sinh theo học Đại học (Quỹ sẽ đến nhà và địa p
- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - | 81 | 7640101 | V | 764 | Thú y | NN | 166,6 | 1.016.000 |

**Facts in source**: ✅ 3 found, ❌ 1 missing
  Missing: ['5.000.000 đồng']

---

### HOUT-XDOM-09 (Line 69)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["Tài liệu phân bổ quỹ học bổng.md", "03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md"] | ["Tài liệu phân bổ quỹ học bổng.md", "03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md"] |

**Source Evidence**:

- `Tài liệu phân bổ quỹ học bổng.md`:
  - | 1   | I                                                                                            | KH GD và đào tạo giáo viên                     
  - | 3   | IV                                                                                           | Khoa học sự sống, khoa học tự nhiên            
  - | 8   | Chương trình tiên tiến, Chương trình chất lượng cao khóa 51 (áp dụng từ học kỳ 2, 2025-2026) |                                                
  - - Quỹ học bổng của lớp: 8.0% số lượng SV x Mức học bổng loại Khá.
  - - Quỹ học bổng của học kỳ đầu tiên của khóa học theo khối lớp chuyên ngành: 8.0% số lượng SV x 7.500.000 đồng/học kỳ;
- `03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md`:
  - Căn cứ Nghị quyết số 99/NQ-HĐT ngày 19 tháng 4 năm 2023 của Hội đồng Trường ban hành Quy chế Tổ chức và hoạt động của Trường Đại học Cần Thơ; Nghị quy
  - Căn cứ Tờ trình số 218/TTr-CTSV, ngày 09 tháng 6 năm 2026 của Phòng Công tác Sinh viên về định mức học bổng khuyến khích áp dụng từ học kỳ 1, năm học 
  - - Tổng quỹ học bổng theo khóa, ngành = Tổng học phí sinh viên cùng khóa, ngành đã đăng ký tại học kỳ liền trước x 8% x 90%.
  - + Quỹ học bổng khuyến khích theo ngành cho học kỳ đầu khóa học: 8% số lượng sinh viên theo từng ngành x **9.000.000 đồng/học kỳ**.
  - - Mức học bổng loại xuất sắc = 1,2 Mức học bổng loại Khá

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['học phí thực đóng']

---

### HOUT-XDOM-10 (Line 70)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Sinh viên ngành Nuôi trồng thủy sản tiên tiến K52 được xét học bổng khuyến khích nếu đạt kết quả học tập và rèn luyện theo quy định. | Sinh viên ngành NTTS tiên tiến được xét học bổng khuyến khích nếu đạt kết quả học tập và rèn luyện từ loại Khá trở lên; quỹ học bổng của ngành được trích 8% từ tổng học phí sinh viên đã đóng. |
| `required_facts` | ["Nuôi trồng thủy sản tiên tiến", "K52", "học bổng khuyến khích"] | ["Nuôi trồng thủy sản tiên tiến", "8%", "loại Khá trở lên"] |
| `gold_sources` | ["03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md", "Tài liệu phân bổ quỹ học bổng.md", "08_7720203_HoaDuoc.md"] | ["03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md", "Tài liệu phân bổ quỹ học bổng.md"] |

**Source Evidence**:

- `03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md`:
  - Căn cứ Nghị quyết số 99/NQ-HĐT ngày 19 tháng 4 năm 2023 của Hội đồng Trường ban hành Quy chế Tổ chức và hoạt động của Trường Đại học Cần Thơ; Nghị quy
  - Căn cứ Tờ trình số 218/TTr-CTSV, ngày 09 tháng 6 năm 2026 của Phòng Công tác Sinh viên về định mức học bổng khuyến khích áp dụng từ học kỳ 1, năm học 
  - - Tổng quỹ học bổng theo khóa, ngành = Tổng học phí sinh viên cùng khóa, ngành đã đăng ký tại học kỳ liền trước x 8% x 90%.
  - + Quỹ học bổng khuyến khích theo ngành cho học kỳ đầu khóa học: 8% số lượng sinh viên theo từng ngành x **9.000.000 đồng/học kỳ**.
- `Tài liệu phân bổ quỹ học bổng.md`:
  - | 1   | I                                                                                            | KH GD và đào tạo giáo viên                     
  - | 3   | IV                                                                                           | Khoa học sự sống, khoa học tự nhiên            
  - | 8   | Chương trình tiên tiến, Chương trình chất lượng cao khóa 51 (áp dụng từ học kỳ 2, 2025-2026) |                                                
  - - Quỹ học bổng của lớp: 8.0% số lượng SV x Mức học bổng loại Khá.
  - - Quỹ học bổng của học kỳ đầu tiên của khóa học theo khối lớp chuyên ngành: 8.0% số lượng SV x 7.500.000 đồng/học kỳ;

**Facts in source**: ✅ 1 found, ❌ 2 missing
  Missing: ['Nuôi trồng thủy sản tiên tiến', 'loại Khá trở lên']

---

### HOUT-XDOM-11 (Line 71)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["HB_LuongVanCang.md", "02_7310201_ChinhTriHoc.md"] | ["HB_LuongVanCang.md"] |

**Source Evidence**:

- `HB_LuongVanCang.md`:
  - # Thông báo — Học bổng Lương Văn Can — Năm học 2025-2026
  - ## Về việc xét cấp học bổng Lương Văn Can, năm học 2026 – 2027
  - Theo Thông báo của Quỹ Hỗ trợ Tài Năng Lương Văn Can về việc triển khai chương trình Học bổng Lương Văn Can dành cho sinh viên tại các Trường Đại học 
  - Học bổng được xét lại từng học kỳ, nhằm đảm bảo tính minh bạch và công bằng. Ứng viên không đáp ứng được các yêu cầu của Quỹ Hỗ trợ Tài năng Lương Văn
  - Bảng dưới đây mô tả riêng tiêu chí dự tuyển Học bổng Lương Văn Can cho sinh viên đang học và tân sinh viên Khóa 52; ô trống là tiêu chí nguồn không qu

**Facts in source**: ✅ 3 found, ❌ 1 missing
  Missing: ['không phân biệt ngành học']

---

### HOUT-XDOM-12 (Line 72)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `mghp.md`:
  - **Ngữ cảnh:** Tài liệu hướng dẫn sinh viên về các đối tượng được miễn, giảm học phí (100%, 70%, 50%) và các loại giấy tờ, hồ sơ cần thiết để nộp cho P
  - ## 2. Đối tượng miễn 100% học phí
- `MucHocPhi_2526_MienGiam.md`:
  - | 4 | Khối ngành V: Toán và thống kê, máy tính và CN thông tin, CN kỹ thuật, kỹ thuật, sản xuất và chế biến, kiến trúc và xây dựng, nông lâm nghiệp và
- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - | 64 | 7580201 | V | 758 | Kỹ thuật xây dựng | TN | 150,3 | 966.000 |
  - | 65 | 7580202 | V | 758 | Kỹ thuật xây dựng công trình thủy | TN | 150,3 | 966.000 |

**Facts in source**: ✅ 3 found, ❌ 1 missing
  Missing: ['Khối V']

---

### HOUT-XDOM-13 (Line 73)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `MucHocPhi_2526_MienGiam.md`:
  - Các mức cần tra cứu phổ biến gồm: học phần Giáo dục quốc phòng và An ninh và Khối ngành III là **451.000 đồng/tín chỉ**; Khối ngành IV là **487.000 đồ
  - | 2 | Khối ngành III: Kinh doanh và quản lý, pháp luật | 451.000 |
  - | 1  | Giáo dục quốc phòng và An ninh | 8          | 451.000                 |
  - | 1 | Khối ngành I: Khoa học giáo dục và đào tạo giáo viên (chỉ áp dụng cho sinh viên không hưởng chính sách theo Nghị định 116/2020/NĐ-CP) | 451.000 
- `85_7340101_QuanTriKinhDoanh.md`:
  - - Ngành: **Quản trị kinh doanh** (Business Administration)
  - - Đơn vị quản lý: Khoa Quản trị kinh doanh, Trường Kinh tế
  - Chương trình đào tạo ngành Quản trị kinh doanh trình độ đại học nhằm đào tạo những cử nhân có nền tảng kiến thức hiện đại, hệ thống và thực tiễn về qu
  - Hoàn thành chương trình đào tạo ngành Quản trị kinh doanh trình độ đại học, người tốt nghiệp có khả năng:
  - - b. Lập kế hoạch, giao tiếp, làm việc nhóm, và giải quyết hiệu quả vấn đề phức hợp liên quan học tập và nghiên cứu chuyên môn trong lĩnh vực quản trị

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-XDOM-14 (Line 74)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `VayVon.md`:
  - **4.1. Mức vay hiện hành:** Mức 800.000 đồng/tháng trong hướng dẫn nghiệp vụ năm 2007 là mức lịch sử và không còn dùng làm mức vay hiện hành. Theo Quy
  - - Chủ hộ là người đại diện cho hộ gia đình trực tiếp vay vốn và có trách nhiệm trả nợ NHCSXH, là cha hoặc mẹ hoặc người đại diện cho gia đình nhưng đã
  - - Người vay không phải thế chấp tài sản nhưng phải gia nhập và là thành viên Tổ Tiết kiệm và vay vốn (TK&VV) tại thôn, ấp, bản, buôn (gọi chung là thô
  - chưa là thành viên của Tổ TK&VV thì Tổ TK&VV tại thôn đang hoạt động hiện nay tổ chức kết nạp thành viên bổ sung hoặc thành lập Tổ mới nếu đủ điều kiệ
  - 4.2. Đến kỳ giải ngân, người vay mang Chứng minh nhân dân, Khế ước nhận nợ đến điểm giao dịch quy định của NHCSXH để nhận tiền vay. Trường hợp, người 
- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - Các mức học phí thực tế Khóa 52 thường được tra cứu gồm: Sư phạm Toán học **807.000 đồng/tín chỉ**; Khoa học máy tính **966.000 đồng/tín chỉ**; Kinh d
  - | 62 | 7580101 | V | 758 | Kiến trúc | TN | 165,6 | 1.016.000 |

**Facts in source**: ✅ 4 found, ❌ 0 missing

---

### HOUT-XDOM-15 (Line 75)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `HTCPHT.md`:
  - **1. Đối tượng được hỗ trợ chi phí học tập:**
  - **2. Hồ sơ xin được hỗ trợ chi phí học tập:**
  - - Đơn đề nghị Hỗ trợ chi phí học tập *(theo mẫu)*;
  - # Bản lưu inactive — Hỗ trợ sinh viên dân tộc thiểu số thuộc Chương trình mục tiêu quốc gia — Giai đoạn 2021-2025
  - ## Về việc hỗ trợ chi phí đào tạo đại học theo Chương trình mục tiêu quốc gia phát triển kinh tế - xã hội vùng đồng bào dân tộc thiểu số và miền núi g

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['miễn giảm học phí']

---

### HOUT-XDOM-16 (Line 76)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Ngành Nuôi trồng thủy sản chương trình tiên tiến có tổng 163 tín chỉ. Để nộp hồ sơ học bổng SCC, sinh viên cần đạt điểm trung bình tích lũy từ 8.0 trở lên. | Ngành Nuôi trồng thủy sản chương trình tiên tiến có tổng 161 tín chỉ. Để nộp hồ sơ học bổng SCC, sinh viên cần đạt điểm trung bình tích lũy từ 8.0 trở lên. |
| `required_facts` | ["Nuôi trồng thủy sản tiên tiến", "163 tín chỉ", "8.0", "SCC"] | ["Nuôi trồng thủy sản tiên tiến", "161 tín chỉ", "8.0", "SCC"] |

**Source Evidence**:

- `HB_SCC.md`:
  - # Thông báo — Học bổng SCC — Năm học 2025-2026
  - ## Về việc trao học bổng Saigon Children’s Charity CIO (SCC), năm học 2025-2026
  - Căn cứ Quyết định số 461/QĐ-UBND ngày 30/01/2026 của Ủy ban nhân dân thành phố Cần Thơ về việc phê duyệt khoản viện trợ dự án “Hỗ trợ học bổng cho sin

**Facts in source**: ✅ 1 found, ❌ 3 missing
  Missing: ['Nuôi trồng thủy sản tiên tiến', '161 tín chỉ', '8.0']

---

### HOUT-XDOM-17 (Line 77)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `108_7480107_TriTueNhanTao.md`:
  - - Ngành: **Trí tuệ nhân tạo** (Artificial Intelligence)
  - Chương trình đào tạo trình độ đại học ngành trí tuệ nhân tạo đào tạo những kỹ sư có kiến thức tổng quát về trí tuệ nhân tạo và kỹ năng phân tích, vận 
  - - b. Trang bị cho người học kiến thức cơ bản về toán, thống kê, công nghệ thông tin; kiến thức nền tảng khoa học máy tính, trí tuệ nhân tạo và toán ứn
  - - c. Trang bị cho người học kiến thức chuyên sâu về trí tuệ nhân tạo, các hệ thống thông minh. (PEO3)
  - - d. Rèn luyện cho người học năng lực phân tích, vận dụng kiến thức chuyên sâu và kỹ năng để thiết kế và xây dựng các ứng dụng đáp ứng nhu cầu thực ti
- `HB_LuongVanCang.md`:
  - # Thông báo — Học bổng Lương Văn Can — Năm học 2025-2026
  - ## Về việc xét cấp học bổng Lương Văn Can, năm học 2026 – 2027
  - Theo Thông báo của Quỹ Hỗ trợ Tài Năng Lương Văn Can về việc triển khai chương trình Học bổng Lương Văn Can dành cho sinh viên tại các Trường Đại học 
  - Học bổng được xét lại từng học kỳ, nhằm đảm bảo tính minh bạch và công bằng. Ứng viên không đáp ứng được các yêu cầu của Quỹ Hỗ trợ Tài năng Lương Văn
  - Bảng dưới đây mô tả riêng tiêu chí dự tuyển Học bổng Lương Văn Can cho sinh viên đang học và tân sinh viên Khóa 52; ô trống là tiêu chí nguồn không qu

**Facts in source**: ✅ 4 found, ❌ 0 missing

---

### HOUT-XDOM-18 (Line 78)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `61_7510605_LogisticsVaQuanLyChuoiCungUng.md`:
  - - Ngành: Logistics và Quản lý chuỗi cung ứng (Logistics and Supply Chain Management)
  - Chương trình đào tạo ngành logistics và Quản lý chuỗi cung ứng trình độ đại học, đào tạo người tốt nghiệp trở thành cử nhân Logistics và Quản lý chuỗi
  - Chương trình đào tạo ngành Logistics và Quản lý chuỗi cung ứng trình độ đại học:
  - - a. Trở thành chuyên viên và nhân viên Logistics và Quản lý chuỗi cung ứng có năng lực chuyên môn vững vàng, có khả năng vận dụng kiến thức khoa học,
  - - c. Có khả năng thực hiện nghiên cứu khoa học, ứng dụng - chuyển giao và triển khai các giải pháp trong lĩnh vực logistics và quản lý chuỗi cung ứng 
- `03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md`:
  - ## Về việc định mức học bổng khuyến khích học tập áp dụng từ học kỳ 1, năm học 2026-2027
  - - Mức học bổng loại Khá = Số tiền học phí sinh viên đã đóng trong học kỳ liền trước. (*Trường hợp được miễn, giảm, được nhà nước cấp bù học phí thì mứ
  - - Mức học bổng loại giỏi = 1,1 Mức học bổng loại Khá;
  - - Mức học bổng loại xuất sắc = 1,2 Mức học bổng loại Khá

**Facts in source**: ✅ 4 found, ❌ 0 missing

---

### HOUT-XDOM-19 (Line 79)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `96_7640101_ThuY.md`:
  - - Ngành: **Thú y** (Veterinary Medicine)
  - - Loại văn bằng: Bác sĩ Thú y
  - - Đơn vị quản lý: Khoa Thú y, Trường Nông nghiệp
  - Mục tiêu chung của chương trình đào tạo ngành Thú y là đào tạo sinh viên trở thành Bác sĩ Thú y có phẩm chất chính trị, đạo đức và sức khoẻ tốt; có tr
  - - a. Đào tạo và giáo dục sinh viên có đủ sức khỏe, phẩm chất đạo đức, chính trị và năng lực chuyên môn để làm việc và quản lý tại các Cơ quan nhà nước
- `03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md`:
  - Căn cứ Luật Giáo dục đại học ngày 10 tháng 12 năm 2025;
  - Căn cứ Nghị quyết số 99/NQ-HĐT ngày 19 tháng 4 năm 2023 của Hội đồng Trường ban hành Quy chế Tổ chức và hoạt động của Trường Đại học Cần Thơ; Nghị quy
  - - Riêng học bổng **học kỳ đầu tiên** của khóa 52:

**Facts in source**: ✅ 2 found, ❌ 2 missing
  Missing: ['175 tín chỉ', 'từng học kỳ']

---

### HOUT-XDOM-20 (Line 80)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `63_7520212_KyThuatYSinh.md`:
  - - Ngành: Kỹ thuật y sinh (Biomedical Engineering)
  - Chương trình đào tạo Kỹ thuật y sinh (KTYS) trình độ đại học đào tạo người tốt nghiệp trở thành kỹ sư ngành Kỹ thuật y sinh có nền tảng chuyên môn vữn
  - - Chương trình đào tạo ngành Kỹ thuật y sinh của Đại học Bách Khoa Hà Nội: https://seee.hust.edu.vn/vi/dao-tao/dao-tao-dai-hoc/et2-ky-thuat-y-sinh-287
  - - Chương trình đào tạo ngành Vật lý kỹ thuật chuyên ngành Kỹ thuật y sinh của Trường Đại học Bách Khoa TP.HCM (đạt chất lượng theo Tiêu chuẩn của BGĐT
  - - Chương trình đào tạo ngành Kỹ thuật y sinh của trường Đại học Sư phạm kỹ thuật TP.HCM (CTĐT đạt chuẩn kiểm định AUN-QA năm 2022): https://aao.hcmute
- `HB_Vallet_Chi_Tiet.md`:
  - # Thông báo — Học bổng Vallet dành cho sinh viên — Năm 2026
  - BAN ĐIỀU HÀNH HỌC BỔNG VALLET - KHU VỰC PHÍA NAM
  - Học bổng Vallet được ra đời từ hơn 25 năm nay nhằm giúp đỡ các học sinh, sinh viên và các học viên sau đại học Việt Nam có tài năng hoặc xuất sắc tron
  - Quy trình đăng ký, nộp hồ sơ đến quá trình xét tuyển và công bố kết quả của Học bổng Vallet 2026 như sau:
  - **Lưu ý:** Nếu có bất kỳ sự không trung thực trong khai báo hồ sơ trực tuyến, Ban học bổng sẽ: (1) thông báo về trường; (2) không tiếp nhận hồ sơ xin 

**Facts in source**: ✅ 3 found, ❌ 1 missing
  Missing: ['loại Giỏi']

---

### HOUT-COMP-01 (Line 81)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "MucHocPhi_ChatLuongCao_TienTien.md", "44_7580205_KyThuatXayDungCongTrinhGiaoThong.md"] | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "MucHocPhi_ChatLuongCao_TienTien.md"] |

**Source Evidence**:

- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - | 64 | 7580201 | V | 758 | Kỹ thuật xây dựng | TN | 150,3 | 966.000 |
  - | 65 | 7580202 | V | 758 | Kỹ thuật xây dựng công trình thủy | TN | 150,3 | 966.000 |
  - Các mức học phí thực tế Khóa 52 thường được tra cứu gồm: Sư phạm Toán học **807.000 đồng/tín chỉ**; Khoa học máy tính **966.000 đồng/tín chỉ**; Kinh d
  - | 34 | 7460112 | V | 746 | Toán ứng dụng | KH | 131,0 | 966.000 |
  - | 35 | 7460108 | V | 746 | Khoa học dữ liệu | KH | 131,0 | 966.000 |
- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - | 8  | Kỹ thuật xây dựng                         |     | 26  | 28  | 30  | 33  | 33  | 33  | 40  | 41,8|
  - | 8  | Kỹ thuật xây dựng                         |         | 876.000 | 989.000 | 1.064.000 | 1.161.000 | 1.142.000 | 1.073.000 | 1.308.000 | 1.366.000
  - | 1  | Công nghệ thông tin                        | 882.000 | 914.000 | 989.000 | 1.064.000 | 1.161.000 | 1.254.000 | 1.181.000 | 1.308.000 | 1.438.00
  - | 3  | Công nghệ kỹ thuật hóa học              | 882.000 | 876.000 | 989.000 | 1.064.000 | 1.161.000 | 1.254.000 | 1.181.000 | 1.308.000 | 1.438.000 |

**Facts in source**: ✅ 3 found, ❌ 1 missing
  Missing: ['chênh lệch']

---

### HOUT-COMP-02 (Line 82)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "115_7640101C_ThuY_CTCLC.md"] | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md"] |

**Source Evidence**:

- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - | 81 | 7640101 | V | 764 | Thú y | NN | 166,6 | 1.016.000 |
  - Các mức học phí thực tế Khóa 52 thường được tra cứu gồm: Sư phạm Toán học **807.000 đồng/tín chỉ**; Khoa học máy tính **966.000 đồng/tín chỉ**; Kinh d
  - | 62 | 7580101 | V | 758 | Kiến trúc | TN | 165,6 | 1.016.000 |
  - | 34 | 7460112 | V | 746 | Toán ứng dụng | KH | 131,0 | 966.000 |
  - | 35 | 7460108 | V | 746 | Khoa học dữ liệu | KH | 131,0 | 966.000 |

**Facts in source**: ✅ 5 found, ❌ 0 missing

---

### HOUT-COMP-03 (Line 83)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Cả hai ngành Quản trị kinh doanh CLC K52 và Tài chính - Ngân hàng CLC K52 đều có mức học phí là 1.363.000 đồng/tín chỉ. | Cả hai ngành Quản trị kinh doanh CLC K52 và Tài chính - Ngân hàng CLC K52 đều có mức học phí năm học là 38.000.000 đồng/năm (đơn giá tín chỉ chuyên ngành là 1.363.000 đồng/TC). |
| `required_facts` | ["Quản trị kinh doanh", "Tài chính - Ngân hàng", "CLC", "1.363.000"] | ["Quản trị kinh doanh", "Tài chính - Ngân hàng", "CLC", "38.000.000 đồng/năm"] |
| `gold_sources` | ["MucHocPhi_ChatLuongCao_TienTien.md", "85_7340101_QuanTriKinhDoanh.md"] | ["MucHocPhi_ChatLuongCao_TienTien.md"] |

**Source Evidence**:

- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - | 9  | Quản trị kinh doanh                         |     |     |     |     | 33  | 33  | 33  | 40  | 40  |
  - | 9  | Quản trị kinh doanh                         |         |         |         |           | 1.161.000 | 1.142.000 | 1.118.000 | 1.363.000 | 1.363.0
  - **Ngữ cảnh:** Đây là PHỤ LỤC 3 của Văn bản số 2276/ĐHCT-KHTC ngày 17/07/2026 của Giám đốc Đại học Cần Thơ (thay thế văn bản số 423/ĐHCT-KHTC ngày 03/0

**Facts in source**: ✅ 2 found, ❌ 2 missing
  Missing: ['Tài chính - Ngân hàng', '38.000.000 đồng/năm']

---

### HOUT-COMP-04 (Line 84)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_ChatLuongCao_TienTien.md", "106_7420201_CongNgheSinhHoc.md"] | ["MucHocPhi_ChatLuongCao_TienTien.md"] |

**Source Evidence**:

- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - Các mức học phí thực tế thường được tra cứu gồm: Công nghệ thông tin Chất lượng cao Khóa 52 **44 triệu đồng/năm học**; Kinh doanh quốc tế Chất lượng c
  - | 1  | Nuôi trồng thủy sản | 935.000 | 935.000 | 935.000 | 935.000 | 1.211.000 | 1.309.000 | 1.284.000 | 1.422.000 | 1.564.000 |
  - | 2  | Công nghệ sinh học   |     |     |     |     | 33  | 36  | 36  | 40  | 44  |
  - | 2  | Công nghệ sinh học   | 935.000 | 935.000 | 935.000 | 935.000 | 1.191.000 | 1.286.000 | 1.230.000 | 1.363.000 | 1.499.000 |

**Facts in source**: ✅ 4 found, ❌ 0 missing

---

### HOUT-COMP-05 (Line 85)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Ngành Kỹ thuật điều khiển và tự động hóa CLC Khóa 51 có mức học phí 1.251.000 đồng/tín chỉ, Khóa 52 có mức học phí cao hơn. Mức học phí tăng qua từng khóa. | Kỹ thuật điều khiển và tự động hóa CLC Khóa 51 là 40.000.000 đồng/năm, Khóa 52 là 44.000.000 đồng/năm. K52 tăng 4.000.000 đồng/năm (tăng 10%). |
| `required_facts` | ["Kỹ thuật điều khiển và tự động hóa", "K51", "1.251.000", "K52"] | ["Kỹ thuật điều khiển và tự động hóa", "K51", "40 triệu", "K52", "44 triệu", "4 triệu"] |
| `gold_sources` | ["MucHocPhi_ChatLuongCao_TienTien.md", "48_7520216_KyThuatDieuKhienVaTuDongHoa.md"] | ["MucHocPhi_ChatLuongCao_TienTien.md"] |

**Source Evidence**:

- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - | 12 | Kỹ thuật điều khiển và tự động hóa       |     |     |     |     |     | 33  | 33  | 37  | 41  |
  - | 12 | Kỹ thuật điều khiển và tự động hóa       |         |         |         |           |           | 1.142.000 | 1.118.000 | 1.251.000 | 1.340.000 
  - Các mức học phí thực tế thường được tra cứu gồm: Công nghệ thông tin Chất lượng cao Khóa 52 **44 triệu đồng/năm học**; Kinh doanh quốc tế Chất lượng c
  - | TT | Ngành                                        | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |
  - | TT | Ngành                  | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |

**Facts in source**: ✅ 6 found, ❌ 0 missing

---

### HOUT-COMP-06 (Line 86)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `61_7510605_LogisticsVaQuanLyChuoiCungUng.md`:
  - - Ngành: Logistics và Quản lý chuỗi cung ứng (Logistics and Supply Chain Management)
  - Chương trình đào tạo ngành logistics và Quản lý chuỗi cung ứng trình độ đại học, đào tạo người tốt nghiệp trở thành cử nhân Logistics và Quản lý chuỗi
  - Chương trình đào tạo ngành Logistics và Quản lý chuỗi cung ứng trình độ đại học:
  - - a. Trở thành chuyên viên và nhân viên Logistics và Quản lý chuỗi cung ứng có năng lực chuyên môn vững vàng, có khả năng vận dụng kiến thức khoa học,
  - - b. Phát triển năng lực tư duy sáng tạo và học tập suốt đời, chủ động cập nhật kiến thức mới, thích ứng với sự phát triển của khoa học – công nghệ và
- `108_7480107_TriTueNhanTao.md`:
  - - Ngành: **Trí tuệ nhân tạo** (Artificial Intelligence)
  - Chương trình đào tạo trình độ đại học ngành trí tuệ nhân tạo đào tạo những kỹ sư có kiến thức tổng quát về trí tuệ nhân tạo và kỹ năng phân tích, vận 
  - - b. Trang bị cho người học kiến thức cơ bản về toán, thống kê, công nghệ thông tin; kiến thức nền tảng khoa học máy tính, trí tuệ nhân tạo và toán ứn
  - - c. Trang bị cho người học kiến thức chuyên sâu về trí tuệ nhân tạo, các hệ thống thông minh. (PEO3)
  - - d. Rèn luyện cho người học năng lực phân tích, vận dụng kiến thức chuyên sâu và kỹ năng để thiết kế và xây dựng các ứng dụng đáp ứng nhu cầu thực ti

**Facts in source**: ✅ 5 found, ❌ 0 missing

---

### HOUT-COMP-07 (Line 87)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `96_7640101_ThuY.md`:
  - - Ngành: **Thú y** (Veterinary Medicine)
  - - Loại văn bằng: Bác sĩ Thú y
  - - Đơn vị quản lý: Khoa Thú y, Trường Nông nghiệp
  - Mục tiêu chung của chương trình đào tạo ngành Thú y là đào tạo sinh viên trở thành Bác sĩ Thú y có phẩm chất chính trị, đạo đức và sức khoẻ tốt; có tr
  - - a. Đào tạo và giáo dục sinh viên có đủ sức khỏe, phẩm chất đạo đức, chính trị và năng lực chuyên môn để làm việc và quản lý tại các Cơ quan nhà nước
- `102_7620305_QuanLyThuySan.md`:
  - - Ngành: **Quản lý thủy sản (Fisheries Management)**
  - Đào tạo kỹ sư Quản lý thủy sản cung cấp cho người học hệ thống kiến thức cơ bản và chuyên môn sâu về quản lý trong lĩnh vực nuôi trồng, khai thác và c
  - - Chuẩn Chương trình đào tạo ngành Quản lý thủy sản Trường Đại học Nha Trang (ban hành theo QĐ số 1201/QĐ-ĐHNT ngày 11 tháng 11 năm 2021; Mã ngành 762
  - - Chương trình đào tạo bậc Thạc sĩ ngành Khoa học thuỷ sản trong Kinh tế và quản lý thủy sản, Indian Institute of Management và chương trình đào tạo Đ
  - * **Các mô hình quản lý thủy sản** (Mã số: TS484)

**Facts in source**: ✅ 4 found, ❌ 1 missing
  Missing: ['175 tín chỉ']

---

### HOUT-COMP-08 (Line 88)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_2526_MienGiam.md", "94_7620103_KhoaHocDat_QuanLyDatVaCongNghePhanBon.md"] | ["MucHocPhi_2526_MienGiam.md"] |

**Source Evidence**:

- `MucHocPhi_2526_MienGiam.md`:
  - Các mức cần tra cứu phổ biến gồm: học phần Giáo dục quốc phòng và An ninh và Khối ngành III là **451.000 đồng/tín chỉ**; Khối ngành IV là **487.000 đồ
  - | 4 | Khối ngành V: Toán và thống kê, máy tính và CN thông tin, CN kỹ thuật, kỹ thuật, sản xuất và chế biến, kiến trúc và xây dựng, nông lâm nghiệp và
  - | 5 | Khối ngành VI. Các khối ngành sức khỏe khác | 753.000 |
  - | 6 | Khối ngành VII: Nhân văn, khoa học xã hội và hành vi, báo chí và thông tin, dịch vụ xã hội, du lịch, khách sạn, thể dục thể thao, dịch vụ vận tả
  - | 2 | Khối ngành III: Kinh doanh và quản lý, pháp luật | 451.000 |

**Facts in source**: ✅ 5 found, ❌ 0 missing

---

### HOUT-COMP-09 (Line 89)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md`:
  - - Mức học bổng loại Khá = Số tiền học phí sinh viên đã đóng trong học kỳ liền trước. (*Trường hợp được miễn, giảm, được nhà nước cấp bù học phí thì mứ
  - - Mức học bổng loại giỏi = 1,1 Mức học bổng loại Khá;
  - - Mức học bổng loại xuất sắc = 1,2 Mức học bổng loại Khá

**Facts in source**: ✅ 5 found, ❌ 0 missing

---

### HOUT-COMP-10 (Line 90)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "111_7380103_LuatDanSuVaToTungDanSu.md"] | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md"] |

**Source Evidence**:

- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - | 26 | 7380101 | III | 738 | Luật | LK | 114,5 | 844.000 |
  - | 27 | 7380103 | III | 738 | Luật dân sự và tố tụng dân sự | LK | 114,5 | 844.000 |
  - | 28 | 7380107 | III | 738 | Luật kinh tế | LK | 114,5 | 844.000 |
  - Các mức học phí thực tế Khóa 52 thường được tra cứu gồm: Sư phạm Toán học **807.000 đồng/tín chỉ**; Khoa học máy tính **966.000 đồng/tín chỉ**; Kinh d
  - | 17 | 7340101 | III | 734 | Quản trị kinh doanh | KT | 114,5 | 844.000 |

**Facts in source**: ✅ 4 found, ❌ 1 missing
  Missing: ['thấp hơn 35,8 triệu']

---

### HOUT-TEMP-01 (Line 91)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - | TT | Ngành                                        | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |
  - | TT | Ngành                  | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |
  - | Khóa            | K44     | K45     | K46     | K47     | K48     | K49     | K50     | K51     | K52     |
  - | TT | Ngành                                        | K44     | K45     | K46     | K47       | K48       | K49       | K50       | K51       | K52   
  - | TT | Ngành                  | K44     | K45     | K46     | K47     | K48       | K49       | K50       | K51       | K52       |

**Facts in source**: ✅ 4 found, ❌ 0 missing

---

### HOUT-TEMP-02 (Line 92)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_ChatLuongCao_TienTien.md", "76_7340120_KinhDoanhQuocTe.md"] | ["MucHocPhi_ChatLuongCao_TienTien.md"] |

**Source Evidence**:

- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - Các mức học phí thực tế thường được tra cứu gồm: Công nghệ thông tin Chất lượng cao Khóa 52 **44 triệu đồng/năm học**; Kinh doanh quốc tế Chất lượng c
  - | 2  | Kinh doanh quốc tế                          | 22  | 24  | 27  | 30  | 33  | 36  | 36  | 40  | 40  |
  - | 2  | Kinh doanh quốc tế                          | 770.000 | 839.000 | 951.000 | 1.064.000 | 1.161.000 | 1.254.000 | 1.230.000 | 1.363.000 | 1.363.0
  - **Ngữ cảnh:** Đây là PHỤ LỤC 3 của Văn bản số 2276/ĐHCT-KHTC ngày 17/07/2026 của Giám đốc Đại học Cần Thơ (thay thế văn bản số 423/ĐHCT-KHTC ngày 03/0
  - | 1  | Công nghệ thông tin                        | 25  | 26  | 28  | 30  | 33  | 36  | 36  | 40  | 44  |

**Facts in source**: ✅ 5 found, ❌ 0 missing

---

### HOUT-TEMP-03 (Line 93)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - Các mức học phí thực tế thường được tra cứu gồm: Công nghệ thông tin Chất lượng cao Khóa 52 **44 triệu đồng/năm học**; Kinh doanh quốc tế Chất lượng c
  - | TT | Ngành                                        | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |
  - | TT | Ngành                  | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |
  - | Khóa            | K44     | K45     | K46     | K47     | K48     | K49     | K50     | K51     | K52     |
  - | TT | Ngành                                        | K44     | K45     | K46     | K47       | K48       | K49       | K50       | K51       | K52   

**Facts in source**: ✅ 4 found, ❌ 0 missing

---

### HOUT-TEMP-04 (Line 94)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `quychehocvu.md`:
  - *(Ban hành kèm theo Quyết định số 3266/QĐ-ĐHCT ngày 15 tháng 8 năm 2024 của Hiệu trưởng Trường Đại học Cần Thơ)*
  - 2. Quy định này áp dụng đối với SV các ngành, khóa đào tạo trình độ đại học hình thức chính quy của Trường Đại học Cần Thơ (*ĐHCT*).
  - ### Điều 2. Sinh viên
  - Những SV học liên thông (người có bằng tốt nghiệp trình độ cao đẳng hình thức chính quy trở lên; người đã có bằng tốt nghiệp trình độ đại học trở lên)
  - 1. Mỗi năm học được tổ chức thành 03 HK gọi là Học kỳ 1, Học kỳ 2 và Học kỳ 3.
- `QD1813_QD_ban_hanh_Quy_dinh_cong_tac_hoc_vu_2021.md`:
  - *Cần Thơ, ngày 18 tháng 6 năm 2021*
  - *Căn cứ Luật Giáo dục đại học ngày 18 tháng 6 năm 2012 và Luật sửa đổi, bổ sung một số điều của Luật Giáo dục đại học ngày 19 tháng 11 năm 2018;*
  - *Căn cứ Nghị quyết số 29/NQ-HĐT ngày 19 tháng 5 năm 2020 của Hội đồng trường Trường Đại học Cần Thơ ban hành Quy chế tổ chức và hoạt động của Trường Đ
  - *Căn cứ Văn bản hợp nhất số 17/VBHN-BGDĐT ngày 15 tháng 5 năm 2014 của Bộ trưởng Bộ Giáo dục và Đào tạo Quyết định ban hành Quy chế đào tạo đại học và
  - *Căn cứ Thông tư số 16/2015/TT-BGDĐT ngày 12 tháng 8 năm 2015 của Bộ trưởng Bộ Giáo dục và Đào tạo ban hành Quy chế đánh giá kết quả rèn luyện của ngư

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['Quy chế học vụ']

---

### HOUT-TEMP-05 (Line 95)

**Severity**: `CRITICAL`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `reference_answer` | Ngành Thú y CLC có mức học phí thay đổi qua từng khóa, mức học phí tính theo đồng/tín chỉ tăng dần từ Khóa 50 đến Khóa 52. | Ngành Thú y CLC Khóa 50 có học phí là 39.000.000 đồng/năm, trong khi Khóa 52 có học phí là 44.000.000 đồng/năm (tăng 5.000.000 đồng/năm). |
| `required_facts` | ["Thú y CLC", "K50", "K52", "tăng dần"] | ["Thú y", "CLC", "K50", "39 triệu", "K52", "44 triệu"] |
| `gold_sources` | ["MucHocPhi_ChatLuongCao_TienTien.md", "115_7640101C_ThuY_CTCLC.md"] | ["MucHocPhi_ChatLuongCao_TienTien.md"] |

**Source Evidence**:

- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - Các mức học phí thực tế thường được tra cứu gồm: Công nghệ thông tin Chất lượng cao Khóa 52 **44 triệu đồng/năm học**; Kinh doanh quốc tế Chất lượng c
  - | 15 | Thú y                                        |     |     |     |     |     |     |     | 40  | 41,8|
  - | 15 | Thú y                                        |         |         |         |           |           |           |           | 1.412.000 | 1.475.
  - **Ngữ cảnh:** Đây là PHỤ LỤC 3 của Văn bản số 2276/ĐHCT-KHTC ngày 17/07/2026 của Giám đốc Đại học Cần Thơ (thay thế văn bản số 423/ĐHCT-KHTC ngày 03/0
  - | TT | Ngành                                        | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |

**Facts in source**: ✅ 6 found, ❌ 0 missing

---

### HOUT-ADVS-01 (Line 96)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "MucHocPhi_ChatLuongCao_TienTien.md", "MucHocPhi_QuyDinhChung.md"] | ["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "MucHocPhi_ChatLuongCao_TienTien.md"] |

**Source Evidence**:

- `MucHocPhi_DaiHocChinhQuy_Khoa52.md`:
  - **Ngữ cảnh:** Đây là PHỤ LỤC 2 của Văn bản số 2276/ĐHCT-KHTC ngày 17/07/2026 của Giám đốc Đại học Cần Thơ (thay thế văn bản số 423/ĐHCT-KHTC ngày 03/0
- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - Các bảng dưới đây là mức học phí thực tế theo tín chỉ của chương trình Chất lượng cao và chương trình Tiên tiến tại Đại học Cần Thơ năm học 2026-2027.
  - ## II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ)
  - **Ngữ cảnh:** Đây là PHỤ LỤC 3 của Văn bản số 2276/ĐHCT-KHTC ngày 17/07/2026 của Giám đốc Đại học Cần Thơ (thay thế văn bản số 423/ĐHCT-KHTC ngày 03/0

**Facts in source**: ✅ 2 found, ❌ 1 missing
  Missing: ['tùy thuộc vào ngành học']

---

### HOUT-ADVS-02 (Line 97)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Facts in source**: ✅ 0 found, ❌ 3 missing
  Missing: ['điểm học tập', 'điểm rèn luyện', 'loại Khá trở lên']

---

### HOUT-ADVS-03 (Line 98)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `HTCPHT.md`:
  - **1. Đối tượng được hỗ trợ chi phí học tập:**
  - **2. Hồ sơ xin được hỗ trợ chi phí học tập:**
  - - Đơn đề nghị Hỗ trợ chi phí học tập *(theo mẫu)*;
- `mghp.md`:
  - | **Khoản 4-Điều 15:** Người học từ 16 tuổi đến 22 tuổi đang học giáo dục đại học văn bằng thứ nhất thuộc đối tượng hưởng trợ cấp xã hội hàng tháng (s
- `VayVon.md`:
  - # Hướng dẫn — Quy trình vay vốn học sinh, sinh viên theo Quyết định 157/2007/QĐ-TTg — Có cập nhật mức vay năm 2022
  - ### 1. Người vay vốn tại NHCSXH:
  - - Chủ hộ là người đại diện cho hộ gia đình trực tiếp vay vốn và có trách nhiệm trả nợ NHCSXH, là cha hoặc mẹ hoặc người đại diện cho gia đình nhưng đã
  - - Học sinh, sinh viên mồ côi cả cha lẫn mẹ hoặc chỉ mồ côi cha hoặc mẹ nhưng người còn lại không có khả năng lao động được trực tiếp vay vốn tại NHCSX
  - ### 2. Nơi cư trú hợp pháp của người vay vốn là nơi người đó thường xuyên sinh sống. Trường hợp không xác định được nơi cư trú của người vay vốn theo 
- `02_246_23-06-2026.md`:
  - # Thông báo — Hồ sơ hỗ trợ chi phí học tập — Học kỳ 3 năm học 2025-2026
  - Hỗ trợ chi phí học tập
  - ## 1. Sinh viên **đã được Hỗ trợ chi phí học tập năm 2025** chỉ cần nộp bổ sung Bản sao có công chứng Giấy chứng nhận hộ nghèo, hộ cận nghèo **năm 202
  - ## 2. Đối với sinh viên **chưa hưởng Hỗ trợ chi phí học tập** thuộc đối tượng dân tộc thiểu số thuộc hộ nghèo, hộ cận nghèo (*Lưu ý: trúng tuyển hệ ch
  - - Đơn đề nghị hỗ trợ chi phí học tập (mẫu đơn theo phụ lục I);

**Facts in source**: ✅ 3 found, ❌ 1 missing
  Missing: ['miễn giảm học phí']

---

### HOUT-ADVS-04 (Line 99)

**Severity**: `UNCHANGED`

Không thay đổi nội dung (chỉ đổi `review_status` → `verified`).

**Source Evidence**:

- `quychehocvu.md`:
  - Sau thời hạn đóng học phí, SV không đóng học phí sẽ bị hủy kết quả học tập những học phần nợ học phí trong HK đó và buộc phải đóng học phí còn nợ cùng
  - a) Không đang là SV trình độ năm thứ nhất hoặc năm cuối khóa, không thuộc diện bị xem xét buộc thôi học và còn đủ thời gian học tập theo quy định tại 
  - ### Điều 18. Nghỉ học tạm thời, cảnh báo học tập, đình chỉ học tập và buộc thôi học
  - d) Vì lý do cá nhân (hoàn cảnh gia đình neo đơn, việc riêng,...). Trường hợp này chỉ giải quyết khi SV đã học ít nhất 1 HK ở Trường ĐHCT, không thuộc 
  - 5. Buộc thôi học trong các trường hợp:

**Facts in source**: ✅ 3 found, ❌ 0 missing

---

### HOUT-ADVS-05 (Line 100)

**Severity**: `MEDIUM`

| Field | Before | After |
|---|---|---|
| `review_status` | approved | verified |
| `gold_sources` | ["MucHocPhi_ChatLuongCao_TienTien.md", "109_7480102C_MangMayTinhVaTruyenThongDuLieu_CTCLC.md"] | ["MucHocPhi_ChatLuongCao_TienTien.md"] |

**Source Evidence**:

- `MucHocPhi_ChatLuongCao_TienTien.md`:
  - Các bảng dưới đây là mức học phí thực tế theo tín chỉ của chương trình Chất lượng cao và chương trình Tiên tiến tại Đại học Cần Thơ năm học 2026-2027.
  - ## II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ)
  - # Bảng học phí thực tế — Chương trình Chất lượng cao và Tiên tiến — Năm học 2026-2027
  - **Ngữ cảnh:** Đây là PHỤ LỤC 3 của Văn bản số 2276/ĐHCT-KHTC ngày 17/07/2026 của Giám đốc Đại học Cần Thơ (thay thế văn bản số 423/ĐHCT-KHTC ngày 03/0
  - Các mức học phí thực tế thường được tra cứu gồm: Công nghệ thông tin Chất lượng cao Khóa 52 **44 triệu đồng/năm học**; Kinh doanh quốc tế Chất lượng c

**Facts in source**: ✅ 3 found, ❌ 1 missing
  Missing: ['theo năm']

---
