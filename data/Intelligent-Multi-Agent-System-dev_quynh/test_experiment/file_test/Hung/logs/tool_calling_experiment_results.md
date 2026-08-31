# Financial Function Experiment Results

- Started: `2026-08-13T16:58:57.867476+07:00`
- Gemini model for tool selection: `gemini-3.5-flash-lite`
- Dataset: `data/tool_calling_experiment.json`
- Design: 10 cases per financial function; isolated sessions; deterministic result checks.

> Tuition lookup is a structured orchestration step. Scholarship and tuition-reduction calculations are Gemini tool calls.

## Summary

| Function | Selection/path | Arguments | Result | End-to-end case pass |
|---|---:|---:|---:|---:|
| Structured tuition lookup | 10/10 | 10/10 | 10/10 | 10/10 |
| Scholarship tool calling | 10/10 | 9/10 | 10/10 | 9/10 |
| Tuition-reduction tool calling | 10/10 | 10/10 | 10/10 | 10/10 |
| **Overall** | **30/30** | **29/30** | **30/30** | **29/30** |

## Case-level evidence

### Case 01 - PASS

- Function: `tuition_lookup`
- Focus: `exact_program_and_cohort`
- Query: Học phí ngành CNTT CLC K49 là bao nhiêu?
- Expected tool/path: `tra_cuu_hoc_phi`
- Selected tool/path: `tra_cuu_hoc_phi`
- Expected arguments: `{"cau_hoi": "Học phí ngành CNTT CLC K49 là bao nhiêu?"}`
- Selected arguments: `{"cau_hoi": "Học phí ngành CNTT CLC K49 là bao nhiêu?"}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
[KẾT QUẢ TRA CỨU HỌC PHÍ CẤU TRÚC - NGUỒN ƯU TIÊN]
Ngành: Công nghệ thông tin
Chương trình: Chất lượng cao (CLC)
Khóa tuyển sinh: 49
- Học phí cố định mỗi năm học (khối kiến thức ngành/cơ sở ngành/chuyên ngành): 36.000.000 đồng
- Học phí mỗi tín chỉ (khối kiến thức ngành/cơ sở ngành/chuyên ngành): 1.254.000 đồng
- Học phí mỗi tín chỉ (khối kiến thức đại cương chung): 441.000 đồng
Năm học của văn bản: 2026-2027
Nguồn: MucHocPhi_ChatLuongCao_TienTien.md
Phải dùng các con số trên; không thay bằng kết quả vector search khác.
```

### Case 02 - PASS

- Function: `tuition_lookup`
- Focus: `general_common_rate`
- Query: Học phí chung của K52 là bao nhiêu một tín chỉ?
- Expected tool/path: `tra_cuu_hoc_phi`
- Selected tool/path: `tra_cuu_hoc_phi`
- Expected arguments: `{"cau_hoi": "Học phí chung của K52 là bao nhiêu một tín chỉ?"}`
- Selected arguments: `{"cau_hoi": "Học phí chung của K52 là bao nhiêu một tín chỉ?"}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
[KẾT QUẢ TRA CỨU HỌC PHÍ CẤU TRÚC - NGUỒN ƯU TIÊN]
Phạm vi: Khối kiến thức đại cương chung
Chương trình: Đại trà/chuẩn
Khóa tuyển sinh: 52
- Học phí mỗi tín chỉ (khối kiến thức đại cương chung): 695.000 đồng
Năm học của văn bản: 2026-2027
Nguồn: MucHocPhi_DaiHocChinhQuy_Khoa52.md
Phải dùng các con số trên; không thay bằng kết quả vector search khác.
```

### Case 03 - PASS

- Function: `tuition_lookup`
- Focus: `standard_program_old_cohort`
- Query: Học phí thực tế ngành CNTT đại trà K49 là bao nhiêu một tín chỉ?
- Expected tool/path: `tra_cuu_hoc_phi`
- Selected tool/path: `tra_cuu_hoc_phi`
- Expected arguments: `{"cau_hoi": "Học phí thực tế ngành CNTT đại trà K49 là bao nhiêu một tín chỉ?"}`
- Selected arguments: `{"cau_hoi": "Học phí thực tế ngành CNTT đại trà K49 là bao nhiêu một tín chỉ?"}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
[KẾT QUẢ TRA CỨU HỌC PHÍ CẤU TRÚC - NGUỒN ƯU TIÊN]
Ngành: Công nghệ thông tin
Chương trình: Đại trà/chuẩn
Khóa tuyển sinh: 49
- Học phí mỗi tín chỉ (khối kiến thức ngành/cơ sở ngành/chuyên ngành): 832.000 đồng
Năm học của văn bản: 2026-2027
Nguồn: MucHocPhi_DaiHocChinhQuy_Khoa51_VeTruoc.md
Phải dùng các con số trên; không thay bằng kết quả vector search khác.
```

### Case 04 - PASS

