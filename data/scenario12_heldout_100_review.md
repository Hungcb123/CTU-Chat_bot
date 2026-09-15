# Scenario 1–2: Balanced Held-Out Benchmark (100 Cases) Audit & Review

> **Symmetric Twin Benchmark Protocol**:
> - Phân bổ đồng đều: 4 Specialist Domains x 25 queries = 100 queries.
> - Phân bổ phong cách: 50 câu văn phong chuẩn (Formal) + 50 câu sinh viên tự nhiên (Colloquial Paraphrase).
> - Disjoint Clause/Entity Split: 100% không trùng lặp thực thể ngành/gói học bổng/điều khoản quy chế với Dev (100 câu).
> - Tất cả các trường đã được xác thực từ văn bản pháp quy gốc của Trường Đại học Cần Thơ.

## Quota Summary

- `Academic Specialist`: 25 (13 Formal + 12 Colloquial)
- `Financial Specialist`: 25 (13 Formal + 12 Colloquial)
- `Scholarship Specialist`: 25 (13 Formal + 12 Colloquial)
- `General Specialist`: 25 (13 Formal + 12 Colloquial)
- **Total**: 100 approved held-out cases.

---

## [001/100] HOUT-ACAD-01 — ACADEMIC (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Chương trình đào tạo ngành Trí tuệ nhân tạo tại Trường Đại học Cần Thơ có tổng cộng bao nhiêu tín chỉ?

**Reference answer:** Chương trình đào tạo ngành Trí tuệ nhân tạo tại Trường Đại học Cần Thơ có tổng cộng 161 tín chỉ (Bắt buộc: 113 tín chỉ, Tự chọn: 48 tín chỉ).

**Required facts:** `["Trí tuệ nhân tạo", "161 tín chỉ", "113", "48"]`

**Gold sources:** `["108_7480107_TriTueNhanTao.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 113 TC; Tự chọn: 48 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.375`

---

## [002/100] HOUT-ACAD-02 — ACADEMIC (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Chương trình đào tạo ngành Logistics và Quản lý chuỗi cung ứng có tổng cộng bao nhiêu tín chỉ?

**Reference answer:** Chương trình đào tạo ngành Logistics và Quản lý chuỗi cung ứng có tổng cộng 141 tín chỉ với thời gian đào tạo 4 năm.

**Required facts:** `["Logistics và Quản lý chuỗi cung ứng", "141 tín chỉ", "4 năm"]`

**Gold sources:** `["61_7510605_LogisticsVaQuanLyChuoiCungUng.md"]`