- Function: `tuition_lookup`
- Focus: `standard_program_new_cohort`
- Query: Học phí thực tế CNTT đại trà khóa 52 là bao nhiêu?
- Expected tool/path: `tra_cuu_hoc_phi`
- Selected tool/path: `tra_cuu_hoc_phi`
- Expected arguments: `{"cau_hoi": "Học phí thực tế CNTT đại trà khóa 52 là bao nhiêu?"}`
- Selected arguments: `{"cau_hoi": "Học phí thực tế CNTT đại trà khóa 52 là bao nhiêu?"}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
[KẾT QUẢ TRA CỨU HỌC PHÍ CẤU TRÚC - NGUỒN ƯU TIÊN]
Ngành: Công nghệ thông tin
Chương trình: Đại trà/chuẩn
Khóa tuyển sinh: 52
- Học phí toàn khóa (khối kiến thức ngành/cơ sở ngành/chuyên ngành): 150.300.000 đồng
- Học phí mỗi tín chỉ (khối kiến thức ngành/cơ sở ngành/chuyên ngành): 966.000 đồng
- Học phí mỗi tín chỉ (khối kiến thức đại cương chung): 695.000 đồng
Năm học của văn bản: 2026-2027
Nguồn: MucHocPhi_DaiHocChinhQuy_Khoa52.md
Phải dùng các con số trên; không thay bằng kết quả vector search khác.
```

### Case 05 - PASS

- Function: `tuition_lookup`
- Focus: `clc_general_common`
- Query: Học phí đại cương chung của chương trình CLC K49 là bao nhiêu?
- Expected tool/path: `tra_cuu_hoc_phi`
- Selected tool/path: `tra_cuu_hoc_phi`
- Expected arguments: `{"cau_hoi": "Học phí đại cương chung của chương trình CLC K49 là bao nhiêu?"}`
- Selected arguments: `{"cau_hoi": "Học phí đại cương chung của chương trình CLC K49 là bao nhiêu?"}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
[KẾT QUẢ TRA CỨU HỌC PHÍ CẤU TRÚC - NGUỒN ƯU TIÊN]
Phạm vi: Khối kiến thức đại cương chung
Chương trình: Chất lượng cao (CLC)
Khóa tuyển sinh: 49
- Học phí mỗi tín chỉ (khối kiến thức đại cương chung): 441.000 đồng
Năm học của văn bản: 2026-2027
Nguồn: MucHocPhi_ChatLuongCao_TienTien.md
Phải dùng các con số trên; không thay bằng kết quả vector search khác.
```

### Case 06 - PASS

- Function: `tuition_lookup`
- Focus: `different_clc_major`
- Query: Kỹ thuật điện CLC K49 đóng học phí thực tế bao nhiêu?
- Expected tool/path: `tra_cuu_hoc_phi`
- Selected tool/path: `tra_cuu_hoc_phi`
- Expected arguments: `{"cau_hoi": "Kỹ thuật điện CLC K49 đóng học phí thực tế bao nhiêu?"}`
- Selected arguments: `{"cau_hoi": "Kỹ thuật điện CLC K49 đóng học phí thực tế bao nhiêu?"}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
[KẾT QUẢ TRA CỨU HỌC PHÍ CẤU TRÚC - NGUỒN ƯU TIÊN]
Ngành: Kỹ thuật điện
Chương trình: Chất lượng cao (CLC)
Khóa tuyển sinh: 49
- Học phí cố định mỗi năm học (khối kiến thức ngành/cơ sở ngành/chuyên ngành): 33.000.000 đồng
- Học phí mỗi tín chỉ (khối kiến thức ngành/cơ sở ngành/chuyên ngành): 1.142.000 đồng
- Học phí mỗi tín chỉ (khối kiến thức đại cương chung): 441.000 đồng
Năm học của văn bản: 2026-2027
Nguồn: MucHocPhi_ChatLuongCao_TienTien.md
Phải dùng các con số trên; không thay bằng kết quả vector search khác.
```

### Case 07 - PASS

- Function: `tuition_lookup`
- Focus: `advanced_program`
- Query: Công nghệ sinh học chương trình tiên tiến K49 có học phí bao nhiêu?
- Expected tool/path: `tra_cuu_hoc_phi`
- Selected tool/path: `tra_cuu_hoc_phi`
- Expected arguments: `{"cau_hoi": "Công nghệ sinh học chương trình tiên tiến K49 có học phí bao nhiêu?"}`
- Selected arguments: `{"cau_hoi": "Công nghệ sinh học chương trình tiên tiến K49 có học phí bao nhiêu?"}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
[KẾT QUẢ TRA CỨU HỌC PHÍ CẤU TRÚC - NGUỒN ƯU TIÊN]
Ngành: Công nghệ sinh học
Chương trình: Tiên tiến
Khóa tuyển sinh: 49
- Học phí cố định mỗi năm học (khối kiến thức ngành/cơ sở ngành/chuyên ngành): 36.000.000 đồng
- Học phí mỗi tín chỉ (khối kiến thức ngành/cơ sở ngành/chuyên ngành): 1.286.000 đồng
- Học phí mỗi tín chỉ (khối kiến thức đại cương chung): 441.000 đồng
Năm học của văn bản: 2026-2027
Nguồn: MucHocPhi_ChatLuongCao_TienTien.md
Phải dùng các con số trên; không thay bằng kết quả vector search khác.
```

### Case 08 - PASS

- Function: `tuition_lookup`
- Focus: `missing_cohort_clarification`
- Query: Học phí ngành CNTT CLC là bao nhiêu?
- Expected tool/path: `tra_cuu_hoc_phi`
- Selected tool/path: `tra_cuu_hoc_phi`
- Expected arguments: `{"cau_hoi": "Học phí ngành CNTT CLC là bao nhiêu?"}`
- Selected arguments: `{"cau_hoi": "Học phí ngành CNTT CLC là bao nhiêu?"}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Bạn vui lòng cho biết khóa tuyển sinh của ngành Công nghệ thông tin (ví dụ K49 hoặc K52).
```

### Case 09 - PASS

- Function: `tuition_lookup`
- Focus: `missing_standard_cohort`
- Query: Học phí CNTT đại trà là bao nhiêu?
- Expected tool/path: `tra_cuu_hoc_phi`
- Selected tool/path: `tra_cuu_hoc_phi`
- Expected arguments: `{"cau_hoi": "Học phí CNTT đại trà là bao nhiêu?"}`
- Selected arguments: `{"cau_hoi": "Học phí CNTT đại trà là bao nhiêu?"}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Bạn vui lòng cho biết khóa tuyển sinh của ngành Công nghệ thông tin (ví dụ K49 hoặc K52).
```

### Case 10 - PASS

- Function: `tuition_lookup`
- Focus: `unknown_major_clarification`
- Query: Học phí ngành Không gian học K49 là bao nhiêu?
- Expected tool/path: `tra_cuu_hoc_phi`
- Selected tool/path: `tra_cuu_hoc_phi`
- Expected arguments: `{"cau_hoi": "Học phí ngành Không gian học K49 là bao nhiêu?"}`
- Selected arguments: `{"cau_hoi": "Học phí ngành Không gian học K49 là bao nhiêu?"}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Bạn vui lòng cho biết tên hoặc mã ngành cần tra cứu học phí.
```

### Case 11 - PASS

- Function: `scholarship_calculation`
- Focus: `excellent_exact_boundary`
- Query: GPA của em là 3.6, điểm rèn luyện 90, ngành CNTT. Hãy tính loại và số tiền học bổng.
- Expected tool/path: `tinh_tien_hoc_bong`
- Selected tool/path: `tinh_tien_hoc_bong`
- Expected arguments: `{"gpa": 3.6, "drl": 90, "khoi_nganh": "CNTT"}`
- Selected arguments: `{"khoi_nganh": "CNTT", "gpa": 3.6, "drl": 90}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Chúc mừng! Với GPA 3.6 và ĐRL 90, bạn đạt học bổng loại **Xuất sắc**.

Sau đây là số tiền bạn sẽ nhận được (tùy thuộc vào khối ngành của bạn):
- Khối I (KH GD và đào tạo giáo viên): 8.810.000 đồng.
- Khối III (Kinh doanh và quản lý, pháp luật): 9.240.000 đồng.
- Khối IV (Khoa học sự sống, khoa học tự nhiên): 9.520.000 đồng.
👉 **(Ngành của bạn) Khối V (Toán, thống kê máy tính, CNTT, CNKT, kỹ thuật, SX và chế biến): 10.560.000 đồng.**
- Khối VI (Sức khỏe): 10.560.000 đồng.
- Khối VII (Nhân văn, KHXH và hành vi, báo chí và TT, DVXH, DL, KS, TDTT.): 9.240.000 đồng.
- Khối CTTT_K50 (Chương trình tiên tiến, chất lượng cao từ khóa 50 về trước): 13.090.000 đồng.
- Khối CTTT_K51 (Chương trình tiên tiến, chất lượng cao khóa 51): 15.860.000 đồng.

```

### Case 12 - PASS