**Evidence excerpt:** - Ngành: Logistics và Quản lý chuỗi cung ứng (Logistics and Supply Chain Management)
- Mã ngành: 7510605
- Số lượng tín chỉ: 141 tín chỉ
- Thời gian đào tạo: 4 năm

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.173913`

---

## [003/100] HOUT-ACAD-03 — ACADEMIC (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Chương trình đào tạo ngành Đảm bảo chất lượng và an toàn thực phẩm tại Trường Đại học Cần Thơ có bao nhiêu tín chỉ bắt buộc?

**Reference answer:** Chương trình đào tạo ngành Đảm bảo chất lượng và an toàn thực phẩm có tổng cộng 161 tín chỉ, trong đó có 117 tín chỉ bắt buộc và 44 tín chỉ tự chọn.

**Required facts:** `["161 tín chỉ", "117 tín chỉ bắt buộc", "44 tín chỉ tự chọn"]`

**Gold sources:** `["114_7540106_DamBaoChatLuongVaAnToanTthucPham.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 117 TC; Tự chọn: 44 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.085714`

---

## [004/100] HOUT-ACAD-04 — ACADEMIC (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Chương trình đào tạo ngành Nuôi trồng thủy sản hệ chuẩn yêu cầu tích lũy tổng cộng bao nhiêu tín chỉ?

**Reference answer:** Chương trình đào tạo ngành Nuôi trồng thủy sản hệ chuẩn yêu cầu tích lũy tổng cộng 161 tín chỉ.

**Required facts:** `["Nuôi trồng thủy sản", "161 tín chỉ"]`

**Gold sources:** `["100_7620301_NuoiTrongThuySan.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 115 TC; Tự chọn: 46 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.115385`

---

## [005/100] HOUT-ACAD-05 — ACADEMIC (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Tổng số tín chỉ cần hoàn thành của chương trình đào tạo ngành Công nghệ sinh học là bao nhiêu?

**Reference answer:** Chương trình đào tạo ngành Công nghệ sinh học yêu cầu hoàn thành tổng cộng 161 tín chỉ.

**Required facts:** `["Công nghệ sinh học", "161 tín chỉ"]`

**Gold sources:** `["106_7420201_CongNgheSinhHoc.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 116 TC; Tự chọn: 45 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.12`

---

## [006/100] HOUT-ACAD-06 — ACADEMIC (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Ngành Thú y hệ chuẩn tại Đại học Cần Thơ đào tạo trong thời gian bao lâu và có bao nhiêu tín chỉ?

**Reference answer:** Ngành Thú y tại Đại học Cần Thơ có thời gian đào tạo là 5 năm với khối lượng kiến trúc chương trình là 175 tín chỉ.

**Required facts:** `["Thú y", "5 năm", "175"]`

**Gold sources:** `["96_7640101_ThuY.md", "quychehocvu.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`

**Evidence excerpt:** - Thời gian đào tạo: 5 năm
- Khối lượng chương trình đào tạo: 175 tín chỉ

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.035714`

---

## [007/100] HOUT-ACAD-07 — ACADEMIC (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Chương trình đào tạo ngành Quản lý thủy sản có tổng cộng bao nhiêu tín chỉ tích lũy?

**Reference answer:** Chương trình đào tạo ngành Quản lý thủy sản có tổng cộng 141 tín chỉ.

**Required facts:** `["Quản lý thủy sản", "141 tín chỉ"]`

**Gold sources:** `["102_7620305_QuanLyThuySan.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 141 TC (Bắt buộc: 105 TC; Tự chọn: 36 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.208333`

---

## [008/100] HOUT-ACAD-08 — ACADEMIC (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Chương trình đào tạo ngành Công nghệ Sau thu hoạch có tổng số tín chỉ bắt buộc là bao nhiêu?

**Reference answer:** Chương trình đào tạo ngành Công nghệ Sau thu hoạch có 116 tín chỉ bắt buộc trên tổng số 161 tín chỉ toàn khóa.

**Required facts:** `["Công nghệ Sau thu hoạch", "116 tín chỉ bắt buộc", "161"]`

**Gold sources:** `["103_7540104_CongNgheSauThuHoach.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 116 TC; Tự chọn: 45 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.12`

---

## [009/100] HOUT-ACAD-09 — ACADEMIC (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Ngành Công nghệ thực phẩm chất lượng cao có tổng khối lượng chương trình đào tạo là bao nhiêu tín chỉ?

**Reference answer:** Ngành Công nghệ thực phẩm chất lượng cao có tổng khối lượng chương trình là 161 tín chỉ.

**Required facts:** `["Công nghệ thực phẩm chất lượng cao", "161 tín chỉ"]`

**Gold sources:** `["105_7540101C_CongNgheThucPham_CTCLC.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 120 TC; Tự chọn: 41 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.03125`

---

## [010/100] HOUT-ACAD-10 — ACADEMIC (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Chương trình tiên tiến ngành Công nghệ sinh học đào tạo bao nhiêu tín chỉ toàn khóa?

**Reference answer:** Chương trình tiên tiến ngành Công nghệ sinh học đào tạo tổng cộng 161 tín chỉ.

**Required facts:** `["Công nghệ sinh học", "tiên tiến", "161 tín chỉ"]`

**Gold sources:** `["107_7420201T_CongNgheSinhHoc_CTTT.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 119 TC; Tự chọn: 42 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.086957`

---

## [011/100] HOUT-ACAD-11 — ACADEMIC (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Chương trình chất lượng cao ngành Mạng máy tính và Truyền thông dữ liệu có bao nhiêu tín chỉ bắt buộc?

**Reference answer:** Chương trình chất lượng cao ngành Mạng máy tính và Truyền thông dữ liệu có 104 tín chỉ bắt buộc trong tổng số 141 tín chỉ.

**Required facts:** `["Mạng máy tính và Truyền thông dữ liệu", "104 tín chỉ bắt buộc", "141 tín chỉ"]`

**Gold sources:** `["109_7480102C_MangMayTinhVaTruyenThongDuLieu_CTCLC.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 141 TC (Bắt buộc: 104 TC; Tự chọn: 37 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.038462`

---

## [012/100] HOUT-ACAD-12 — ACADEMIC (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Chương trình đào tạo ngành Hóa Dược tại Trường Đại học Cần Thơ có tổng cộng bao nhiêu tín chỉ?

**Reference answer:** Chương trình đào tạo ngành Hóa Dược có tổng cộng 141 tín chỉ (Bắt buộc: 104 tín chỉ, Tự chọn: 37 tín chỉ).

**Required facts:** `["Hóa Dược", "141 tín chỉ"]`

**Gold sources:** `["08_7720203_HoaDuoc.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 141 TC (Bắt buộc: 104 TC; Tự chọn: 37 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.409091`

---

## [013/100] HOUT-ACAD-13 — ACADEMIC (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Chương trình đào tạo ngành Vật lý kỹ thuật có khối lượng tích lũy toàn khóa là bao nhiêu tín chỉ?

**Reference answer:** Chương trình đào tạo ngành Vật lý kỹ thuật có khối lượng tích lũy toàn khóa là 141 tín chỉ.

**Required facts:** `["Vật lý kỹ thuật", "141 tín chỉ"]`

**Gold sources:** `["05_7520401_VatLyKyThuat.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 141 TC (Bắt buộc: 98 TC; Tự chọn: 43 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.071429`

---

## [014/100] HOUT-ACAD-14 — ACADEMIC (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Dạ thầy cô cho em hỏi ngành Trí tuệ nhân tạo của trường mình học tổng cộng bao nhiêu chỉ thì được tốt nghiệp vậy ạ?

**Reference answer:** Chương trình đào tạo ngành Trí tuệ nhân tạo tại Trường Đại học Cần Thơ có tổng cộng 161 tín chỉ (Bắt buộc: 113 tín chỉ, Tự chọn: 48 tín chỉ).

**Required facts:** `["Trí tuệ nhân tạo", "161 tín chỉ"]`

**Gold sources:** `["108_7480107_TriTueNhanTao.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 113 TC; Tự chọn: 48 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [015/100] HOUT-ACAD-15 — ACADEMIC (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Ngành Logistics và Quản lý chuỗi cung ứng CTU học mấy năm và cần qua bao nhiêu tín chỉ mới ra trường được ạ?

**Reference answer:** Chương trình đào tạo ngành Logistics và Quản lý chuỗi cung ứng có tổng cộng 141 tín chỉ với thời gian đào tạo 4 năm.

**Required facts:** `["Logistics và Quản lý chuỗi cung ứng", "141 tín chỉ", "4 năm"]`

**Gold sources:** `["61_7510605_LogisticsVaQuanLyChuoiCungUng.md"]`

**Evidence excerpt:** - Ngành: Logistics và Quản lý chuỗi cung ứng (Logistics and Supply Chain Management)
- Mã ngành: 7510605
- Số lượng tín chỉ: 141 tín chỉ
- Thời gian đào tạo: 4 năm

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [016/100] HOUT-ACAD-16 — ACADEMIC (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Em đang tìm hiểu ngành Đảm bảo chất lượng và ATTP thì thấy có phần bắt buộc với tự chọn, phần bắt buộc là mấy chỉ vậy ad?

**Reference answer:** Chương trình đào tạo ngành Đảm bảo chất lượng và an toàn thực phẩm có tổng cộng 161 tín chỉ, trong đó có 117 tín chỉ bắt buộc và 44 tín chỉ tự chọn.

**Required facts:** `["117 tín chỉ bắt buộc", "161 tín chỉ"]`

**Gold sources:** `["114_7540106_DamBaoChatLuongVaAnToanTthucPham.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 117 TC; Tự chọn: 44 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [017/100] HOUT-ACAD-17 — ACADEMIC (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Nuôi trồng thủy sản hệ chuẩn học nặng không ạ, khóa học gồm bao nhiêu tín chỉ vậy mọi người?

**Reference answer:** Chương trình đào tạo ngành Nuôi trồng thủy sản hệ chuẩn yêu cầu tích lũy tổng cộng 161 tín chỉ.

**Required facts:** `["Nuôi trồng thủy sản", "161 tín chỉ"]`

**Gold sources:** `["100_7620301_NuoiTrongThuySan.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 115 TC; Tự chọn: 46 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [018/100] HOUT-ACAD-18 — ACADEMIC (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Mọi người cho em hỏi ngành Công nghệ sinh học khung chương trình tính tổng hết là bao nhiêu chỉ vậy?

**Reference answer:** Chương trình đào tạo ngành Công nghệ sinh học yêu cầu hoàn thành tổng cộng 161 tín chỉ.

**Required facts:** `["Công nghệ sinh học", "161 tín chỉ"]`

**Gold sources:** `["106_7420201_CongNgheSinhHoc.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 116 TC; Tự chọn: 45 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [019/100] HOUT-ACAD-19 — ACADEMIC (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Ngành Bác sĩ Thú y CTU học bao nhiêu năm mới tốt nghiệp và tổng số tín chỉ là bao nhiêu?

**Reference answer:** Ngành Thú y tại Đại học Cần Thơ có thời gian đào tạo là 5 năm với khối lượng kiến trúc chương trình là 175 tín chỉ.

**Required facts:** `["Thú y", "5 năm", "175"]`

**Gold sources:** `["96_7640101_ThuY.md", "115_7640101C_ThuY_CTCLC.md", "quychehocvu.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`

**Evidence excerpt:** - Thời gian đào tạo: 5 năm
- Khối lượng chương trình đào tạo: 175 tín chỉ

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.033333`

---

## [020/100] HOUT-ACAD-20 — ACADEMIC (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Em tính nộp hồ sơ Quản lý thủy sản, cho em hỏi chương trình này phải tích lũy bao nhiêu tín chỉ?

**Reference answer:** Chương trình đào tạo ngành Quản lý thủy sản có tổng cộng 141 tín chỉ.

**Required facts:** `["Quản lý thủy sản", "141 tín chỉ"]`

**Gold sources:** `["102_7620305_QuanLyThuySan.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 141 TC (Bắt buộc: 105 TC; Tự chọn: 36 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [021/100] HOUT-ACAD-21 — ACADEMIC (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Chương trình Công nghệ Sau thu hoạch bắt buộc sinh viên phải học bao nhiêu tín chỉ môn cố định vậy ạ?

**Reference answer:** Chương trình đào tạo ngành Công nghệ Sau thu hoạch có 116 tín chỉ bắt buộc trên tổng số 161 tín chỉ toàn khóa.

**Required facts:** `["Công nghệ Sau thu hoạch", "116 tín chỉ bắt buộc", "161"]`

**Gold sources:** `["103_7540104_CongNgheSauThuHoach.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 116 TC; Tự chọn: 45 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [022/100] HOUT-ACAD-22 — ACADEMIC (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Hệ chất lượng cao ngành Công nghệ thực phẩm cả khóa phải học hết mấy tín chỉ ạ?

**Reference answer:** Ngành Công nghệ thực phẩm chất lượng cao có tổng khối lượng chương trình là 161 tín chỉ.

**Required facts:** `["Công nghệ thực phẩm chất lượng cao", "161 tín chỉ"]`

**Gold sources:** `["105_7540101C_CongNgheThucPham_CTCLC.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 120 TC; Tự chọn: 41 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [023/100] HOUT-ACAD-23 — ACADEMIC (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Chương trình tiên tiến ngành CNSH của trường có tổng cộng bao nhiêu tín chỉ để ra trường?

**Reference answer:** Chương trình tiên tiến ngành Công nghệ sinh học đào tạo tổng cộng 161 tín chỉ.

**Required facts:** `["Công nghệ sinh học", "tiên tiến", "161 tín chỉ"]`

**Gold sources:** `["107_7420201T_CongNgheSinhHoc_CTTT.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 119 TC; Tự chọn: 42 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.130435`

---

## [024/100] HOUT-ACAD-24 — ACADEMIC (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Ngành Hóa Dược bên trường mình quy định khung đào tạo tích lũy hết bao nhiêu tín chỉ vậy ạ?

**Reference answer:** Chương trình đào tạo ngành Hóa Dược có tổng cộng 141 tín chỉ (Bắt buộc: 104 tín chỉ, Tự chọn: 37 tín chỉ).

**Required facts:** `["Hóa Dược", "141 tín chỉ"]`

**Gold sources:** `["08_7720203_HoaDuoc.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 141 TC (Bắt buộc: 104 TC; Tự chọn: 37 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [025/100] HOUT-ACAD-25 — ACADEMIC (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Em muốn hỏi ngành Vật lý kỹ thuật có chương trình học tất cả bao nhiêu tín chỉ mới hoàn thành?

**Reference answer:** Chương trình đào tạo ngành Vật lý kỹ thuật có khối lượng tích lũy toàn khóa là 141 tín chỉ.

**Required facts:** `["Vật lý kỹ thuật", "141 tín chỉ"]`

**Gold sources:** `["05_7520401_VatLyKyThuat.md"]`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 141 TC (Bắt buộc: 98 TC; Tự chọn: 43 TC)

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [026/100] HOUT-FIN-01 — FINANCIAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Ngành Thú y khóa 52 chương trình chuẩn đóng học phí trọn khóa là bao nhiêu tiền?

**Reference answer:** Mức thu của ngành Thú y, chương trình chuẩn, khóa 52, năm học 2026-2027 là 166.600.000 đồng toàn khóa.

**Required facts:** `["Thú y", "52", "166600000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Thú y, chương trình chuẩn, khóa 52, năm học 2026-2027 là 166.600.000 đồng toàn khóa.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [027/100] HOUT-FIN-02 — FINANCIAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Học phí toàn khóa của ngành Kỹ thuật y sinh K52 hệ chuẩn năm học 2026-2027 là bao nhiêu?

**Reference answer:** Mức thu của ngành Kỹ thuật y sinh, chương trình chuẩn, khóa 52, năm học 2026-2027 là 150.300.000 đồng toàn khóa.

**Required facts:** `["Kỹ thuật y sinh", "52", "150300000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Kỹ thuật y sinh, chương trình chuẩn, khóa 52, năm học 2026-2027 là 150.300.000 đồng toàn khóa.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.2`

---

## [028/100] HOUT-FIN-03 — FINANCIAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Học phí trọn khóa ngành Kỹ thuật xây dựng công trình thủy hệ chuẩn K52 là bao nhiêu?

**Reference answer:** Mức thu của ngành Kỹ thuật xây dựng công trình thủy, chương trình chuẩn, khóa 52, năm học 2026-2027 là 150.300.000 đồng toàn khóa.

**Required facts:** `["Kỹ thuật xây dựng công trình thủy", "52", "150300000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Kỹ thuật xây dựng công trình thủy, chương trình chuẩn, khóa 52, năm học 2026-2027 là 150.300.000 đồng toàn khóa.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [029/100] HOUT-FIN-04 — FINANCIAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Sinh viên ngành Công nghệ sinh học chương trình tiên tiến khóa 52 mỗi năm học đóng bao nhiêu học phí?

**Reference answer:** Mức thu của ngành Công nghệ sinh học, chương trình tiên tiến, khóa 52, năm học 2026-2027 là 44.000.000 đồng mỗi năm học.

**Required facts:** `["Công nghệ sinh học", "52", "44000000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_ChatLuongCao_TienTien.md"]`

**Evidence excerpt:** I. Học phí cố định theo khóa học (triệu đồng/năm học) | Chương trình Tiên tiến | Mức thu của ngành Công nghệ sinh học, chương trình tiên tiến, khóa 52, năm học 2026-2027 là 44.000.000 đồng mỗi năm học.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.027778`

---

## [030/100] HOUT-FIN-05 — FINANCIAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Một tín chỉ ngành Nuôi trồng thủy sản hệ tiên tiến khóa 49 có mức thu học phí là bao nhiêu?

**Reference answer:** Mức thu của ngành Nuôi trồng thủy sản, chương trình tiên tiến, khóa 49, năm học 2026-2027 là 1.309.000 đồng mỗi tín chỉ.

**Required facts:** `["Nuôi trồng thủy sản", "49", "1309000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_ChatLuongCao_TienTien.md"]`

**Evidence excerpt:** II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ) | Chương trình Tiên tiến (đồng/tín chỉ) | Mức thu của ngành Nuôi trồng thủy sản, chương trình tiên tiến, khóa 49, năm học 2026-2027 là 1.309.000 đồng mỗi tín chỉ.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.034483`

---

## [031/100] HOUT-FIN-06 — FINANCIAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Một tín chỉ ngành Quản lý xây dựng chương trình chuẩn khóa 52 có mức thu học phí là bao nhiêu?

**Reference answer:** Mức thu của ngành Quản lý xây dựng, chương trình chuẩn, khóa 52, năm học 2026-2027 là 966.000 đồng mỗi tín chỉ.

**Required facts:** `["Quản lý xây dựng", "52", "966000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Quản lý xây dựng, chương trình chuẩn, khóa 52, năm học 2026-2027 là 966.000 đồng mỗi tín chỉ.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.033333`

---

## [032/100] HOUT-FIN-07 — FINANCIAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Học phí một tín chỉ của ngành Kỹ thuật điều khiển và tự động hóa hệ chuẩn khóa 52 là bao nhiêu?

**Reference answer:** Mức thu của ngành Kỹ thuật điều khiển và tự động hóa, chương trình chuẩn, khóa 52, năm học 2026-2027 là 966.000 đồng mỗi tín chỉ.

**Required facts:** `["Kỹ thuật điều khiển và tự động hóa", "52", "966000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Kỹ thuật điều khiển và tự động hóa, chương trình chuẩn, khóa 52, năm học 2026-2027 là 966.000 đồng mỗi tín chỉ.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.035714`

---

## [033/100] HOUT-FIN-08 — FINANCIAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Sinh viên ngành Tài chính – Ngân hàng chất lượng cao khóa 49 đóng học phí bao nhiêu mỗi năm học?

**Reference answer:** Mức thu của ngành Tài chính – Ngân hàng, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 33.000.000 đồng mỗi năm học.

**Required facts:** `["Tài chính – Ngân hàng", "49", "33000000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_ChatLuongCao_TienTien.md"]`

**Evidence excerpt:** I. Học phí cố định theo khóa học (triệu đồng/năm học) | Chương trình Chất lượng cao | Mức thu của ngành Tài chính – Ngân hàng, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 33.000.000 đồng mỗi năm học.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.035714`

---

## [034/100] HOUT-FIN-09 — FINANCIAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Học phí tính theo tín chỉ của ngành Kinh doanh quốc tế chương trình CLC khóa 49 là bao nhiêu?

**Reference answer:** Mức thu của ngành Kinh doanh quốc tế, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 1.254.000 đồng mỗi tín chỉ.

**Required facts:** `["Kinh doanh quốc tế", "49", "1254000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_ChatLuongCao_TienTien.md"]`

**Evidence excerpt:** II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ) | Chương trình Chất lượng cao (đồng/tín chỉ) | Mức thu của ngành Kinh doanh quốc tế, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 1.254.000 đồng mỗi tín chỉ.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.037037`

---

## [035/100] HOUT-FIN-10 — FINANCIAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Một tín chỉ ngành Công nghệ kỹ thuật hóa học chất lượng cao khóa 49 mức thu là bao nhiêu?

**Reference answer:** Mức thu của ngành Công nghệ kỹ thuật hóa học, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 1.254.000 đồng mỗi tín chỉ.

**Required facts:** `["Công nghệ kỹ thuật hóa học", "49", "1254000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_ChatLuongCao_TienTien.md"]`

**Evidence excerpt:** II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ) | Chương trình Chất lượng cao (đồng/tín chỉ) | Mức thu của ngành Công nghệ kỹ thuật hóa học, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 1.254.000 đồng mỗi tín chỉ.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.071429`

---

## [036/100] HOUT-FIN-11 — FINANCIAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Học phần Giáo dục quốc phòng và An ninh có mức học phí cơ sở để tính miễn, giảm học phí là bao nhiêu tiền trên một tín chỉ?

**Reference answer:** Mức học phí cơ sở để tính miễn, giảm học phí cho học phần Giáo dục quốc phòng và An ninh là 451.000 đồng/tín chỉ.

**Required facts:** `["Giáo dục quốc phòng và An ninh", "451000", "cơ sở tính miễn, giảm"]`

**Gold sources:** `["MucHocPhi_2526_MienGiam.md"]`

**Evidence excerpt:** Các mức cần tra cứu phổ biến gồm: học phần Giáo dục quốc phòng và An ninh và Khối ngành III là 451.000 đồng/tín chỉ

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.194444`

---

## [037/100] HOUT-FIN-12 — FINANCIAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Mức học phí làm cơ sở tính miễn, giảm học phí cho Khối ngành IV tại Trường Đại học Cần Thơ cho năm học 2025-2026 là bao nhiêu?

**Reference answer:** Mức học phí làm cơ sở tính miễn, giảm học phí cho Khối ngành IV tại Trường Đại học Cần Thơ cho năm học 2025-2026 là 487.000 đồng/tín chỉ.

**Required facts:** `["Khối ngành IV", "487000", "cơ sở tính miễn, giảm"]`

**Gold sources:** `["MucHocPhi_2526_MienGiam.md"]`

**Evidence excerpt:** Khối ngành IV là 487.000 đồng/tín chỉ

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.30303`

---

## [038/100] HOUT-FIN-13 — FINANCIAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Sinh viên thuộc đối tượng nào sẽ được miễn 100% học phí nếu bản thân và cha mẹ hoặc ông bà thuộc hộ nghèo, hộ cận nghèo?

**Reference answer:** Sinh viên là dân tộc thiểu số có cha, mẹ hoặc ông, bà thuộc hộ nghèo, hộ cận nghèo theo quy định sẽ được miễn 100% học phí.

**Required facts:** `["dân tộc thiểu số", "hộ nghèo, hộ cận nghèo", "miễn 100% học phí"]`

**Gold sources:** `["mghp.md"]`

**Evidence excerpt:** Khoản 7-Điều 15: Sinh viên là dân tộc thiểu số có cha, mẹ hoặc ông, bà thuộc hộ nghèo, hộ cận nghèo

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.02381`

---

## [039/100] HOUT-FIN-14 — FINANCIAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Em muốn theo học ngành Thú y hệ chuẩn K52 thì học phí đóng trọn gói từ đầu tới lúc tốt nghiệp ra trường hết bao nhiêu tiền ạ?

**Reference answer:** Mức thu của ngành Thú y, chương trình chuẩn, khóa 52, năm học 2026-2027 là 166.600.000 đồng toàn khóa.

**Required facts:** `["Thú y", "52", "166600000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Thú y, chương trình chuẩn, khóa 52, năm học 2026-2027 là 166.600.000 đồng toàn khóa.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [040/100] HOUT-FIN-15 — FINANCIAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Cho em hỏi học phí nguyên khóa cho ngành Kỹ thuật y sinh hệ chuẩn khóa 52 năm học tới tính tổng cộng là bao nhiêu tiền?

**Reference answer:** Mức thu của ngành Kỹ thuật y sinh, chương trình chuẩn, khóa 52, năm học 2026-2027 là 150.300.000 đồng toàn khóa.

**Required facts:** `["Kỹ thuật y sinh", "52", "150300000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Kỹ thuật y sinh, chương trình chuẩn, khóa 52, năm học 2026-2027 là 150.300.000 đồng toàn khóa.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [041/100] HOUT-FIN-16 — FINANCIAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Sinh viên mới trúng tuyển ngành Kỹ thuật xây dựng công trình thủy hệ chuẩn K52 thì học hết khóa ra trường tốn bao nhiêu học phí ạ?

**Reference answer:** Mức thu của ngành Kỹ thuật xây dựng công trình thủy, chương trình chuẩn, khóa 52, năm học 2026-2027 là 150.300.000 đồng toàn khóa.

**Required facts:** `["Kỹ thuật xây dựng công trình thủy", "52", "150300000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Kỹ thuật xây dựng công trình thủy, chương trình chuẩn, khóa 52, năm học 2026-2027 là 150.300.000 đồng toàn khóa.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [042/100] HOUT-FIN-17 — FINANCIAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Em học Công nghệ sinh học hệ tiên tiến K52 thì trung bình mỗi năm đóng khoảng bao nhiêu tiền học phí vậy mọi người?

**Reference answer:** Mức thu của ngành Công nghệ sinh học, chương trình tiên tiến, khóa 52, năm học 2026-2027 là 44.000.000 đồng mỗi năm học.

**Required facts:** `["Công nghệ sinh học", "52", "44000000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_ChatLuongCao_TienTien.md"]`

**Evidence excerpt:** I. Học phí cố định theo khóa học (triệu đồng/năm học) | Chương trình Tiên tiến | Mức thu của ngành Công nghệ sinh học, chương trình tiên tiến, khóa 52, năm học 2026-2027 là 44.000.000 đồng mỗi năm học.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [043/100] HOUT-FIN-18 — FINANCIAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Mấy anh chị khóa trước cho em hỏi Nuôi trồng thủy sản hệ tiên tiến K49 thì đăng ký mỗi tín chỉ tính giá bao nhiêu tiền vậy ạ?

**Reference answer:** Mức thu của ngành Nuôi trồng thủy sản, chương trình tiên tiến, khóa 49, năm học 2026-2027 là 1.309.000 đồng mỗi tín chỉ.

**Required facts:** `["Nuôi trồng thủy sản", "49", "1309000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_ChatLuongCao_TienTien.md"]`

**Evidence excerpt:** II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ) | Chương trình Tiên tiến (đồng/tín chỉ) | Mức thu của ngành Nuôi trồng thủy sản, chương trình tiên tiến, khóa 49, năm học 2026-2027 là 1.309.000 đồng mỗi tín chỉ.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [044/100] HOUT-FIN-19 — FINANCIAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Ngành Quản lý xây dựng chương trình chuẩn K52 thì mỗi chỉ đóng bao nhiêu k vậy ad?

**Reference answer:** Mức thu của ngành Quản lý xây dựng, chương trình chuẩn, khóa 52, năm học 2026-2027 là 966.000 đồng mỗi tín chỉ.

**Required facts:** `["Quản lý xây dựng", "52", "966000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Quản lý xây dựng, chương trình chuẩn, khóa 52, năm học 2026-2027 là 966.000 đồng mỗi tín chỉ.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [045/100] HOUT-FIN-20 — FINANCIAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Học phí 1 tín chỉ của Kỹ thuật điều khiển và tự động hóa hệ chuẩn K52 là bao nhiêu ạ?

**Reference answer:** Mức thu của ngành Kỹ thuật điều khiển và tự động hóa, chương trình chuẩn, khóa 52, năm học 2026-2027 là 966.000 đồng mỗi tín chỉ.

**Required facts:** `["Kỹ thuật điều khiển và tự động hóa", "52", "966000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Kỹ thuật điều khiển và tự động hóa, chương trình chuẩn, khóa 52, năm học 2026-2027 là 966.000 đồng mỗi tín chỉ.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [046/100] HOUT-FIN-21 — FINANCIAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Sinh viên ngành Tài chính Ngân hàng CLC K49 mỗi năm phải nộp bao nhiêu tiền học phí vậy?

**Reference answer:** Mức thu của ngành Tài chính – Ngân hàng, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 33.000.000 đồng mỗi năm học.

**Required facts:** `["Tài chính – Ngân hàng", "49", "33000000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_ChatLuongCao_TienTien.md"]`

**Evidence excerpt:** I. Học phí cố định theo khóa học (triệu đồng/năm học) | Chương trình Chất lượng cao | Mức thu của ngành Tài chính – Ngân hàng, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 33.000.000 đồng mỗi năm học.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [047/100] HOUT-FIN-22 — FINANCIAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Kinh doanh quốc tế chất lượng cao khóa 49 tính học phí theo tín chỉ là bao nhiêu một chỉ?

**Reference answer:** Mức thu của ngành Kinh doanh quốc tế, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 1.254.000 đồng mỗi tín chỉ.

**Required facts:** `["Kinh doanh quốc tế", "49", "1254000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_ChatLuongCao_TienTien.md"]`

**Evidence excerpt:** II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ) | Chương trình Chất lượng cao (đồng/tín chỉ) | Mức thu của ngành Kinh doanh quốc tế, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 1.254.000 đồng mỗi tín chỉ.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.071429`

---

## [048/100] HOUT-FIN-23 — FINANCIAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Ngành Công nghệ kỹ thuật hóa học CLC K49 thu học phí mỗi chỉ bao nhiêu tiền vậy mng?

**Reference answer:** Mức thu của ngành Công nghệ kỹ thuật hóa học, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 1.254.000 đồng mỗi tín chỉ.

**Required facts:** `["Công nghệ kỹ thuật hóa học", "49", "1254000", "2026-2027"]`

**Gold sources:** `["MucHocPhi_ChatLuongCao_TienTien.md"]`

**Evidence excerpt:** II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ) | Chương trình Chất lượng cao (đồng/tín chỉ) | Mức thu của ngành Công nghệ kỹ thuật hóa học, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 1.254.000 đồng mỗi tín chỉ.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [049/100] HOUT-FIN-24 — FINANCIAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Môn GDQP được tính mức trần để hỗ trợ miễn giảm học phí là bao nhiêu tiền một tín chỉ vậy ạ?

**Reference answer:** Mức học phí cơ sở để tính miễn, giảm học phí cho học phần Giáo dục quốc phòng và An ninh là 451.000 đồng/tín chỉ.

**Required facts:** `["Giáo dục quốc phòng và An ninh", "451000", "cơ sở tính miễn, giảm"]`

**Gold sources:** `["MucHocPhi_2526_MienGiam.md"]`

**Evidence excerpt:** Các mức cần tra cứu phổ biến gồm: học phần Giáo dục quốc phòng và An ninh và Khối ngành III là 451.000 đồng/tín chỉ

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.090909`

---

## [050/100] HOUT-FIN-25 — FINANCIAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Nhà em là dân tộc thiểu số thuộc hộ cận nghèo thì có được trường miễn hết 100% học phí không ạ?

**Reference answer:** Sinh viên là dân tộc thiểu số có cha, mẹ hoặc ông, bà thuộc hộ nghèo, hộ cận nghèo theo quy định sẽ được miễn 100% học phí.

**Required facts:** `["dân tộc thiểu số", "hộ nghèo, hộ cận nghèo", "miễn 100% học phí"]`

**Gold sources:** `["mghp.md"]`

**Evidence excerpt:** Khoản 7-Điều 15: Sinh viên là dân tộc thiểu số có cha, mẹ hoặc ông, bà thuộc hộ nghèo, hộ cận nghèo

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [051/100] HOUT-SCH-01 — SCHOLARSHIP (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Mức học bổng bình quân cho học kỳ đầu tiên của học bổng khuyến khích học tập là bao nhiêu?

**Reference answer:** Mức học bổng bình quân cho học kỳ đầu tiên là 5.000.000 đồng/học kỳ/sinh viên.

**Required facts:** `["Mức học bổng bình quân", "học kỳ đầu tiên", "5000000"]`

**Gold sources:** `["HB_K51_2026.md", "03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md"]`

**Evidence excerpt:** Mức học bổng bình quân học kỳ đầu tiên là 5.000.000 đồng/học kỳ/sinh viên.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.074074`

---

## [052/100] HOUT-SCH-02 — SCHOLARSHIP (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Học bổng Thắp sáng Niềm Tin cho tân sinh viên Khóa 52 có mức tối đa là bao nhiêu mỗi năm học và bao gồm những khoản nào?

**Reference answer:** Mức học bổng tối đa là 30.000.000 đồng/năm học, bao gồm học phí và sinh hoạt phí.

**Required facts:** `["30.000.000 đồng/năm học", "Học phí", "Sinh hoạt phí"]`

**Gold sources:** `["HB_TanSinhVien_K52.md"]`

**Evidence excerpt:** Mức học bổng: tối đa 30.000.000 đồng/năm học, gồm Học phí + Sinh hoạt phí;

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.057143`

---

## [053/100] HOUT-SCH-03 — SCHOLARSHIP (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Theo thông báo xét cấp học bổng tài trợ, sinh viên Đại học Cần Thơ được phân bổ bao nhiêu suất học bổng Vallet năm 2026?

**Reference answer:** Đại học Cần Thơ (CTU) được phân bổ 12 suất học bổng Vallet cho sinh viên trong năm 2026.

**Required facts:** `["Đại học Cần Thơ", "CTU", "12 suất học bổng", "năm 2026"]`

**Gold sources:** `["HB_Vallet_Chi_Tiet.md"]`

**Evidence excerpt:** 1 | Đại học Cần Thơ Phòng Công tác Sinh viên | CTU | 12

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.052632`

---

## [054/100] HOUT-SCH-04 — SCHOLARSHIP (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Năm 2026, có bao nhiêu suất học bổng SCIC - Nâng bước tài năng trẻ được trao cho sinh viên Trường Công nghệ Thông tin & Truyền thông và mỗi suất trị giá bao nhiêu?

**Reference answer:** Năm 2026, SCIC dành 05 suất học bổng cho sinh viên Trường CNTT&TT, mỗi suất có giá trị 10.000.000 đồng.

**Required facts:** `["05 suất", "10.000.000 đồng", "SCIC", "Trường Công nghệ Thông tin & Truyền thông"]`

**Gold sources:** `["HB_SCIC_2026.md"]`

**Evidence excerpt:** Năm 2026, SCIC dành 05 suất học bổng cho sinh viên theo học tại Trường Công nghệ Thông tin & Truyền thông, Đại học Cần Thơ và giá trị mỗi suất học bổng là 10.000.000 đồng.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.025`

---

## [055/100] HOUT-SCH-05 — SCHOLARSHIP (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Mức học bổng khuyến khích học tập cho sinh viên Khối V loại Giỏi là bao nhiêu tiền mỗi học kỳ?

**Reference answer:** Mức học bổng khuyến khích học tập cho sinh viên Khối V loại Giỏi là 9.050.000 đồng mỗi học kỳ.

**Required facts:** `["Khối V", "loại Giỏi", "9.050.000 đồng/học kỳ"]`

**Gold sources:** `["Tài liệu phân bổ quỹ học bổng.md"]`

**Evidence excerpt:** V | Sức khỏe | 7.540.000 | 9.050.000 | 10.560.000

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.363636`

---

## [056/100] HOUT-SCH-06 — SCHOLARSHIP (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Giá trị mỗi suất học bổng Saigon Children’s Charity CIO (SCC) năm học 2025-2026 cho sinh viên ĐHCT là bao nhiêu và có bao nhiêu suất?

**Reference answer:** Mỗi suất học bổng SCC trị giá 10.000.000 đồng và có tổng cộng 10 suất được trao.

**Required facts:** `["10.000.000 đồng", "10 suất", "SCC"]`

**Gold sources:** `["HB_SCC.md"]`

**Evidence excerpt:** 3. Giá trị suất học bổng: 10.000.000 đồng (Mười triệu đồng)
4. Số suất học bổng: 10 suất

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.054054`

---

## [057/100] HOUT-SCH-07 — SCHOLARSHIP (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Điều kiện về kết quả học tập và rèn luyện để sinh viên dự tuyển học bổng SCC là gì?

**Reference answer:** Sinh viên cần đạt điểm trung bình tích lũy từ 3.2 trở lên và điểm rèn luyện tích lũy từ Tốt trở lên.

**Required facts:** `["TBTL từ 3.2", "điểm rèn luyện", "Tốt trở lên"]`

**Gold sources:** `["HB_SCC.md"]`

**Evidence excerpt:** - Điểm TBTL từ 3.2 trở lên; - Điểm rèn luyện tích lũy từ Tốt trở lên;

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [058/100] HOUT-SCH-08 — SCHOLARSHIP (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Quy trình xét cấp Học bổng Lương Văn Can gồm có mấy vòng tuyển chọn?

**Reference answer:** Quá trình xét duyệt Học bổng Lương Văn Can gồm 02 vòng: vòng sơ tuyển (vòng 1) và vòng phỏng vấn (vòng 2).

**Required facts:** `["02 vòng", "sơ tuyển", "phỏng vấn", "Lương Văn Can"]`

**Gold sources:** `["HB_LuongVanCang.md"]`

**Evidence excerpt:** Quá trình xét duyệt Học bổng gồm 02 vòng: vòng sơ tuyển (vòng 1), vòng phỏng vấn (vòng 2).

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [059/100] HOUT-SCH-09 — SCHOLARSHIP (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Suất học bổng Lương Văn Can được trao dưới các hình thức nào và bao gồm các khoản chi phí nào?

**Reference answer:** Học bổng trao các suất toàn phần hoặc bán phần bao gồm học phí, sinh hoạt phí và/hoặc chi phí học ngoại ngữ.

**Required facts:** `["toàn phần hoặc bán phần", "học phí", "sinh hoạt phí", "ngoại ngữ"]`

**Gold sources:** `["HB_LuongVanCang.md"]`

**Evidence excerpt:** Hội đồng tuyển chọn sẽ quyết định trao các suất học bổng toàn phần hoặc bán phần bao gồm học phí, sinh hoạt phí và/hoặc chi phí học ngoại ngữ.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [060/100] HOUT-SCH-10 — SCHOLARSHIP (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Mỗi suất học bổng Vallet dành cho sinh viên năm 2026 có giá trị là bao nhiêu tiền?

**Reference answer:** Mỗi suất học bổng Vallet dành cho sinh viên có giá trị là 29.000.000 đồng/suất.

**Required facts:** `["Vallet", "29.000.000 đồng", "sinh viên"]`

**Gold sources:** `["HB_Vallet_Chi_Tiet.md", "HB_Vallet.md"]`

**Evidence excerpt:** Học bổng Vallet: 29.000.000 đồng/suất cho sinh viên đại học.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [061/100] HOUT-SCH-11 — SCHOLARSHIP (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Mức học bổng khuyến khích học tập cho sinh viên Khối V loại Xuất sắc là bao nhiêu tiền mỗi học kỳ?

**Reference answer:** Mức học bổng khuyến khích học tập cho sinh viên Khối V loại Xuất sắc là 10.560.000 đồng mỗi học kỳ.

**Required facts:** `["Khối V", "loại Xuất sắc", "10.560.000 đồng/học kỳ"]`

**Gold sources:** `["Tài liệu phân bổ quỹ học bổng.md"]`

**Evidence excerpt:** V | Sức khỏe | 7.540.000 | 9.050.000 | 10.560.000

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.391304`

---

## [062/100] HOUT-SCH-12 — SCHOLARSHIP (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Mức học bổng khuyến khích học tập cho sinh viên Khối V loại Khá là bao nhiêu tiền mỗi học kỳ?

**Reference answer:** Mức học bổng khuyến khích học tập cho sinh viên Khối V loại Khá là 7.540.000 đồng mỗi học kỳ.

**Required facts:** `["Khối V", "loại Khá", "7.540.000 đồng/học kỳ"]`

**Gold sources:** `["Tài liệu phân bổ quỹ học bổng.md"]`

**Evidence excerpt:** V | Sức khỏe | 7.540.000 | 9.050.000 | 10.560.000

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.363636`

---

## [063/100] HOUT-SCH-13 — SCHOLARSHIP (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Đối tượng xét cấp học bổng Thắp sáng Niềm Tin Khóa 52 yêu cầu mức thu nhập gia đình bình quân như thế nào?

**Reference answer:** Gia đình sinh viên phải thuộc diện hộ nghèo, cận nghèo hoặc có hoàn cảnh đặc biệt khó khăn với mức thu nhập bình quân không quá 1,5 triệu đồng/người/tháng.

**Required facts:** `["Thắp sáng Niềm Tin", "hộ nghèo", "1,5 triệu đồng"]`

**Gold sources:** `["HB_TanSinhVien_K52.md"]`

**Evidence excerpt:** gia đình có hoàn cảnh đặc biệt khó khăn, thu nhập bình quân không quá 1,5 triệu đồng/người/tháng

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.027778`

---

## [064/100] HOUT-SCH-14 — SCHOLARSHIP (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Học kỳ đầu tiên tân sinh viên thì học bổng khuyến khích học tập được tính bình quân một suất là bao nhiêu tiền vậy ạ?

**Reference answer:** Mức học bổng bình quân cho học kỳ đầu tiên là 5.000.000 đồng/học kỳ/sinh viên.

**Required facts:** `["Mức học bổng bình quân", "5000000"]`

**Gold sources:** `["HB_K51_2026.md", "03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md"]`

**Evidence excerpt:** Mức học bổng bình quân học kỳ đầu tiên là 5.000.000 đồng/học kỳ/sinh viên.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.060606`

---

## [065/100] HOUT-SCH-15 — SCHOLARSHIP (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Tân sinh viên K52 nộp học bổng Thắp sáng Niềm Tin thì nếu được duyệt mức cao nhất nhận được mấy chục triệu một năm?

**Reference answer:** Mức học bổng tối đa là 30.000.000 đồng/năm học, bao gồm học phí và sinh hoạt phí.

**Required facts:** `["30.000.000 đồng/năm học", "Học phí", "Sinh hoạt phí"]`

**Gold sources:** `["HB_TanSinhVien_K52.md"]`

**Evidence excerpt:** Mức học bổng: tối đa 30.000.000 đồng/năm học, gồm Học phí + Sinh hoạt phí;

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [066/100] HOUT-SCH-16 — SCHOLARSHIP (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Năm 2026 trường mình được bên quỹ Vallet chia cho bao nhiêu suất học bổng sinh viên vậy ạ?

**Reference answer:** Đại học Cần Thơ (CTU) được phân bổ 12 suất học bổng Vallet cho sinh viên trong năm 2026.

**Required facts:** `["Đại học Cần Thơ", "CTU", "12 suất học bổng"]`

**Gold sources:** `["HB_Vallet_Chi_Tiet.md"]`

**Evidence excerpt:** 1 | Đại học Cần Thơ Phòng Công tác Sinh viên | CTU | 12

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.038462`

---

## [067/100] HOUT-SCH-17 — SCHOLARSHIP (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Sinh viên IT bên Trường CNTT&TT có học bổng SCIC không, được mấy suất và giá trị mỗi suất bao nhiêu tiền?

**Reference answer:** Năm 2026, SCIC dành 05 suất học bổng cho sinh viên Trường CNTT&TT, mỗi suất có giá trị 10.000.000 đồng.

**Required facts:** `["05 suất", "10.000.000 đồng", "SCIC"]`

**Gold sources:** `["HB_SCIC_2026.md"]`

**Evidence excerpt:** Năm 2026, SCIC dành 05 suất học bổng cho sinh viên theo học tại Trường Công nghệ Thông tin & Truyền thông, Đại học Cần Thơ và giá trị mỗi suất học bổng là 10.000.000 đồng.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [068/100] HOUT-SCH-18 — SCHOLARSHIP (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Em học khối ngành Sức khỏe (Khối V) nếu đạt học lực Giỏi thì học bổng khuyến khích được bao nhiêu tiền một kỳ?

**Reference answer:** Mức học bổng khuyến khích học tập cho sinh viên Khối V loại Giỏi là 9.050.000 đồng mỗi học kỳ.

**Required facts:** `["Khối V", "loại Giỏi", "9.050.000 đồng/học kỳ"]`

**Gold sources:** `["Tài liệu phân bổ quỹ học bổng.md"]`

**Evidence excerpt:** V | Sức khỏe | 7.540.000 | 9.050.000 | 10.560.000

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [069/100] HOUT-SCH-19 — SCHOLARSHIP (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Học bổng Saigon Children’s Charity năm nay cho sinh viên CTU trị giá bao nhiêu tiền một suất và có mấy suất vậy ad?

**Reference answer:** Mỗi suất học bổng SCC trị giá 10.000.000 đồng và có tổng cộng 10 suất được trao.

**Required facts:** `["10.000.000 đồng", "10 suất", "SCC"]`

**Gold sources:** `["HB_SCC.md"]`

**Evidence excerpt:** 3. Giá trị suất học bổng: 10.000.000 đồng (Mười triệu đồng)
4. Số suất học bổng: 10 suất

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [070/100] HOUT-SCH-20 — SCHOLARSHIP (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Em muốn nộp học bổng SCC thì cần điểm tích lũy bao nhiêu chấm với điểm rèn luyện cỡ nào mới đủ điều kiện?

**Reference answer:** Sinh viên cần đạt điểm trung bình tích lũy từ 3.2 trở lên và điểm rèn luyện tích lũy từ Tốt trở lên.

**Required facts:** `["TBTL từ 3.2", "điểm rèn luyện", "Tốt trở lên"]`

**Gold sources:** `["HB_SCC.md"]`

**Evidence excerpt:** - Điểm TBTL từ 3.2 trở lên; - Điểm rèn luyện tích lũy từ Tốt trở lên;

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [071/100] HOUT-SCH-21 — SCHOLARSHIP (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Xét học bổng Lương Văn Can có phải phỏng vấn trực tiếp không hay chỉ cần nộp hồ sơ là xong vậy ạ?

**Reference answer:** Quá trình xét duyệt Học bổng Lương Văn Can gồm 02 vòng: vòng sơ tuyển (vòng 1) và vòng phỏng vấn (vòng 2).

**Required facts:** `["02 vòng", "sơ tuyển", "phỏng vấn"]`

**Gold sources:** `["HB_LuongVanCang.md"]`

**Evidence excerpt:** Quá trình xét duyệt Học bổng gồm 02 vòng: vòng sơ tuyển (vòng 1), vòng phỏng vấn (vòng 2).

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [072/100] HOUT-SCH-22 — SCHOLARSHIP (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Học bổng Lương Văn Can có hỗ trợ tiền học tiếng Anh với sinh hoạt phí cho sinh viên không mọi người?

**Reference answer:** Học bổng trao các suất toàn phần hoặc bán phần bao gồm học phí, sinh hoạt phí và/hoặc chi phí học ngoại ngữ.

**Required facts:** `["sinh hoạt phí", "ngoại ngữ", "Lương Văn Can"]`

**Gold sources:** `["HB_LuongVanCang.md"]`

**Evidence excerpt:** Hội đồng tuyển chọn sẽ quyết định trao các suất học bổng toàn phần hoặc bán phần bao gồm học phí, sinh hoạt phí và/hoặc chi phí học ngoại ngữ.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [073/100] HOUT-SCH-23 — SCHOLARSHIP (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Cho em hỏi học bổng Vallet mỗi bạn nhận được bao nhiêu tiền một suất vậy ạ?

**Reference answer:** Mỗi suất học bổng Vallet dành cho sinh viên có giá trị là 29.000.000 đồng/suất.

**Required facts:** `["Vallet", "29.000.000 đồng"]`

**Gold sources:** `["HB_Vallet_Chi_Tiet.md", "HB_Vallet.md"]`

**Evidence excerpt:** Học bổng Vallet: 29.000.000 đồng/suất cho sinh viên đại học.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [074/100] HOUT-SCH-24 — SCHOLARSHIP (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Khối V ngành y dược nếu đạt loại Xuất sắc thì học bổng khuyến khích học kỳ đó được hơn 10 triệu không ạ?

**Reference answer:** Mức học bổng khuyến khích học tập cho sinh viên Khối V loại Xuất sắc là 10.560.000 đồng mỗi học kỳ.

**Required facts:** `["Khối V", "loại Xuất sắc", "10.560.000 đồng/học kỳ"]`

**Gold sources:** `["Tài liệu phân bổ quỹ học bổng.md"]`

**Evidence excerpt:** V | Sức khỏe | 7.540.000 | 9.050.000 | 10.560.000

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.03125`

---

## [075/100] HOUT-SCH-25 — SCHOLARSHIP (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Gia đình em thu nhập khoảng 1 triệu rưỡi một người một tháng thì có đủ chuẩn nộp học bổng Thắp sáng Niềm Tin không?

**Reference answer:** Gia đình sinh viên thuộc diện hộ nghèo, cận nghèo hoặc có hoàn cảnh đặc biệt khó khăn với mức thu nhập bình quân không quá 1,5 triệu đồng/người/tháng đủ điều kiện nộp hồ sơ.

**Required facts:** `["Thắp sáng Niềm Tin", "1,5 triệu đồng"]`

**Gold sources:** `["HB_TanSinhVien_K52.md"]`

**Evidence excerpt:** thu nhập bình quân không quá 1,5 triệu đồng/người/tháng

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [076/100] HOUT-GEN-01 — GENERAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Sinh viên Trường Đại học Cần Thơ được miễn thi và tính điểm cho bao nhiêu học phần khi tham gia các kỳ thi Olympic toàn quốc hoặc cuộc thi Robocon?

**Reference answer:** Sinh viên được xem xét miễn thi và tính điểm cho một học phần (khối lượng không quá 4 tín chỉ), nếu tham gia nhiều kỳ thi trong một học kỳ thì chỉ được miễn không quá 2 học phần.

**Required facts:** `["miễn thi và tính điểm", "không quá 4 tín chỉ", "không quá 2 học phần"]`

**Gold sources:** `["QD2457_Quy_dinh_xet_mien_va_cong_nhan_diem_HP_hinh_thuc_CQ_nam_2024_llp.md"]`

**Evidence excerpt:** SV được xem xét miễn thi và tính điểm cho một học phần... có khối lượng không quá 4 tín chỉ. SV tham gia nhiều kỳ thi/cuộc thi trong một học kỳ chỉ xét miễn thi và tính điểm cho không quá 2 học phần.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.041667`

---

## [077/100] HOUT-GEN-02 — GENERAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Thời gian tối đa để sinh viên hoàn thành chương trình đào tạo đại học chính quy có thời gian thiết kế là 4,5 năm là bao nhiêu năm?

**Reference answer:** Thời gian học tập tối đa cho phép để sinh viên hoàn thành chương trình đào tạo có thời gian thiết kế là 4,5 năm là 9 năm.

**Required facts:** `["4,5 năm", "9 năm"]`

**Gold sources:** `["quychehocvu.md"]`

**Evidence excerpt:** 4,5 năm | 9 năm

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.184211`

---

## [078/100] HOUT-GEN-03 — GENERAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Theo Quy định công tác học vụ của Trường Đại học Cần Thơ, sinh viên có thể được xét công nhận tốt nghiệp vào các tháng nào trong năm?

**Reference answer:** Sinh viên có thể được xét công nhận tốt nghiệp vào các tháng 01, tháng 6 và tháng 8 hàng năm.

**Required facts:** `["tháng 01", "tháng 6", "tháng 8"]`

**Gold sources:** `["QD1813_QD_ban_hanh_Quy_dinh_cong_tac_hoc_vu_2021.md"]`

**Evidence excerpt:** Hằng năm, SV được xét tốt nghiệp vào tháng 01, tháng 6 và tháng 8.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.047619`

---

## [079/100] HOUT-GEN-04 — GENERAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Theo quy định, mẫu đơn xin học lại áp dụng cho trường hợp sinh viên bị đình chỉ học tập như thế nào?

**Reference answer:** Mẫu đơn xin học lại này áp dụng cho sinh viên bị đình chỉ học tập có thời hạn.

**Required facts:** `["đình chỉ học tập", "có thời hạn"]`

**Gold sources:** `["3_don_xin_hoc_lai_llp.md"]`

**Evidence excerpt:** Lưu ý: Mẫu này áp dụng đối với sinh viên bị đình chỉ học tập có thời hạn.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.033333`

---

## [080/100] HOUT-GEN-05 — GENERAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Theo quy định của Đại học Cần Thơ, sinh viên cần cung cấp những giấy tờ gì khi làm đơn xin tạm nghỉ học vì lý do điều trị bệnh?

**Reference answer:** Khi làm đơn xin tạm nghỉ học vì lý do điều trị bệnh, sinh viên cần nộp kèm hồ sơ hoặc giấy chỉ định của Bác sĩ.

**Required facts:** `["hồ sơ", "giấy chỉ định của Bác sĩ"]`

**Gold sources:** `["5_don_xin_tam_nghi_hoc_llp.md"]`

**Evidence excerpt:** Lý do*: Điều trị bệnh... (Kèm theo hồ sơ hoặc giấy chỉ định của Bác sĩ nếu có)*

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.027027`

---

## [081/100] HOUT-GEN-06 — GENERAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Để minh chứng cho việc xét tuyển theo phương thức học bạ khi xin chuyển ngành, sinh viên cần nộp những loại giấy tờ nào?

**Reference answer:** Sinh viên cần nộp bản sao học bạ có công chứng hoặc chứng thực.

**Required facts:** `["bản sao học bạ", "công chứng hoặc chứng thực"]`

**Gold sources:** `["7_don_de_nghi_chuyen_ctdt_llp.md", "02_3924KHTH_23-10-2023_llp.md"]`

**Evidence excerpt:** Nếu sử dụng xét tuyển theo phương thức học bạ, thì sinh viên cần minh chứng học bạ (bản sao, công chứng hoặc chứng thực).

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [082/100] HOUT-GEN-07 — GENERAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Mức vay vốn tối đa cho mỗi học sinh, sinh viên là bao nhiêu theo quy định mới nhất?

**Reference answer:** Mức vay vốn tối đa cho mỗi học sinh, sinh viên là 4.000.000 đồng mỗi tháng.

**Required facts:** `["Mức vay vốn tối đa", "4.000.000 đồng/tháng"]`

**Gold sources:** `["VayVonSinhVien2022.md", "NDCP_VayVonSVKT.md", "VayVon.md"]`

**Evidence excerpt:** Mức vay vốn tối đa là 4.000.000 đồng/tháng/học sinh, sinh viên.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [083/100] HOUT-GEN-08 — GENERAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Mức sinh hoạt phí tối đa mà người học có thể nhận hàng tháng theo quy định của Quyết định 29/2025/QĐ-TTg là bao nhiêu?

**Reference answer:** Mức sinh hoạt phí và chi phí học tập khác tối đa mà người học có thể nhận hàng tháng là 5 triệu đồng.

**Required facts:** `["sinh hoạt phí", "5 triệu đồng/tháng"]`

**Gold sources:** `["Q_29_STEM_288.md", "VayVonVoiNhomNganhKThuat.md", "NDCP_VayVonSVKT.md"]`

**Evidence excerpt:** Tiền sinh hoạt phí và chi phí học tập khác tối đa là 5 triệu đồng/tháng.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [084/100] HOUT-GEN-09 — GENERAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Học sinh, sinh viên có hoàn cảnh khó khăn có thể vay tối đa bao nhiêu tiền để mua máy tính, thiết bị học tập trực tuyến theo Quyết định 09/2022/QĐ-TTg?

**Reference answer:** Mức vốn cho vay tối đa là 10 triệu đồng cho mỗi học sinh, sinh viên.

**Required facts:** `["Mức vốn cho vay tối đa", "10 triệu đồng"]`

**Gold sources:** `["VayVonMuaMayTinh.md"]`

**Evidence excerpt:** Mức vốn cho vay tối đa là 10 triệu đồng/học sinh, sinh viên.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.068182`

---

## [085/100] HOUT-GEN-10 — GENERAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Theo Thông báo về việc hỗ trợ chi phí đào tạo đại học, sinh viên dân tộc thiểu số thuộc diện nào thì đủ điều kiện nhận hỗ trợ chi phí học tập?

**Reference answer:** Sinh viên dân tộc thiểu số hệ chính quy thuộc hộ nghèo, hộ cận nghèo hoặc ngành Sư phạm nhưng chưa hưởng chính sách Nghị định 116/2020/NĐ-CP thì đủ điều kiện nhận hỗ trợ chi phí học tập.

**Required facts:** `["dân tộc thiểu số", "hộ nghèo, hộ cận nghèo", "hỗ trợ chi phí"]`

**Gold sources:** `["Ho_tro.md", "02_246_23-06-2026.md"]`

**Evidence excerpt:** Sinh viên đang học tại Trường hệ chính quy... là người dân tộc thiểu số theo Quyết định 1227/QĐ – TTg ngày 14/7/2021 thuộc hộ nghèo, hộ cận nghèo

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.088889`

---

## [086/100] HOUT-GEN-11 — GENERAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Theo Quyết định về Trợ cấp xã hội của Đại học Cần Thơ, mức trợ cấp xã hội cho mỗi sinh viên thuộc diện hộ nghèo hoặc con mồ côi là bao nhiêu và trong thời gian nào?

**Reference answer:** Mức trợ cấp là 100.000 đồng/sinh viên/tháng, áp dụng cho học kỳ 2, năm học 2025 – 2026 (từ tháng 01/2026 đến tháng 04/2026).

**Required facts:** `["100.000 đồng/sinh viên/tháng", "học kỳ 2", "tháng 01/2026 đến tháng 04/2026"]`

**Gold sources:** `["TCXH.md"]`

**Evidence excerpt:** Điều 2. Mức trợ cấp là 100.000 đồng/sinh viên/tháng. Thời gian hưởng trợ cấp xã hội là học kỳ 2, năm học 2025 – 2026 (Từ tháng 01/2026 đến tháng 04/2026).

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.022222`

---

## [087/100] HOUT-GEN-12 — GENERAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Sinh viên có được phép đặt bát hương thờ cúng trong phòng ở Ký túc xá không?

**Reference answer:** Sinh viên không được phép đặt bát hương thờ cúng trong phòng ở và trong khu vực Ký túc xá.

**Required facts:** `["không được đặt bát hương", "Ký túc xá"]`

**Gold sources:** `["Noi quy KTX nam 2016_llp.md"]`

**Evidence excerpt:** Không được đặt bát hương thờ cúng trong phòng ở và trong khu vực KTX; Không nuôi cá, vật nuôi trong phòng ở và khu vực KTX

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [088/100] HOUT-GEN-13 — GENERAL (formal)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Lệ phí để xin cấp một bản sao văn bằng tốt nghiệp đại học là bao nhiêu?

**Reference answer:** Chi phí cấp một bản sao bằng Bác sĩ thú y là 90.000đ/bản, các văn bằng còn lại là 50.000đ/bản.

**Required facts:** `["90.000đ", "50.000đ", "bản sao văn bằng"]`

**Gold sources:** `["Phieu_De_nghi_cap_ban_sao_cap_lai_chinh_sua_NDVB_llp.md"]`

**Evidence excerpt:** 90.000đ/ 1 bản – Bằng Bác sĩ thú y; 50.000đ/ 1 bản – Các văn bằng còn lại

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.064516`

---

## [089/100] HOUT-GEN-14 — GENERAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Em đi thi Robocon đạt giải cấp trường với tham gia Olympic thì có được miễn thi môn nào trên lớp không ạ?

**Reference answer:** Sinh viên được xem xét miễn thi và tính điểm cho một học phần (khối lượng không quá 4 tín chỉ), nếu tham gia nhiều kỳ thi trong một học kỳ thì chỉ được miễn không quá 2 học phần.

**Required facts:** `["miễn thi", "không quá 4 tín chỉ", "không quá 2 học phần"]`

**Gold sources:** `["QD2457_Quy_dinh_xet_mien_va_cong_nhan_diem_HP_hinh_thuc_CQ_nam_2024_llp.md"]`

**Evidence excerpt:** SV được xem xét miễn thi và tính điểm cho một học phần... có khối lượng không quá 4 tín chỉ. SV tham gia nhiều kỳ thi/cuộc thi trong một học kỳ chỉ xét miễn thi và tính điểm cho không quá 2 học phần.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [090/100] HOUT-GEN-15 — GENERAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Chương trình học 4 năm rưỡi thì nhà trường cho phép học kéo dài dây dưa tối đa mấy năm là bị đuổi học vậy mng?

**Reference answer:** Thời gian học tập tối đa cho phép để sinh viên hoàn thành chương trình đào tạo có thời gian thiết kế là 4,5 năm là 9 năm.

**Required facts:** `["4,5 năm", "9 năm"]`

**Gold sources:** `["quychehocvu.md"]`

**Evidence excerpt:** 4,5 năm | 9 năm

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [091/100] HOUT-GEN-16 — GENERAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** CTU mình một năm có mấy đợt xét tốt nghiệp và rơi vào những tháng nào vậy mọi người?

**Reference answer:** Sinh viên có thể được xét công nhận tốt nghiệp vào các tháng 01, tháng 6 và tháng 8 hàng năm.

**Required facts:** `["tháng 01", "tháng 6", "tháng 8"]`

**Gold sources:** `["QD1813_QD_ban_hanh_Quy_dinh_cong_tac_hoc_vu_2021.md"]`

**Evidence excerpt:** Hằng năm, SV được xét tốt nghiệp vào tháng 01, tháng 6 và tháng 8.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [092/100] HOUT-GEN-17 — GENERAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Hồi trước bị trường đình chỉ học tập có thời hạn, giờ muốn quay lại học tiếp thì điền mẫu đơn nào ạ?

**Reference answer:** Mẫu đơn xin học lại này áp dụng cho sinh viên bị đình chỉ học tập có thời hạn.

**Required facts:** `["đình chỉ học tập", "có thời hạn"]`

**Gold sources:** `["3_don_xin_hoc_lai_llp.md"]`

**Evidence excerpt:** Lưu ý: Mẫu này áp dụng đối với sinh viên bị đình chỉ học tập có thời hạn.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [093/100] HOUT-GEN-18 — GENERAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Em bị bệnh nặng phải nằm viện điều trị dài ngày, muốn làm đơn tạm nghỉ học một kỳ thì cần xin giấy tờ gì của bệnh viện?

**Reference answer:** Khi làm đơn xin tạm nghỉ học vì lý do điều trị bệnh, sinh viên cần nộp kèm hồ sơ hoặc giấy chỉ định của Bác sĩ.

**Required facts:** `["hồ sơ", "giấy chỉ định của Bác sĩ"]`

**Gold sources:** `["5_don_xin_tam_nghi_hoc_llp.md"]`

**Evidence excerpt:** Lý do*: Điều trị bệnh... (Kèm theo hồ sơ hoặc giấy chỉ định của Bác sĩ nếu có)*

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [094/100] HOUT-GEN-19 — GENERAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Làm hồ sơ xin chuyển ngành học mà dùng điểm học bạ THPT thì có cần công chứng học bạ không ạ?

**Reference answer:** Sinh viên cần nộp bản sao học bạ có công chứng hoặc chứng thực.

**Required facts:** `["bản sao học bạ", "công chứng"]`

**Gold sources:** `["7_don_de_nghi_chuyen_ctdt_llp.md", "02_3924KHTH_23-10-2023_llp.md"]`

**Evidence excerpt:** Nếu sử dụng xét tuyển theo phương thức học bạ, thì sinh viên cần minh chứng học bạ (bản sao, công chứng hoặc chứng thực).

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [095/100] HOUT-GEN-20 — GENERAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Hạn mức sinh viên vay vốn chính sách trang trải việc học tối đa một tháng được bao nhiêu triệu vậy ạ?

**Reference answer:** Mức vay vốn tối đa cho mỗi học sinh, sinh viên là 4.000.000 đồng mỗi tháng.

**Required facts:** `["Mức vay vốn tối đa", "4.000.000 đồng/tháng"]`

**Gold sources:** `["VayVonSinhVien2022.md", "NDCP_VayVonSVKT.md", "VayVon.md"]`

**Evidence excerpt:** Mức vay vốn tối đa là 4.000.000 đồng/tháng/học sinh, sinh viên.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [096/100] HOUT-GEN-21 — GENERAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Em học khối kỹ thuật theo QĐ 29 thì tiền vay hỗ trợ sinh hoạt phí hàng tháng được tối đa mấy triệu?

**Reference answer:** Mức sinh hoạt phí và chi phí học tập khác tối đa mà người học có thể nhận hàng tháng là 5 triệu đồng.

**Required facts:** `["sinh hoạt phí", "5 triệu đồng/tháng"]`

**Gold sources:** `["Q_29_STEM_288.md", "VayVonVoiNhomNganhKThuat.md", "NDCP_VayVonSVKT.md"]`

**Evidence excerpt:** Tiền sinh hoạt phí và chi phí học tập khác tối đa là 5 triệu đồng/tháng.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [097/100] HOUT-GEN-22 — GENERAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Gia đình khó khăn muốn vay vốn ngân hàng chính sách mua laptop học online thì gói này vay tối đa được bao nhiêu tiền?

**Reference answer:** Mức vốn cho vay tối đa là 10 triệu đồng cho mỗi học sinh, sinh viên.

**Required facts:** `["Mức vốn cho vay tối đa", "10 triệu đồng"]`

**Gold sources:** `["VayVonMuaMayTinh.md"]`

**Evidence excerpt:** Mức vốn cho vay tối đa là 10 triệu đồng/học sinh, sinh viên.

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---

## [098/100] HOUT-GEN-23 — GENERAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Tụi em là sinh viên dân tộc thiểu số hộ nghèo học chính quy thì được nhà trường trợ cấp tiền hỗ trợ chi phí học tập thế nào?

**Reference answer:** Sinh viên dân tộc thiểu số hệ chính quy thuộc hộ nghèo, hộ cận nghèo hoặc ngành Sư phạm nhưng chưa hưởng chính sách Nghị định 116/2020/NĐ-CP thì đủ điều kiện nhận hỗ trợ chi phí học tập.

**Required facts:** `["dân tộc thiểu số", "hộ nghèo, hộ cận nghèo", "hỗ trợ chi phí"]`

**Gold sources:** `["Ho_tro.md", "02_246_23-06-2026.md"]`

**Evidence excerpt:** Sinh viên đang học tại Trường hệ chính quy... là người dân tộc thiểu số theo Quyết định 1227/QĐ – TTg ngày 14/7/2021 thuộc hộ nghèo, hộ cận nghèo

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.153846`

---

## [099/100] HOUT-GEN-24 — GENERAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Trợ cấp xã hội cho sinh viên nghèo mồ côi của trường học kỳ 2 này được phát bao nhiêu tiền một tháng vậy mọi người?

**Reference answer:** Mức trợ cấp là 100.000 đồng/sinh viên/tháng, áp dụng cho học kỳ 2, năm học 2025 – 2026 (từ tháng 01/2026 đến tháng 04/2026).

**Required facts:** `["100.000 đồng/sinh viên/tháng", "học kỳ 2"]`

**Gold sources:** `["TCXH.md"]`

**Evidence excerpt:** Điều 2. Mức trợ cấp là 100.000 đồng/sinh viên/tháng. Thời gian hưởng trợ cấp xã hội là học kỳ 2, năm học 2025 – 2026 (Từ tháng 01/2026 đến tháng 04/2026).

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.073171`

---

## [100/100] HOUT-GEN-25 — GENERAL (colloquial)

- [x] Approved
- [x] Question tự đủ nghĩa & đúng thực tế
- [x] Reference Answer có trích dẫn văn bản chứng minh
- [x] Required Facts chính xác
- [x] Gold Sources chuẩn xác
- [x] Disjoint Entity Verified (Zero leakage so với Dev)

**Question:** Ở phòng ký túc xá CTU có được lập bàn thờ hay để bát hương thờ cúng không mấy bạn?

**Reference answer:** Sinh viên không được phép đặt bát hương thờ cúng trong phòng ở và trong khu vực Ký túc xá.

**Required facts:** `["không được đặt bát hương", "Ký túc xá"]`

**Gold sources:** `["Noi quy KTX nam 2016_llp.md"]`

**Evidence excerpt:** Không được đặt bát hương thờ cúng trong phòng ở và trong khu vực KTX; Không nuôi cá, vật nuôi trong phòng ở và khu vực KTX

**Novelty vs Dev:** exact=`False`, max_5gram_jaccard=`0.0`

---