- Function: `scholarship_calculation`
- Focus: `gpa_limits_class`
- Query: Em học CNTT, GPA 3.59 và điểm rèn luyện 95 thì đạt học bổng loại nào, bao nhiêu tiền?
- Expected tool/path: `tinh_tien_hoc_bong`
- Selected tool/path: `tinh_tien_hoc_bong`
- Expected arguments: `{"gpa": 3.59, "drl": 95, "khoi_nganh": "CNTT"}`
- Selected arguments: `{"drl": 95, "khoi_nganh": "CNTT", "gpa": 3.59}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Chúc mừng! Với GPA 3.59 và ĐRL 95, bạn đạt học bổng loại **Giỏi**.

Sau đây là số tiền bạn sẽ nhận được (tùy thuộc vào khối ngành của bạn):
- Khối I (KH GD và đào tạo giáo viên): 7.550.000 đồng.
- Khối III (Kinh doanh và quản lý, pháp luật): 7.920.000 đồng.
- Khối IV (Khoa học sự sống, khoa học tự nhiên): 8.160.000 đồng.
👉 **(Ngành của bạn) Khối V (Toán, thống kê máy tính, CNTT, CNKT, kỹ thuật, SX và chế biến): 9.050.000 đồng.**
- Khối VI (Sức khỏe): 9.050.000 đồng.
- Khối VII (Nhân văn, KHXH và hành vi, báo chí và TT, DVXH, DL, KS, TDTT.): 7.920.000 đồng.
- Khối CTTT_K50 (Chương trình tiên tiến, chất lượng cao từ khóa 50 về trước): 11.220.000 đồng.
- Khối CTTT_K51 (Chương trình tiên tiến, chất lượng cao khóa 51): 13.600.000 đồng.

```

### Case 13 - PASS

- Function: `scholarship_calculation`
- Focus: `good_exact_boundary`
- Query: GPA 3.2, rèn luyện 80, khối Kinh doanh và quản lý. Tính học bổng giúp em.
- Expected tool/path: `tinh_tien_hoc_bong`
- Selected tool/path: `tinh_tien_hoc_bong`
- Expected arguments: `{"gpa": 3.2, "drl": 80, "khoi_nganh": "Kinh doanh"}`
- Selected arguments: `{"gpa": 3.2, "drl": 80, "khoi_nganh": "Kinh doanh và quản lý"}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Chúc mừng! Với GPA 3.2 và ĐRL 80, bạn đạt học bổng loại **Giỏi**.

Sau đây là số tiền bạn sẽ nhận được (tùy thuộc vào khối ngành của bạn):
- Khối I (KH GD và đào tạo giáo viên): 7.550.000 đồng.
👉 **(Ngành của bạn) Khối III (Kinh doanh và quản lý, pháp luật): 7.920.000 đồng.**
- Khối IV (Khoa học sự sống, khoa học tự nhiên): 8.160.000 đồng.
- Khối V (Toán, thống kê máy tính, CNTT, CNKT, kỹ thuật, SX và chế biến): 9.050.000 đồng.
- Khối VI (Sức khỏe): 9.050.000 đồng.
- Khối VII (Nhân văn, KHXH và hành vi, báo chí và TT, DVXH, DL, KS, TDTT.): 7.920.000 đồng.
- Khối CTTT_K50 (Chương trình tiên tiến, chất lượng cao từ khóa 50 về trước): 11.220.000 đồng.
- Khối CTTT_K51 (Chương trình tiên tiến, chất lượng cao khóa 51): 13.600.000 đồng.

```

### Case 14 - PASS

- Function: `scholarship_calculation`
- Focus: `lower_metric_controls_class`
- Query: Em thuộc khối Kinh doanh, GPA 3.19 và ĐRL 90. Em được học bổng gì và bao nhiêu?
- Expected tool/path: `tinh_tien_hoc_bong`
- Selected tool/path: `tinh_tien_hoc_bong`
- Expected arguments: `{"gpa": 3.19, "drl": 90, "khoi_nganh": "Kinh doanh"}`
- Selected arguments: `{"khoi_nganh": "Kinh doanh", "gpa": 3.19, "drl": 90}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Chúc mừng! Với GPA 3.19 và ĐRL 90, bạn đạt học bổng loại **Khá**.

Sau đây là số tiền bạn sẽ nhận được (tùy thuộc vào khối ngành của bạn):
- Khối I (KH GD và đào tạo giáo viên): 6.290.000 đồng.
👉 **(Ngành của bạn) Khối III (Kinh doanh và quản lý, pháp luật): 6.600.000 đồng.**
- Khối IV (Khoa học sự sống, khoa học tự nhiên): 6.800.000 đồng.
- Khối V (Toán, thống kê máy tính, CNTT, CNKT, kỹ thuật, SX và chế biến): 7.540.000 đồng.
- Khối VI (Sức khỏe): 7.540.000 đồng.
- Khối VII (Nhân văn, KHXH và hành vi, báo chí và TT, DVXH, DL, KS, TDTT.): 6.600.000 đồng.
- Khối CTTT_K50 (Chương trình tiên tiến, chất lượng cao từ khóa 50 về trước): 9.350.000 đồng.
- Khối CTTT_K51 (Chương trình tiên tiến, chất lượng cao khóa 51): 11.330.000 đồng.

```

### Case 15 - PASS

- Function: `scholarship_calculation`
- Focus: `fair_exact_boundary`
- Query: GPA 2.5, điểm rèn luyện 65, em học khối Sức khỏe. Tính mức học bổng.
- Expected tool/path: `tinh_tien_hoc_bong`
- Selected tool/path: `tinh_tien_hoc_bong`
- Expected arguments: `{"gpa": 2.5, "drl": 65, "khoi_nganh": "Sức khỏe"}`
- Selected arguments: `{"gpa": 2.5, "khoi_nganh": "Sức khỏe", "drl": 65}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Chúc mừng! Với GPA 2.5 và ĐRL 65, bạn đạt học bổng loại **Khá**.

Sau đây là số tiền bạn sẽ nhận được (tùy thuộc vào khối ngành của bạn):
- Khối I (KH GD và đào tạo giáo viên): 6.290.000 đồng.
- Khối III (Kinh doanh và quản lý, pháp luật): 6.600.000 đồng.
- Khối IV (Khoa học sự sống, khoa học tự nhiên): 6.800.000 đồng.
- Khối V (Toán, thống kê máy tính, CNTT, CNKT, kỹ thuật, SX và chế biến): 7.540.000 đồng.
👉 **(Ngành của bạn) Khối VI (Sức khỏe): 7.540.000 đồng.**
- Khối VII (Nhân văn, KHXH và hành vi, báo chí và TT, DVXH, DL, KS, TDTT.): 6.600.000 đồng.
- Khối CTTT_K50 (Chương trình tiên tiến, chất lượng cao từ khóa 50 về trước): 9.350.000 đồng.
- Khối CTTT_K51 (Chương trình tiên tiến, chất lượng cao khóa 51): 11.330.000 đồng.

```

### Case 16 - PASS

- Function: `scholarship_calculation`
- Focus: `gpa_below_minimum`
- Query: Em học CNTT, GPA 2.49 nhưng điểm rèn luyện 95. Hãy tính xem em có học bổng không.
- Expected tool/path: `tinh_tien_hoc_bong`
- Selected tool/path: `tinh_tien_hoc_bong`
- Expected arguments: `{"gpa": 2.49, "drl": 95, "khoi_nganh": "CNTT"}`
- Selected arguments: `{"khoi_nganh": "CNTT", "drl": 95, "gpa": 2.49}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Rất tiếc! Với GPA 2.49 và ĐRL 95, bạn chưa đủ điều kiện nhận học bổng. (Lưu ý: Để đạt loại Khá cần GPA >= 2.5 và ĐRL >= 65).
```

### Case 17 - PASS

- Function: `scholarship_calculation`
- Focus: `conduct_below_minimum`
- Query: GPA của em 3.8, ĐRL 64, ngành CNTT. Tính học bổng giúp em.
- Expected tool/path: `tinh_tien_hoc_bong`
- Selected tool/path: `tinh_tien_hoc_bong`
- Expected arguments: `{"gpa": 3.8, "drl": 64, "khoi_nganh": "CNTT"}`
- Selected arguments: `{"gpa": 3.8, "drl": 64, "khoi_nganh": "CNTT"}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Rất tiếc! Với GPA 3.8 và ĐRL 64, bạn chưa đủ điều kiện nhận học bổng. (Lưu ý: Để đạt loại Khá cần GPA >= 2.5 và ĐRL >= 65).
```

### Case 18 - PASS

- Function: `scholarship_calculation`
- Focus: `teacher_sector_amount`
- Query: Em học khối Giáo dục và đào tạo giáo viên, GPA 3.7, rèn luyện 92. Học bổng bao nhiêu?
- Expected tool/path: `tinh_tien_hoc_bong`
- Selected tool/path: `tinh_tien_hoc_bong`
- Expected arguments: `{"gpa": 3.7, "drl": 92, "khoi_nganh": "giáo viên"}`
- Selected arguments: `{"gpa": 3.7, "drl": 92, "khoi_nganh": "Giáo dục và đào tạo giáo viên"}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Chúc mừng! Với GPA 3.7 và ĐRL 92, bạn đạt học bổng loại **Xuất sắc**.

Sau đây là số tiền bạn sẽ nhận được (tùy thuộc vào khối ngành của bạn):
- Khối I (KH GD và đào tạo giáo viên): 8.810.000 đồng.
- Khối III (Kinh doanh và quản lý, pháp luật): 9.240.000 đồng.
- Khối IV (Khoa học sự sống, khoa học tự nhiên): 9.520.000 đồng.
- Khối V (Toán, thống kê máy tính, CNTT, CNKT, kỹ thuật, SX và chế biến): 10.560.000 đồng.
- Khối VI (Sức khỏe): 10.560.000 đồng.
- Khối VII (Nhân văn, KHXH và hành vi, báo chí và TT, DVXH, DL, KS, TDTT.): 9.240.000 đồng.
- Khối CTTT_K50 (Chương trình tiên tiến, chất lượng cao từ khóa 50 về trước): 13.090.000 đồng.
- Khối CTTT_K51 (Chương trình tiên tiến, chất lượng cao khóa 51): 15.860.000 đồng.

```

### Case 19 - FAIL

- Function: `scholarship_calculation`
- Focus: `clc_k51_amount`
- Query: Em học chương trình chất lượng cao khóa 51, GPA 3.3 và ĐRL 85. Tính học bổng cho em.
- Expected tool/path: `tinh_tien_hoc_bong`
- Selected tool/path: `tinh_tien_hoc_bong`
- Expected arguments: `{"gpa": 3.3, "drl": 85, "khoi_nganh": "chất lượng cao khóa 51"}`
- Selected arguments: `{"drl": 85, "khoi_nganh": "", "gpa": 3.3}`
- Checks: selection/path=PASS, arguments=FAIL, result=PASS

**Tool output**

```text
Chúc mừng! Với GPA 3.3 và ĐRL 85, bạn đạt học bổng loại **Giỏi**.

Sau đây là số tiền bạn sẽ nhận được (tùy thuộc vào khối ngành của bạn):
- Khối I (KH GD và đào tạo giáo viên): 7.550.000 đồng.
- Khối III (Kinh doanh và quản lý, pháp luật): 7.920.000 đồng.
- Khối IV (Khoa học sự sống, khoa học tự nhiên): 8.160.000 đồng.
- Khối V (Toán, thống kê máy tính, CNTT, CNKT, kỹ thuật, SX và chế biến): 9.050.000 đồng.
- Khối VI (Sức khỏe): 9.050.000 đồng.
- Khối VII (Nhân văn, KHXH và hành vi, báo chí và TT, DVXH, DL, KS, TDTT.): 7.920.000 đồng.
- Khối CTTT_K50 (Chương trình tiên tiến, chất lượng cao từ khóa 50 về trước): 11.220.000 đồng.
- Khối CTTT_K51 (Chương trình tiên tiến, chất lượng cao khóa 51): 13.600.000 đồng.

```

### Case 20 - PASS

- Function: `scholarship_calculation`
- Focus: `missing_sector_lists_all`
- Query: GPA 3.7 và điểm rèn luyện 95 nhưng em chưa cung cấp khối ngành. Hãy tính loại học bổng và liệt kê số tiền các khối.
- Expected tool/path: `tinh_tien_hoc_bong`
- Selected tool/path: `tinh_tien_hoc_bong`
- Expected arguments: `{"gpa": 3.7, "drl": 95, "khoi_nganh": ""}`
- Selected arguments: `{"gpa": 3.7, "drl": 95, "khoi_nganh": ""}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Chúc mừng! Với GPA 3.7 và ĐRL 95, bạn đạt học bổng loại **Xuất sắc**.

Sau đây là số tiền bạn sẽ nhận được (tùy thuộc vào khối ngành của bạn):
- Khối I (KH GD và đào tạo giáo viên): 8.810.000 đồng.
- Khối III (Kinh doanh và quản lý, pháp luật): 9.240.000 đồng.
- Khối IV (Khoa học sự sống, khoa học tự nhiên): 9.520.000 đồng.
- Khối V (Toán, thống kê máy tính, CNTT, CNKT, kỹ thuật, SX và chế biến): 10.560.000 đồng.
- Khối VI (Sức khỏe): 10.560.000 đồng.
- Khối VII (Nhân văn, KHXH và hành vi, báo chí và TT, DVXH, DL, KS, TDTT.): 9.240.000 đồng.
- Khối CTTT_K50 (Chương trình tiên tiến, chất lượng cao từ khóa 50 về trước): 13.090.000 đồng.
- Khối CTTT_K51 (Chương trình tiên tiến, chất lượng cao khóa 51): 15.860.000 đồng.

```

### Case 21 - PASS

- Function: `tuition_reduction_calculation`
- Focus: `seventy_percent`
- Query: Học phí thực tế 832000 đồng/tín chỉ, mức cơ sở miễn giảm 538000 đồng và được giảm 70%. Tính số tiền còn đóng.
- Expected tool/path: `tinh_toan_hoc_phi`
- Selected tool/path: `tinh_toan_hoc_phi`
- Expected arguments: `{"gia_hoc_phi_thuc_te": 832000, "muc_tran_mien_giam": 538000, "phan_tram_giam": 70}`
- Selected arguments: `{"phan_tram_giam": 70, "muc_tran_mien_giam": 538000, "gia_hoc_phi_thuc_te": 832000}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Học phí thực tế: 832.000đ/tín chỉ.
Mức trần (cơ sở miễn giảm): 538.000đ/tín chỉ.
Số tiền được Nhà nước miễn giảm (70.0% x 538.000): 376.600đ/tín chỉ.
=> SỐ TIỀN THỰC TẾ SINH VIÊN PHẢI ĐÓNG LÀ: 455.400đ/tín chỉ.
```

### Case 22 - PASS

- Function: `tuition_reduction_calculation`
- Focus: `full_basis_not_full_actual`
- Query: Học phí thực tế là 695000 đồng, trần miễn giảm 451000 đồng, em được miễn 100%. Còn phải đóng bao nhiêu?
- Expected tool/path: `tinh_toan_hoc_phi`
- Selected tool/path: `tinh_toan_hoc_phi`
- Expected arguments: `{"gia_hoc_phi_thuc_te": 695000, "muc_tran_mien_giam": 451000, "phan_tram_giam": 100}`
- Selected arguments: `{"phan_tram_giam": 100, "gia_hoc_phi_thuc_te": 695000, "muc_tran_mien_giam": 451000}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Học phí thực tế: 695.000đ/tín chỉ.
Mức trần (cơ sở miễn giảm): 451.000đ/tín chỉ.
Số tiền được Nhà nước miễn giảm (100.0% x 451.000): 451.000đ/tín chỉ.
=> SỐ TIỀN THỰC TẾ SINH VIÊN PHẢI ĐÓNG LÀ: 244.000đ/tín chỉ.
```

### Case 23 - PASS

- Function: `tuition_reduction_calculation`
- Focus: `fifty_percent`
- Query: Mức học phí thực tế 966000 đồng, cơ sở miễn giảm 538000 đồng, giảm 50%. Hãy tính tiền được giảm và tiền còn đóng.
- Expected tool/path: `tinh_toan_hoc_phi`
- Selected tool/path: `tinh_toan_hoc_phi`
- Expected arguments: `{"gia_hoc_phi_thuc_te": 966000, "muc_tran_mien_giam": 538000, "phan_tram_giam": 50}`
- Selected arguments: `{"phan_tram_giam": 50, "muc_tran_mien_giam": 538000, "gia_hoc_phi_thuc_te": 966000}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Học phí thực tế: 966.000đ/tín chỉ.
Mức trần (cơ sở miễn giảm): 538.000đ/tín chỉ.
Số tiền được Nhà nước miễn giảm (50.0% x 538.000): 269.000đ/tín chỉ.
=> SỐ TIỀN THỰC TẾ SINH VIÊN PHẢI ĐÓNG LÀ: 697.000đ/tín chỉ.
```

### Case 24 - PASS

- Function: `tuition_reduction_calculation`
- Focus: `zero_due_exact`
- Query: Học phí và mức cơ sở đều là 451000 đồng/tín chỉ, được miễn 100%. Tính số tiền phải đóng.
- Expected tool/path: `tinh_toan_hoc_phi`
- Selected tool/path: `tinh_toan_hoc_phi`
- Expected arguments: `{"gia_hoc_phi_thuc_te": 451000, "muc_tran_mien_giam": 451000, "phan_tram_giam": 100}`
- Selected arguments: `{"gia_hoc_phi_thuc_te": 451000, "muc_tran_mien_giam": 451000, "phan_tram_giam": 100}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Học phí thực tế: 451.000đ/tín chỉ.
Mức trần (cơ sở miễn giảm): 451.000đ/tín chỉ.
Số tiền được Nhà nước miễn giảm (100.0% x 451.000): 451.000đ/tín chỉ.
=> SỐ TIỀN THỰC TẾ SINH VIÊN PHẢI ĐÓNG LÀ: 0đ/tín chỉ.
```

### Case 25 - PASS

- Function: `tuition_reduction_calculation`
- Focus: `clamp_negative_to_zero`
- Query: Học phí thực tế 500000 đồng nhưng cơ sở miễn giảm 600000 đồng, được miễn 100%. Tính tiền còn đóng và không để kết quả âm.
- Expected tool/path: `tinh_toan_hoc_phi`
- Selected tool/path: `tinh_toan_hoc_phi`
- Expected arguments: `{"gia_hoc_phi_thuc_te": 500000, "muc_tran_mien_giam": 600000, "phan_tram_giam": 100}`
- Selected arguments: `{"gia_hoc_phi_thuc_te": 500000, "muc_tran_mien_giam": 600000, "phan_tram_giam": 100}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Học phí thực tế: 500.000đ/tín chỉ.
Mức trần (cơ sở miễn giảm): 600.000đ/tín chỉ.
Số tiền được Nhà nước miễn giảm (100.0% x 600.000): 600.000đ/tín chỉ.
=> SỐ TIỀN THỰC TẾ SINH VIÊN PHẢI ĐÓNG LÀ: 0đ/tín chỉ.
```

### Case 26 - PASS

- Function: `tuition_reduction_calculation`
- Focus: `clc_actual_vs_basis`
- Query: Học phí CLC thực tế 1254000 đồng/tín chỉ, mức cơ sở 441000 đồng, giảm 70%. Em còn đóng bao nhiêu?
- Expected tool/path: `tinh_toan_hoc_phi`
- Selected tool/path: `tinh_toan_hoc_phi`
- Expected arguments: `{"gia_hoc_phi_thuc_te": 1254000, "muc_tran_mien_giam": 441000, "phan_tram_giam": 70}`
- Selected arguments: `{"phan_tram_giam": 70, "gia_hoc_phi_thuc_te": 1254000, "muc_tran_mien_giam": 441000}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Học phí thực tế: 1.254.000đ/tín chỉ.
Mức trần (cơ sở miễn giảm): 441.000đ/tín chỉ.
Số tiền được Nhà nước miễn giảm (70.0% x 441.000): 308.700đ/tín chỉ.
=> SỐ TIỀN THỰC TẾ SINH VIÊN PHẢI ĐÓNG LÀ: 945.300đ/tín chỉ.
```

### Case 27 - PASS

- Function: `tuition_reduction_calculation`
- Focus: `zero_percent`
- Query: Học phí thực tế 832000 đồng, cơ sở miễn giảm 538000 đồng nhưng mức giảm là 0%. Tính số tiền phải đóng.
- Expected tool/path: `tinh_toan_hoc_phi`
- Selected tool/path: `tinh_toan_hoc_phi`
- Expected arguments: `{"gia_hoc_phi_thuc_te": 832000, "muc_tran_mien_giam": 538000, "phan_tram_giam": 0}`
- Selected arguments: `{"phan_tram_giam": 0, "muc_tran_mien_giam": 538000, "gia_hoc_phi_thuc_te": 832000}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Học phí thực tế: 832.000đ/tín chỉ.
Mức trần (cơ sở miễn giảm): 538.000đ/tín chỉ.
Số tiền được Nhà nước miễn giảm (0.0% x 538.000): 0đ/tín chỉ.
=> SỐ TIỀN THỰC TẾ SINH VIÊN PHẢI ĐÓNG LÀ: 832.000đ/tín chỉ.
```

### Case 28 - PASS

- Function: `tuition_reduction_calculation`
- Focus: `decimal_free_money`
- Query: Học phí thực tế 749000 đồng/tín chỉ, mức cơ sở 487000 đồng và giảm 70%. Tính tiền được giảm và còn đóng.
- Expected tool/path: `tinh_toan_hoc_phi`
- Selected tool/path: `tinh_toan_hoc_phi`
- Expected arguments: `{"gia_hoc_phi_thuc_te": 749000, "muc_tran_mien_giam": 487000, "phan_tram_giam": 70}`
- Selected arguments: `{"phan_tram_giam": 70, "muc_tran_mien_giam": 487000, "gia_hoc_phi_thuc_te": 749000}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Học phí thực tế: 749.000đ/tín chỉ.
Mức trần (cơ sở miễn giảm): 487.000đ/tín chỉ.
Số tiền được Nhà nước miễn giảm (70.0% x 487.000): 340.900đ/tín chỉ.
=> SỐ TIỀN THỰC TẾ SINH VIÊN PHẢI ĐÓNG LÀ: 408.100đ/tín chỉ.
```

### Case 29 - PASS

- Function: `tuition_reduction_calculation`
- Focus: `clc_electric_rate`
- Query: Học phí thực tế 1142000 đồng, trần miễn giảm 441000 đồng, được giảm 50%. Còn phải đóng bao nhiêu?
- Expected tool/path: `tinh_toan_hoc_phi`
- Selected tool/path: `tinh_toan_hoc_phi`
- Expected arguments: `{"gia_hoc_phi_thuc_te": 1142000, "muc_tran_mien_giam": 441000, "phan_tram_giam": 50}`
- Selected arguments: `{"gia_hoc_phi_thuc_te": 1142000, "muc_tran_mien_giam": 441000, "phan_tram_giam": 50}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Học phí thực tế: 1.142.000đ/tín chỉ.
Mức trần (cơ sở miễn giảm): 441.000đ/tín chỉ.
Số tiền được Nhà nước miễn giảm (50.0% x 441.000): 220.500đ/tín chỉ.
=> SỐ TIỀN THỰC TẾ SINH VIÊN PHẢI ĐÓNG LÀ: 921.500đ/tín chỉ.
```

### Case 30 - PASS

- Function: `tuition_reduction_calculation`
- Focus: `advanced_program_full_basis`
- Query: Học phí thực tế 1286000 đồng, mức cơ sở miễn giảm 441000 đồng, miễn 100%. Tính số tiền còn đóng.
- Expected tool/path: `tinh_toan_hoc_phi`
- Selected tool/path: `tinh_toan_hoc_phi`
- Expected arguments: `{"gia_hoc_phi_thuc_te": 1286000, "muc_tran_mien_giam": 441000, "phan_tram_giam": 100}`
- Selected arguments: `{"gia_hoc_phi_thuc_te": 1286000, "phan_tram_giam": 100, "muc_tran_mien_giam": 441000}`
- Checks: selection/path=PASS, arguments=PASS, result=PASS

**Tool output**

```text
Học phí thực tế: 1.286.000đ/tín chỉ.
Mức trần (cơ sở miễn giảm): 441.000đ/tín chỉ.
Số tiền được Nhà nước miễn giảm (100.0% x 441.000): 441.000đ/tín chỉ.
=> SỐ TIỀN THỰC TẾ SINH VIÊN PHẢI ĐÓNG LÀ: 845.000đ/tín chỉ.
```
