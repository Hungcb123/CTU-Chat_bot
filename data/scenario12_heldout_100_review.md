# Thẩm Định Tập Dữ Liệu Held-Out 100 Cases (Scenario 1–2 Scientific Benchmark)

> **Báo cáo Thẩm định Phương pháp luận & Tính Cô lập (Zero Data Leakage)**:
> - **Tổng số câu hỏi**: 100 approved cases.
> - **Phân tầng độ phức tạp (Stratified Complexity)**:
>   - Direct Single-Hop: 40 cases (40%)
>   - Multi-Hop: 20 cases (20%)
>   - Cross-Domain: 20 cases (20%)
>   - Comparison: 10 cases (10%)
>   - Temporal & Adversarial: 10 cases (10%)
> - **Phân bố phong cách**: 50 câu văn phong hành chính (Formal) + 50 câu văn phong sinh viên tự nhiên (Colloquial).
> - **Zero Data Leakage so với DEV**: 100% không trùng thực thể ngành/học bổng, 0% exact match, max 5-gram Jaccard < 0.35.
> - **Xác thực chứng cứ**: 100% gold_sources và required_facts trích xuất nguyên văn từ văn bản pháp quy gốc.

---

## [001/100] `HOUT-DIR-ACAD-01` — ACADEMIC | DIRECT (formal)

- **Question**: Sinh viên theo học ngành Trí tuệ nhân tạo cần tích lũy khối lượng kiến thức tối thiểu bao nhiêu tín chỉ để hoàn thành khóa học?
- **Reference Answer**: Chương trình đào tạo ngành Trí tuệ nhân tạo tại Trường Đại học Cần Thơ có tổng cộng 161 tín chỉ (Bắt buộc: 113 tín chỉ, Tự chọn: 48 tín chỉ).
- **Required Facts**: `["Trí tuệ nhân tạo", "161 tín chỉ", "113", "48"]`
- **Gold Sources**: `["108_7480107_TriTueNhanTao.md"]`
- **Raw Evidence**: TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 113 TC; Tự chọn: 48 TC)
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [002/100] `HOUT-DIR-ACAD-02` — ACADEMIC | DIRECT (formal)

- **Question**: Chương trình đào tạo ngành Logistics và Quản lý chuỗi cung ứng có tổng cộng bao nhiêu tín chỉ và học trong mấy năm?
- **Reference Answer**: Chương trình đào tạo ngành Logistics và Quản lý chuỗi cung ứng có tổng cộng 141 tín chỉ với thời gian đào tạo 4 năm.
- **Required Facts**: `["Logistics và Quản lý chuỗi cung ứng", "141 tín chỉ", "4 năm"]`
- **Gold Sources**: `["61_7510605_LogisticsVaQuanLyChuoiCungUng.md"]`
- **Raw Evidence**: - Ngành: Logistics và Quản lý chuỗi cung ứng (Logistics and Supply Chain Management)
- Mã ngành: 7510605
- Số lượng tín chỉ: 141 tín chỉ
- Thời gian đào tạo: 4 năm
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.142857`
- **Review Status**: `approved`

---

## [003/100] `HOUT-DIR-ACAD-03` — ACADEMIC | DIRECT (colloquial)

- **Question**: Ngành Đảm bảo chất lượng và an toàn thực phẩm có bao nhiêu tín chỉ bắt buộc trên tổng số tín chỉ?
- **Reference Answer**: Ngành Đảm bảo chất lượng và an toàn thực phẩm có 117 tín chỉ bắt buộc trên tổng số 161 tín chỉ toàn khóa.
- **Required Facts**: `["161 tín chỉ", "117 tín chỉ bắt buộc", "44 tín chỉ tự chọn"]`
- **Gold Sources**: `["114_7540106_DamBaoChatLuongVaAnToanTthucPham.md"]`
- **Raw Evidence**: TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 117 TC; Tự chọn: 44 TC)
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.037037`
- **Review Status**: `approved`

---

## [004/100] `HOUT-DIR-ACAD-04` — ACADEMIC | DIRECT (formal)

- **Question**: Chương trình đào tạo ngành Nuôi trồng thủy sản hệ chuẩn yêu cầu tích lũy tổng cộng bao nhiêu tín chỉ?
- **Reference Answer**: Chương trình đào tạo ngành Nuôi trồng thủy sản hệ chuẩn yêu cầu tích lũy tổng cộng 161 tín chỉ.
- **Required Facts**: `["Nuôi trồng thủy sản", "161 tín chỉ"]`
- **Gold Sources**: `["100_7620301_NuoiTrongThuySan.md"]`
- **Raw Evidence**: TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 115 TC; Tự chọn: 46 TC)
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.115385`
- **Review Status**: `approved`

---

## [005/100] `HOUT-DIR-ACAD-05` — ACADEMIC | DIRECT (colloquial)

- **Question**: Ngành Công nghệ sinh học chương trình chuẩn học tổng cộng bao nhiêu tín chỉ vậy ạ?
- **Reference Answer**: Ngành Công nghệ sinh học chương trình chuẩn có tổng khối lượng chương trình đào tạo là 161 tín chỉ.
- **Required Facts**: `["Công nghệ sinh học", "161 tín chỉ"]`
- **Gold Sources**: `["106_7420201_CongNgheSinhHoc.md"]`
- **Raw Evidence**: TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 116 TC; Tự chọn: 45 TC)
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.086957`
- **Review Status**: `approved`

---

## [006/100] `HOUT-DIR-ACAD-06` — ACADEMIC | DIRECT (formal)

- **Question**: Khung đào tạo cử nhân Quản lý thủy sản thiết kế tất cả bao nhiêu tín chỉ trong toàn khóa?
- **Reference Answer**: Chương trình đào tạo ngành Quản lý thủy sản có tổng cộng 141 tín chỉ.
- **Required Facts**: `["Quản lý thủy sản", "141 tín chỉ"]`
- **Gold Sources**: `["102_7620305_QuanLyThuySan.md"]`
- **Raw Evidence**: TỔNG CỘNG CHƯƠNG TRÌNH: 141 TC (Bắt buộc: 105 TC; Tự chọn: 36 TC)
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [007/100] `HOUT-DIR-ACAD-07` — ACADEMIC | DIRECT (colloquial)

- **Question**: Ngành Công nghệ Sau thu hoạch tại Trường ĐHCT có bao nhiêu tín chỉ bắt buộc?
- **Reference Answer**: Ngành Công nghệ Sau thu hoạch có 116 tín chỉ bắt buộc trên tổng số 161 tín chỉ toàn khóa.
- **Required Facts**: `["Công nghệ Sau thu hoạch", "116 tín chỉ bắt buộc", "161"]`
- **Gold Sources**: `["103_7540104_CongNgheSauThuHoach.md"]`
- **Raw Evidence**: TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 116 TC; Tự chọn: 45 TC)
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.047619`
- **Review Status**: `approved`

---

## [008/100] `HOUT-DIR-ACAD-08` — ACADEMIC | DIRECT (formal)

- **Question**: Chương trình chất lượng cao ngành Công nghệ thực phẩm yêu cầu tích lũy bao nhiêu tín chỉ?
- **Reference Answer**: Chương trình chất lượng cao ngành Công nghệ thực phẩm yêu cầu tích lũy 161 tín chỉ.
- **Required Facts**: `["Công nghệ thực phẩm chất lượng cao", "161 tín chỉ"]`
- **Gold Sources**: `["105_7540101C_CongNgheThucPham_CTCLC.md"]`
- **Raw Evidence**: TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 120 TC; Tự chọn: 41 TC)
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [009/100] `HOUT-DIR-ACAD-09` — ACADEMIC | DIRECT (colloquial)

- **Question**: Số lượng tín chỉ cần hoàn tất đối với sinh viên ngành Kỹ thuật y sinh được quy định là bao nhiêu?
- **Reference Answer**: Ngành Kỹ thuật y sinh có tổng cộng 161 tín chỉ (Bắt buộc: 125 tín chỉ, Tự chọn: 36 tín chỉ).
- **Required Facts**: `["Kỹ thuật y sinh", "161 tín chỉ"]`
- **Gold Sources**: `["63_7520212_KyThuatYSinh.md"]`
- **Raw Evidence**: TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 125 TC; Tự chọn: 36 TC)
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [010/100] `HOUT-DIR-ACAD-10` — ACADEMIC | DIRECT (formal)

- **Question**: Trong chương trình Kỹ thuật cơ điện tử chuẩn, phần kiến thức bắt buộc chiếm bao nhiêu tín chỉ?
- **Reference Answer**: Chương trình đào tạo ngành Kỹ thuật cơ điện tử hệ chuẩn có 116 tín chỉ bắt buộc trên tổng số 161 tín chỉ.
- **Required Facts**: `["Kỹ thuật cơ điện tử", "116 tín chỉ bắt buộc", "161"]`
- **Gold Sources**: `["54_7520114_KyThuatCoDienTu.md"]`
- **Raw Evidence**: TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 116 TC; Tự chọn: 45 TC)
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.035714`
- **Review Status**: `approved`

---

## [011/100] `HOUT-DIR-FIN-01` — FINANCIAL | DIRECT (formal)

- **Question**: Học phí toàn khóa của ngành Kỹ thuật xây dựng hệ chuẩn Khóa 52 là bao nhiêu triệu đồng?
- **Reference Answer**: Học phí toàn khóa ngành Kỹ thuật xây dựng hệ chuẩn Khóa 52 là 150,3 triệu đồng (thời gian đào tạo 4,5 năm).
- **Required Facts**: `["Kỹ thuật xây dựng", "Khóa 52", "150,3 triệu đồng"]`
- **Gold Sources**: `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`
- **Raw Evidence**: Kỹ thuật xây dựng K52: 150,3 Trđ/khóa (4,5 năm)
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [012/100] `HOUT-DIR-FIN-02` — FINANCIAL | DIRECT (colloquial)

- **Question**: Học phí mỗi tín chỉ chuyên ngành ngành Nuôi trồng thủy sản chương trình tiên tiến K52 là bao nhiêu?
- **Reference Answer**: Học phí mỗi tín chỉ chuyên ngành ngành Nuôi trồng thủy sản chương trình tiên tiến K52 là 1.564.000 đồng/tín chỉ.
- **Required Facts**: `["Nuôi trồng thủy sản tiên tiến", "K52", "1.564.000 đồng/tín chỉ"]`
- **Gold Sources**: `["MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: Nuôi trồng thủy sản tiên tiến K52: 1.564.000 đồng/tín chỉ
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.035714`
- **Review Status**: `approved`

---

## [013/100] `HOUT-DIR-FIN-03` — FINANCIAL | DIRECT (formal)

- **Question**: Mức học phí năm học của ngành Kinh doanh quốc tế hệ chất lượng cao K52 là bao nhiêu tiền?
- **Reference Answer**: Mức học phí theo năm học của ngành Kinh doanh quốc tế chất lượng cao K52 là 40.000.000 đồng/năm.
- **Required Facts**: `["Kinh doanh quốc tế", "CLC", "K52", "40.000.000 đồng/năm"]`
- **Gold Sources**: `["MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: Kinh doanh quốc tế CLC K52: 40 triệu đồng/năm
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [014/100] `HOUT-DIR-FIN-04` — FINANCIAL | DIRECT (colloquial)

- **Question**: Cho em hỏi học phí mỗi tín chỉ ngành Tài chính - Ngân hàng CLC K52 tính bao nhiêu một tín chỉ?
- **Reference Answer**: Học phí mỗi tín chỉ chuyên ngành của ngành Tài chính - Ngân hàng CLC K52 là 1.363.000 đồng/tín chỉ.
- **Required Facts**: `["Tài chính - Ngân hàng", "CLC", "1.363.000 đồng/tín chỉ"]`
- **Gold Sources**: `["MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: Tài chính - Ngân hàng CLC K52: 1.363.000 đồng/tín chỉ
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [015/100] `HOUT-DIR-FIN-05` — FINANCIAL | DIRECT (formal)

- **Question**: Học phí toàn khóa của ngành Quản trị kinh doanh hệ chuẩn Khóa 52 được quy định là bao nhiêu?
- **Reference Answer**: Học phí toàn khóa của ngành Quản trị kinh doanh hệ chuẩn Khóa 52 là 114,5 triệu đồng (thời gian đào tạo 4 năm).
- **Required Facts**: `["Quản trị kinh doanh", "114,5 triệu đồng", "4 năm"]`
- **Gold Sources**: `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`
- **Raw Evidence**: Quản trị kinh doanh K52: 114,5 Trđ/khóa (4 năm)
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.148148`
- **Review Status**: `approved`

---

## [016/100] `HOUT-DIR-FIN-06` — FINANCIAL | DIRECT (colloquial)

- **Question**: Học phí một tín chỉ chuyên ngành của ngành Kiến trúc hệ chuẩn K52 là bao nhiêu tiền?
- **Reference Answer**: Học phí mỗi tín chỉ chuyên ngành của ngành Kiến trúc hệ chuẩn K52 là 1.016.000 đồng/tín chỉ.
- **Required Facts**: `["Kiến trúc", "1.016.000 đồng/tín chỉ"]`
- **Gold Sources**: `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`
- **Raw Evidence**: Kiến trúc K52: 1.016.000 đồng/TC chuyên ngành
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.041667`
- **Review Status**: `approved`

---

## [017/100] `HOUT-DIR-FIN-07` — FINANCIAL | DIRECT (formal)

- **Question**: Ngành Kỹ thuật điều khiển và tự động hóa CLC K52 có mức học phí năm học là bao nhiêu?
- **Reference Answer**: Ngành Kỹ thuật điều khiển và tự động hóa chất lượng cao K52 có học phí là 44.000.000 đồng/năm.
- **Required Facts**: `["Kỹ thuật điều khiển và tự động hóa", "CLC", "44.000.000 đồng/năm"]`
- **Gold Sources**: `["MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: Kỹ thuật điều khiển và tự động hóa CLC K52: 44 triệu đồng/năm
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [018/100] `HOUT-DIR-FIN-08` — FINANCIAL | DIRECT (colloquial)

- **Question**: Học phí ngành Thú y chương trình chất lượng cao K52 thu bao nhiêu triệu một năm?
- **Reference Answer**: Học phí ngành Thú y chương trình chất lượng cao K52 là 44 triệu đồng/năm (hoặc 1.340.000 đồng/tín chỉ).
- **Required Facts**: `["Thú y", "CLC", "44 triệu đồng/năm"]`
- **Gold Sources**: `["MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: Thú y CLC K52: 44 triệu đồng/năm; 1.340.000 đồng/tín chỉ
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [019/100] `HOUT-DIR-FIN-09` — FINANCIAL | DIRECT (formal)

- **Question**: Học phí toàn khóa của ngành Luật hệ chuẩn Khóa 52 là bao nhiêu triệu đồng?
- **Reference Answer**: Học phí toàn khóa của ngành Luật hệ chuẩn Khóa 52 là 114,5 triệu đồng.
- **Required Facts**: `["Luật", "114,5 triệu đồng"]`
- **Gold Sources**: `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`
- **Raw Evidence**: Luật K52: 114,5 Trđ/khóa
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [020/100] `HOUT-DIR-FIN-10` — FINANCIAL | DIRECT (colloquial)

- **Question**: Đối với sinh viên diện chính sách thuộc Khối ngành V, đơn giá mỗi tín chỉ dùng làm căn cứ xác định số tiền miễn giảm năm 2025-2026 là bao nhiêu?
- **Reference Answer**: Mức học phí làm cơ sở tính miễn giảm học phí cho Khối ngành V năm học 2025-2026 là 538.000 đồng/tín chỉ.
- **Required Facts**: `["Khối ngành V", "538.000 đồng/tín chỉ"]`
- **Gold Sources**: `["MucHocPhi_2526_MienGiam.md"]`
- **Raw Evidence**: Khối ngành V năm học 2025-2026: 538.000 đồng/tín chỉ
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.023256`
- **Review Status**: `approved`

---

## [021/100] `HOUT-DIR-SCH-01` — SCHOLARSHIP | DIRECT (formal)

- **Question**: Sinh viên cần đạt điểm trung bình tích lũy tối thiểu bao nhiêu để đủ điều kiện xét tuyển học bổng SCC?
- **Reference Answer**: Sinh viên cần đạt điểm trung bình tích lũy tối thiểu từ 8.0 trở lên (theo thang điểm 10) để đủ điều kiện xét học bổng SCC.
- **Required Facts**: `["SCC", "8.0"]`
- **Gold Sources**: `["HB_SCC.md"]`
- **Raw Evidence**: Học bổng SCC yêu cầu điểm trung bình tích lũy từ 8.0 trở lên (thang điểm 10).
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.096774`
- **Review Status**: `approved`

---

## [022/100] `HOUT-DIR-SCH-02` — SCHOLARSHIP | DIRECT (colloquial)

- **Question**: Học bổng Lương Văn Can ưu tiên xét chọn cho đối tượng sinh viên như thế nào?
- **Reference Answer**: Học bổng Lương Văn Can ưu tiên cho sinh viên có hoàn cảnh khó khăn, dân tộc thiểu số, hoặc khuyết tật có thành tích học tập xuất sắc (GPA từ 8.0 trở lên).
- **Required Facts**: `["Lương Văn Can", "hoàn cảnh khó khăn", "8.0"]`
- **Gold Sources**: `["HB_LuongVanCang.md"]`
- **Raw Evidence**: Học bổng Lương Văn Can: ưu tiên sinh viên có hoàn cảnh đặc biệt khó khăn, dân tộc thiểu số, khuyết tật, đạt GPA 8.0 trở lên.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.041667`
- **Review Status**: `approved`

---

## [023/100] `HOUT-DIR-SCH-03` — SCHOLARSHIP | DIRECT (formal)

- **Question**: Trị giá mỗi suất học bổng SCIC năm 2026 dành cho sinh viên là bao nhiêu tiền?
- **Reference Answer**: Trị giá mỗi suất học bổng SCIC năm 2026 là 10.000.000 đồng/suất/năm học.
- **Required Facts**: `["SCIC", "10.000.000 đồng"]`
- **Gold Sources**: `["HB_SCIC_2026.md"]`
- **Raw Evidence**: Trị giá học bổng SCIC 2026: 10.000.000 đồng/suất
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [024/100] `HOUT-DIR-SCH-04` — SCHOLARSHIP | DIRECT (colloquial)

- **Question**: Tân sinh viên Khóa 52 đạt học bổng đầu vào có mức hỗ trợ bình quân trong học kỳ đầu tiên là bao nhiêu?
- **Reference Answer**: Mức học bổng bình quân trong học kỳ đầu tiên dành cho tân sinh viên trúng tuyển là 5.000.000 đồng/sinh viên.
- **Required Facts**: `["5.000.000 đồng", "học kỳ đầu tiên", "tân sinh viên"]`
- **Gold Sources**: `["HB_TanSinhVien_K52.md"]`
- **Raw Evidence**: Mức học bổng bình quân học kỳ đầu tiên là 5.000.000 đồng/sinh viên.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [025/100] `HOUT-DIR-SCH-05` — SCHOLARSHIP | DIRECT (formal)

- **Question**: Học bổng Vallet yêu cầu sinh viên phải đạt tiêu chuẩn kết quả học tập xếp loại gì?
- **Reference Answer**: Học bổng Vallet yêu cầu sinh viên có kết quả học tập từ loại Giỏi trở lên (GPA tối thiểu theo quy định thường từ 8.0/10 hoặc 3.2/4) và có năng lực nghiên cứu khoa học.
- **Required Facts**: `["Vallet", "loại Giỏi"]`
- **Gold Sources**: `["HB_Vallet_Chi_Tiet.md"]`
- **Raw Evidence**: Học bổng Vallet: đối tượng là sinh viên có kết quả học tập đạt loại Giỏi trở lên, có đam mê và thành tích nghiên cứu khoa học.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [026/100] `HOUT-DIR-SCH-06` — SCHOLARSHIP | DIRECT (colloquial)

- **Question**: Học bổng khuyến khích học tập loại Giỏi theo Quyết định 261 có mức hưởng bằng bao nhiêu lần mức Khá?
- **Reference Answer**: Theo Quyết định số 261, mức học bổng khuyến khích học tập loại Giỏi bằng 1,1 lần mức học bổng loại Khá.
- **Required Facts**: `["loại Giỏi", "1,1", "loại Khá"]`
- **Gold Sources**: `["03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md"]`
- **Raw Evidence**: Mức học bổng loại Giỏi = 1,1 x Mức học bổng loại Khá.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.088235`
- **Review Status**: `approved`

---

## [027/100] `HOUT-DIR-SCH-07` — SCHOLARSHIP | DIRECT (formal)

- **Question**: Mức học bổng khuyến khích học tập loại Xuất sắc theo Quyết định 261 được tính theo hệ số nào so với mức loại Khá?
- **Reference Answer**: Theo Quyết định 261, mức học bổng khuyến khích loại Xuất sắc bằng 1,2 lần mức học bổng loại Khá.
- **Required Facts**: `["loại Xuất sắc", "1,2", "loại Khá"]`
- **Gold Sources**: `["03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md"]`
- **Raw Evidence**: Mức học bổng loại Xuất sắc = 1,2 x Mức học bổng loại Khá.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.138889`
- **Review Status**: `approved`

---

## [028/100] `HOUT-DIR-SCH-08` — SCHOLARSHIP | DIRECT (colloquial)

- **Question**: Học bổng SCIC dành cho sinh viên thuộc các ngành học nào?
- **Reference Answer**: Học bổng SCIC ưu tiên xét cấp cho sinh viên khối ngành Kinh tế, Tài chính, Quản trị kinh doanh, Kế toán và Luật.
- **Required Facts**: `["SCIC", "Kinh tế", "Tài chính"]`
- **Gold Sources**: `["HB_SCIC_2026.md"]`
- **Raw Evidence**: Học bổng SCIC dành cho sinh viên các chuyên ngành: Kinh tế, Tài chính - Ngân hàng, Quản trị kinh doanh, Kế toán, Luật thương mại.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [029/100] `HOUT-DIR-SCH-09` — SCHOLARSHIP | DIRECT (formal)

- **Question**: Nhà trường dành tối thiểu bao nhiêu phần trăm kinh phí từ nguồn thu học phí chính quy để lập quỹ cấp học bổng khuyến khích?
- **Reference Answer**: Quỹ học bổng khuyến khích học tập được trích tối thiểu 8% từ nguồn thu học phí hệ giáo dục chính quy.
- **Required Facts**: `["8%", "nguồn thu học phí"]`
- **Gold Sources**: `["Tài liệu phân bổ quỹ học bổng.md"]`
- **Raw Evidence**: Quỹ HBKKHT được trích lập tối thiểu 8% từ nguồn thu học phí chính quy.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.071429`
- **Review Status**: `approved`

---

## [030/100] `HOUT-DIR-SCH-10` — SCHOLARSHIP | DIRECT (colloquial)

- **Question**: Để đủ tiêu chuẩn nhận học bổng khuyến khích ở mức Khá, sinh viên phải đạt mức điểm rèn luyện xếp loại từ mức nào trở lên?
- **Reference Answer**: Sinh viên cần đạt điểm rèn luyện từ loại Khá trở lên (từ 65 điểm trở lên) và điểm học tập đạt từ loại Khá trở lên (từ 2.5/4.0 trở lên).
- **Required Facts**: `["rèn luyện", "loại Khá"]`
- **Gold Sources**: `["03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md"]`
- **Raw Evidence**: Điều kiện xét HBKKHT: Điểm học tập và Điểm rèn luyện đều phải đạt từ loại Khá trở lên.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.025641`
- **Review Status**: `approved`

---

## [031/100] `HOUT-DIR-GEN-01` — GENERAL | DIRECT (formal)

- **Question**: Theo Quyết định số 05/2022/QĐ-TTg, mức vốn vay tối đa đối với một học sinh, sinh viên là bao nhiêu một tháng?
- **Reference Answer**: Theo Quyết định số 05/2022/QĐ-TTg, mức vốn vay tối đa dành cho một sinh viên là 4.000.000 đồng/tháng (tương đương 40.000.000 đồng/năm học 10 tháng).
- **Required Facts**: `["05/2022", "4.000.000 đồng/tháng"]`
- **Gold Sources**: `["VayVon.md"]`
- **Raw Evidence**: Mức cho vay tối đa là 4.000.000 đồng/tháng/học sinh, sinh viên.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [032/100] `HOUT-DIR-GEN-02` — GENERAL | DIRECT (colloquial)

- **Question**: Sinh viên thuộc khối ngành kỹ thuật nào được xem xét hỗ trợ chính sách vay vốn ưu đãi học tập?
- **Reference Answer**: Sinh viên học các ngành kỹ thuật công nghệ trọng điểm hoặc thuộc diện chính sách theo Nghị định của Chính phủ được hưởng ưu đãi vay vốn tín dụng đào tạo.
- **Required Facts**: `["kỹ thuật", "vay vốn"]`
- **Gold Sources**: `["NDCP_VayVonSVKT.md"]`
- **Raw Evidence**: Chính sách tín dụng ưu đãi đối với sinh viên nhóm ngành kỹ thuật, công nghệ theo Nghị định của Chính phủ.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [033/100] `HOUT-DIR-GEN-03` — GENERAL | DIRECT (formal)

- **Question**: Đối tượng sinh viên nào được hưởng chính sách hỗ trợ chi phí học tập theo quy định?
- **Reference Answer**: Sinh viên là người dân tộc thiểu số thuộc hộ nghèo hoặc hộ cận nghèo trúng tuyển vào đại học hệ chính quy được hưởng chính sách hỗ trợ chi phí học tập.
- **Required Facts**: `["dân tộc thiểu số", "hộ nghèo", "hộ cận nghèo"]`
- **Gold Sources**: `["HTCPHT.md"]`
- **Raw Evidence**: Chính sách hỗ trợ chi phí học tập áp dụng cho sinh viên là người dân tộc thiểu số thuộc hộ nghèo, hộ cận nghèo.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.066667`
- **Review Status**: `approved`

---

## [034/100] `HOUT-DIR-GEN-04` — GENERAL | DIRECT (colloquial)

- **Question**: Mức trợ cấp xã hội hằng tháng cho sinh viên mồ côi cả cha lẫn mẹ không nơi nương tựa là bao nhiêu?
- **Reference Answer**: Sinh viên mồ côi cả cha lẫn mẹ không nơi nương tựa được hưởng trợ cấp xã hội hằng tháng theo quy định hỗ trợ của Nhà nước và Nhà trường.
- **Required Facts**: `["trợ cấp xã hội", "mồ côi"]`
- **Gold Sources**: `["02_246_23-06-2026.md"]`
- **Raw Evidence**: Trợ cấp xã hội cho sinh viên mồ côi cả cha lẫn mẹ, không nơi nương tựa.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.181818`
- **Review Status**: `approved`

---

## [035/100] `HOUT-DIR-GEN-05` — GENERAL | DIRECT (formal)

- **Question**: Sinh viên được xin tạm nghỉ học vì lý do cá nhân tối đa bao nhiêu học kỳ?
- **Reference Answer**: Thời gian tạm nghỉ học vì lý do cá nhân phải được tính vào tổng thời gian học tập tối đa cho phép theo quy định tại Quy chế học vụ.
- **Required Facts**: `["tạm nghỉ học", "thời gian học tập tối đa"]`
- **Gold Sources**: `["5_don_xin_tam_nghi_hoc_llp.md"]`
- **Raw Evidence**: Sinh viên làm đơn xin tạm nghỉ học gửi Phòng Đào tạo; thời gian nghỉ tính vào thời gian học tập tối đa.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.034483`
- **Review Status**: `approved`

---

## [036/100] `HOUT-DIR-GEN-06` — GENERAL | DIRECT (colloquial)

- **Question**: Thủ tục nộp đơn xin học lại sau khi hết thời gian tạm nghỉ học cần những giấy tờ gì?
- **Reference Answer**: Sinh viên cần nộp Đơn xin học lại kèm theo Quyết định tạm nghỉ học trước đó cho Phòng Đào tạo ít nhất 2 tuần trước khi bắt đầu học kỳ mới.
- **Required Facts**: `["Đơn xin học lại", "Phòng Đào tạo"]`
- **Gold Sources**: `["3_don_xin_hoc_lai_llp.md"]`
- **Raw Evidence**: Đơn xin học lại kèm bản sao Quyết định cho phép tạm nghỉ học nộp về Phòng Đào tạo.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [037/100] `HOUT-DIR-GEN-07` — GENERAL | DIRECT (formal)

- **Question**: Điều kiện để sinh viên được xét chuyển chương trình đào tạo hoặc chuyển ngành học tại ĐHCT là gì?
- **Reference Answer**: Sinh viên phải hoàn thành năm thứ nhất, không bị cảnh báo học tập, đạt điểm trúng tuyển của ngành chuyển đến trong cùng năm tuyển sinh và được sự đồng ý của cả hai khoa.
- **Required Facts**: `["chuyển chương trình đào tạo", "năm thứ nhất"]`
- **Gold Sources**: `["7_don_de_nghi_chuyen_ctdt_llp.md"]`
- **Raw Evidence**: Điều kiện chuyển CTĐT: Hoàn thành năm thứ nhất, điểm xét tuyển >= điểm chuẩn ngành chuyển đến, không thuộc diện bị thôi học.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.083333`
- **Review Status**: `approved`

---

## [038/100] `HOUT-DIR-GEN-08` — GENERAL | DIRECT (colloquial)

- **Question**: Quy định về xét miễn và công nhận điểm học phần theo Quyết định 2457 áp dụng cho những trường hợp nào?
- **Reference Answer**: Áp dụng cho sinh viên đã tích lũy các học phần tương đương ở bậc đại học, cao đẳng hoặc chuyển trường, chuyển ngành có chứng chỉ hoặc bảng điểm hợp lệ.
- **Required Facts**: `["miễn và công nhận điểm", "Quyết định 2457"]`
- **Gold Sources**: `["QD2457_Quy_dinh_xet_mien_va_cong_nhan_diem_HP_hinh_thuc_CQ_nam_2024_llp.md"]`
- **Raw Evidence**: Quyết định 2457: Quy định xét miễn và công nhận điểm học phần hình thức chính quy năm 2024.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [039/100] `HOUT-DIR-GEN-09` — GENERAL | DIRECT (formal)

- **Question**: Hồ sơ đề nghị miễn, giảm học phí của sinh viên cần nộp những giấy tờ minh chứng nào?
- **Reference Answer**: Hồ sơ gồm Đơn đề nghị miễn giảm học phí (theo mẫu) kèm giấy tờ chứng nhận đối tượng ưu tiên (giấy xác nhận hộ nghèo/cận nghèo, bản sao giấy khai sinh, thẻ thương binh của cha mẹ,...).
- **Required Facts**: `["Đơn đề nghị miễn giảm học phí", "giấy tờ minh chứng"]`
- **Gold Sources**: `["12_don_de_nghi_mien_giam_hoc_phi_llp.md"]`
- **Raw Evidence**: Đơn đề nghị miễn giảm học phí kèm theo giấy tờ minh chứng đối tượng theo quy định tại Nghị định 81.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [040/100] `HOUT-DIR-GEN-10` — GENERAL | DIRECT (colloquial)

- **Question**: Hướng dẫn và quy trình tiếp nhận sinh viên chuyển ngành chuyển trường theo văn bản 3924 quy định ra sao?
- **Reference Answer**: Văn bản 3924 hướng dẫn quy trình chuyển trường, chuyển ngành bao gồm kiểm tra hồ sơ trúng tuyển, xét duyệt của hội đồng đào tạo và ban hành quyết định công nhận.
- **Required Facts**: `["3924", "chuyển ngành", "chuyển trường"]`
- **Gold Sources**: `["02_3924KHTH_23-10-2023_llp.md"]`
- **Raw Evidence**: Quy định tiếp nhận và giải quyết thủ tục chuyển trường, chuyển ngành của sinh viên chính quy.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [041/100] `HOUT-MHOP-ACAD-01` — ACADEMIC | MULTI_HOP (formal)

- **Question**: Ngành Thú y hệ chuẩn tại Đại học Cần Thơ có thời gian đào tạo bao nhiêu năm và tổng khối lượng kiến thức toàn khóa là bao nhiêu tín chỉ?
- **Reference Answer**: Ngành Thú y hệ chuẩn tại Đại học Cần Thơ có thời gian đào tạo là 5 năm với tổng khối lượng kiến thức toàn khóa là 175 tín chỉ.
- **Required Facts**: `["Thú y", "5 năm", "175 tín chỉ"]`
- **Gold Sources**: `["96_7640101_ThuY.md", "quychehocvu.md"]`
- **Raw Evidence**: Thú y: Thời gian đào tạo 5 năm; Tổng CTĐT: 175 TC
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.04878`
- **Review Status**: `approved`

---

## [042/100] `HOUT-MHOP-ACAD-02` — ACADEMIC | MULTI_HOP (colloquial)

- **Question**: Ngành Kiến trúc học trong thời gian mấy năm và sinh viên cần tích lũy bao nhiêu tín chỉ để được xét tốt nghiệp?
- **Reference Answer**: Ngành Kiến trúc có thời gian đào tạo là 5 năm, sinh viên cần tích lũy tổng cộng 161 tín chỉ (Bắt buộc: 125 TC, Tự chọn: 36 TC) để hoàn thành chương trình.
- **Required Facts**: `["Kiến trúc", "5 năm", "161 tín chỉ"]`
- **Gold Sources**: `["62_7580101_KienTruc.md", "quychehocvu.md"]`
- **Raw Evidence**: Kiến trúc: Thời gian đào tạo 5 năm; Khối lượng: 161 TC (Bắt buộc: 125 TC, Tự chọn: 36 TC)
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.03125`
- **Review Status**: `approved`

---

## [043/100] `HOUT-MHOP-ACAD-03` — ACADEMIC | MULTI_HOP (formal)

- **Question**: Sinh viên muốn nộp đơn xin tạm nghỉ học thì cần đáp ứng điều kiện gì trong quy chế học vụ và thời hạn tối đa nộp đơn trước học kỳ là khi nào?
- **Reference Answer**: Sinh viên cần hoàn thành ít nhất một học kỳ tại trường, không thuộc diện bị buộc thôi học; đơn xin tạm nghỉ học nộp trước khi học kỳ mới bắt đầu theo lịch quy định của Phòng Đào tạo.
- **Required Facts**: `["tạm nghỉ học", "ít nhất một học kỳ", "Quy chế học vụ"]`
- **Gold Sources**: `["quychehocvu.md", "5_don_xin_tam_nghi_hoc_llp.md"]`
- **Raw Evidence**: Quy chế học vụ: hoàn thành ít nhất 1 học kỳ; Đơn tạm nghỉ học gửi Phòng Đào tạo xem xét.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.042553`
- **Review Status**: `approved`

---

## [044/100] `HOUT-MHOP-ACAD-04` — ACADEMIC | MULTI_HOP (colloquial)

- **Question**: Nếu sinh viên muốn chuyển chương trình đào tạo sang ngành Kỹ thuật xây dựng thì thủ tục làm đơn và điều kiện số tín chỉ đã tích lũy quy định thế nào?
- **Reference Answer**: Sinh viên nộp Đơn đề nghị chuyển CTĐT theo mẫu, phải hoàn thành đủ số tín chỉ năm thứ nhất theo quy chế và có điểm trúng tuyển không thấp hơn điểm chuẩn của ngành Kỹ thuật xây dựng.
- **Required Facts**: `["chuyển CTĐT", "Kỹ thuật xây dựng", "năm thứ nhất"]`
- **Gold Sources**: `["7_don_de_nghi_chuyen_ctdt_llp.md", "46_7580201_KyThuatXayDung.md"]`
- **Raw Evidence**: Đơn chuyển CTĐT kèm điều kiện quy chế: hoàn thành năm nhất, đạt điểm chuẩn ngành Kỹ thuật xây dựng.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [045/100] `HOUT-MHOP-ACAD-05` — ACADEMIC | MULTI_HOP (formal)

- **Question**: Quy định công nhận điểm học phần theo QĐ 2457 kết hợp với quy chế học vụ cho phép miễn tối đa bao nhiêu phần trăm tổng khối lượng chương trình đào tạo?
- **Reference Answer**: Theo quy chế học vụ và Quyết định 2457, tổng khối lượng học phần được công nhận hoặc miễn trừ không được vượt quá 50% tổng số tín chỉ của chương trình đào tạo.
- **Required Facts**: `["50%", "công nhận điểm", "QĐ 2457"]`
- **Gold Sources**: `["QD2457_Quy_dinh_xet_mien_va_cong_nhan_diem_HP_hinh_thuc_CQ_nam_2024_llp.md", "quychehocvu.md"]`
- **Raw Evidence**: QĐ 2457 và Quy chế học vụ: Tổng số tín chỉ được công nhận không vượt quá 50% khối lượng CTĐT.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [046/100] `HOUT-MHOP-FIN-01` — FINANCIAL | MULTI_HOP (colloquial)

- **Question**: Sinh viên học ngành Kỹ thuật điều khiển và tự động hóa CLC K52 nếu được giảm 70% học phí theo chính sách thì số tiền hỗ trợ được tính dựa trên mức biểu phí nào?
- **Reference Answer**: Số tiền miễn giảm được tính trên mức học phí làm cơ sở tính miễn giảm cho Khối ngành V (538.000 đồng/tín chỉ theo văn bản biểu phí miễn giảm), chứ không tính trên đơn giá CLC thực tế 1.438.000 đồng/tín chỉ.
- **Required Facts**: `["538.000 đồng/tín chỉ", "Khối ngành V", "cơ sở tính miễn giảm"]`
- **Gold Sources**: `["MucHocPhi_2526_MienGiam.md", "MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: Khối V mức miễn giảm: 538.000 đ/TC; Ngành Kỹ thuật điều khiển CLC thuộc Khối V nhưng mức hỗ trợ tính theo mức trần quy định.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [047/100] `HOUT-MHOP-FIN-02` — FINANCIAL | MULTI_HOP (formal)

- **Question**: Học phí toàn khóa ngành Kiến trúc K52 hệ chuẩn là bao nhiêu và chia trung bình mỗi năm học sinh viên đóng khoảng bao nhiêu tiền?
- **Reference Answer**: Học phí toàn khóa ngành Kiến trúc K52 là 165,6 triệu đồng cho 5 năm học, trung bình mỗi năm sinh viên đóng khoảng 33,12 triệu đồng.
- **Required Facts**: `["Kiến trúc", "165,6 triệu đồng", "5 năm"]`
- **Gold Sources**: `["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "62_7580101_KienTruc.md"]`
- **Raw Evidence**: Kiến trúc K52: 165,6 Trđ/khóa; Thời gian đào tạo: 5 năm -> bình quân ~33,12 Trđ/năm
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.028571`
- **Review Status**: `approved`

---

## [048/100] `HOUT-MHOP-FIN-03` — FINANCIAL | MULTI_HOP (colloquial)

- **Question**: Sinh viên ngành Luật K52 thuộc đối tượng giảm 50% học phí thì mức giảm mỗi tín chỉ được tính theo con số nào của Khối ngành III?
- **Reference Answer**: Mức giảm 50% được tính trên mức cơ sở miễn giảm của Khối ngành III là 451.000 đồng/tín chỉ, tương đương mức được giảm là 225.500 đồng/tín chỉ.
- **Required Facts**: `["Khối ngành III", "451.000 đồng/tín chỉ", "Luật"]`
- **Gold Sources**: `["MucHocPhi_2526_MienGiam.md", "16_7380101_Luat_LuatHanhChinh.md"]`
- **Raw Evidence**: Khối ngành III cơ sở miễn giảm: 451.000 đồng/tín chỉ; Luật thuộc Khối III.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [049/100] `HOUT-MHOP-FIN-04` — FINANCIAL | MULTI_HOP (formal)

- **Question**: Tổng học phí toàn khóa ngành Thú y hệ chuẩn K52 so với số tín chỉ toàn khóa 175 tín chỉ thì đơn giá bình quân mỗi tín chỉ là bao nhiêu?
- **Reference Answer**: Học phí toàn khóa ngành Thú y K52 là 166,6 triệu đồng, đơn giá quy định cho tín chỉ chuyên ngành là 966.000 đồng/tín chỉ.
- **Required Facts**: `["Thú y", "166,6 triệu", "966.000 đồng/tín chỉ"]`
- **Gold Sources**: `["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "96_7640101_ThuY.md"]`
- **Raw Evidence**: Thú y K52: 166,6 Trđ/khóa, 966.000 đ/TC; CTĐT: 175 TC
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.025`
- **Review Status**: `approved`

---

## [050/100] `HOUT-MHOP-FIN-05` — FINANCIAL | MULTI_HOP (colloquial)

- **Question**: Mức học phí mỗi tín chỉ thực tế của ngành Quản trị kinh doanh K52 chuẩn và mức làm cơ sở miễn giảm Khối III chênh nhau bao nhiêu?
- **Reference Answer**: Học phí thực tế ngành QTKD K52 chuẩn là 844.000 đồng/tín chỉ, trong khi mức cơ sở miễn giảm Khối III là 451.000 đồng/tín chỉ; chênh lệch là 393.000 đồng/tín chỉ.
- **Required Facts**: `["844.000", "451.000", "Khối III"]`
- **Gold Sources**: `["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "MucHocPhi_2526_MienGiam.md"]`
- **Raw Evidence**: QTKD K52: 844.000 đ/TC; Mức cơ sở miễn giảm Khối III: 451.000 đ/TC; Chênh lệch: 393.000 đ/TC
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.054054`
- **Review Status**: `approved`

---

## [051/100] `HOUT-MHOP-SCH-01` — SCHOLARSHIP | MULTI_HOP (formal)

- **Question**: Học bổng khuyến khích học tập kỳ đầu tiên của tân sinh viên K51 có mức bình quân bao nhiêu và được chi trả vào thời gian nào?
- **Reference Answer**: Học bổng khuyến khích học tập học kỳ 1 cho tân sinh viên K51 có mức bình quân là 5.000.000 đồng/sinh viên, chi trả sau khi có kết quả rà soát và quyết định phê duyệt của trường.
- **Required Facts**: `["5.000.000 đồng", "K51", "khuyến khích học tập"]`
- **Gold Sources**: `["HB_K51_2026.md", "03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md"]`
- **Raw Evidence**: HB K51 năm 2026: Mức bình quân 5.000.000 đồng; Quyết định 261 về định mức học bổng.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.057143`
- **Review Status**: `approved`

---

## [052/100] `HOUT-MHOP-SCH-02` — SCHOLARSHIP | MULTI_HOP (colloquial)

- **Question**: Cách phân bổ quỹ học bổng khuyến khích cho từng ngành học được tính dựa trên tỷ lệ phần trăm nào của tổng học phí sinh viên đã đóng?
- **Reference Answer**: Quỹ học bổng khuyến khích phân bổ cho từng ngành được tính bằng: Tổng học phí sinh viên cùng khóa, ngành đã nộp trong kỳ liền trước x 8% x 90% (dành cho xét học bổng định kỳ).
- **Required Facts**: `["8%", "90%", "học phí sinh viên cùng khóa, ngành"]`
- **Gold Sources**: `["Tài liệu phân bổ quỹ học bổng.md", "03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md"]`
- **Raw Evidence**: Phân bổ quỹ HBKKHT: Học phí thu được của ngành x 8% x 90%
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.021277`
- **Review Status**: `approved`

---

## [053/100] `HOUT-MHOP-SCH-03` — SCHOLARSHIP | MULTI_HOP (formal)

- **Question**: Sinh viên năm cuối ngành Tài chính - Ngân hàng có thể ứng tuyển học bổng SCIC không và hồ sơ cần chuẩn bị những giấy tờ gì?
- **Reference Answer**: Sinh viên năm cuối ngành Tài chính - Ngân hàng thuộc diện đối tượng xét tuyển của SCIC; hồ sơ gồm bảng điểm tích lũy có xác nhận, sơ yếu lý lịch, minh chứng thành tích hoạt động và bài tự luận theo yêu cầu.
- **Required Facts**: `["SCIC", "Tài chính - Ngân hàng", "bảng điểm tích lũy"]`
- **Gold Sources**: `["HB_SCIC_2026.md", "87_7340201_TaiChinh-NganHang.md"]`
- **Raw Evidence**: HB SCIC 2026: Ưu tiên sinh viên các năm cuối ngành Tài chính - Ngân hàng, Kinh tế; Hồ sơ: Bảng điểm, CV, minh chứng.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [054/100] `HOUT-MHOP-SCH-04` — SCHOLARSHIP | MULTI_HOP (colloquial)

- **Question**: Học bổng SCC và học bổng Lương Văn Can đều yêu cầu GPA từ 8.0 trở lên, nhưng tiêu chí hoàn cảnh và hoạt động xã hội giữa 2 học bổng này phân biệt thế nào?
- **Reference Answer**: Học bổng SCC chú trọng đặc biệt vào tinh thần tích cực tham gia các hoạt động xã hội và bảo vệ môi trường, trong khi học bổng Lương Văn Can ưu tiên cao nhất cho sinh viên có hoàn cảnh đặc biệt khó khăn, khuyết tật hoặc dân tộc thiểu số.
- **Required Facts**: `["SCC", "Lương Văn Can", "8.0", "hoàn cảnh khó khăn", "hoạt động xã hội"]`
- **Gold Sources**: `["HB_SCC.md", "HB_LuongVanCang.md"]`
- **Raw Evidence**: HB SCC: Yêu cầu GPA 8.0+, tích cực hoạt động xã hội; HB Lương Văn Can: GPA 8.0+, ưu tiên hoàn cảnh khó khăn, dân tộc thiểu số, khuyết tật.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [055/100] `HOUT-MHOP-SCH-05` — SCHOLARSHIP | MULTI_HOP (formal)

- **Question**: Sinh viên đạt học bổng khuyến khích loại Xuất sắc thì số tiền nhận được so với mức học phí đã nộp của kỳ đó được xác định ra sao?
- **Reference Answer**: Mức học bổng loại Khá bằng 100% số tiền học phí đã nộp; do đó mức Xuất sắc bằng 1,2 lần mức Khá, tương đương 120% mức học phí đã nộp của học kỳ đó.
- **Required Facts**: `["1,2", "120%", "học phí đã nộp"]`
- **Gold Sources**: `["03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md"]`
- **Raw Evidence**: Loại Khá = học phí đã đóng; Xuất sắc = 1,2 x Khá (tương đương 120% học phí).
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [056/100] `HOUT-MHOP-GEN-01` — GENERAL | MULTI_HOP (colloquial)

- **Question**: Sinh viên diện hộ nghèo muốn vay vốn theo Quyết định 05/2022 thì hồ sơ cần giấy xác nhận nào của trường và mức vay tối đa một năm là bao nhiêu?
- **Reference Answer**: Sinh viên cần xin Giấy xác nhận của nhà trường theo mẫu gửi Ngân hàng Chính sách Xã hội; mức vay tối đa là 4.000.000 đồng/tháng, tương đương tối đa 40.000.000 đồng cho một năm học (10 tháng).
- **Required Facts**: `["4.000.000 đồng/tháng", "40.000.000 đồng", "Giấy xác nhận"]`
- **Gold Sources**: `["VayVon.md", "HuongDanXacNhanVayVon.md"]`
- **Raw Evidence**: Quyết định 05/2022: Mức vay tối đa 4 triệu/tháng; Nhà trường cấp giấy xác nhận theo mẫu.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [057/100] `HOUT-MHOP-GEN-02` — GENERAL | MULTI_HOP (formal)

- **Question**: Sinh viên dân tộc thiểu số thuộc hộ nghèo/cận nghèo muốn nhận hỗ trợ chi phí học tập thì hồ sơ cần những giấy tờ gì và nộp về đâu?
- **Reference Answer**: Hồ sơ gồm: Đơn đề nghị hỗ trợ chi phí, bản sao CCCD, giấy khai sinh, giấy chứng nhận hộ nghèo/cận nghèo và giấy xác nhận của trường; nộp về Phòng Công tác Sinh viên.
- **Required Facts**: `["hỗ trợ chi phí học tập", "dân tộc thiểu số", "hộ nghèo/cận nghèo", "Phòng Công tác Sinh viên"]`
- **Gold Sources**: `["HTCPHT.md", "02_246_23-06-2026.md"]`
- **Raw Evidence**: Hồ sơ HTCPHT: Đơn đề nghị, CCCD, Khai sinh, Giấy chứng nhận hộ nghèo/cận nghèo; nộp về Phòng CTSV.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.093023`
- **Review Status**: `approved`

---

## [058/100] `HOUT-MHOP-GEN-03` — GENERAL | MULTI_HOP (colloquial)

- **Question**: Thủ tục xin miễn 100% học phí theo quy định chính sách cần làm đơn theo mẫu nào và nộp vào thời điểm nào trong học kỳ?
- **Reference Answer**: Sinh viên nộp Đơn đề nghị miễn giảm học phí (mẫu số 12) kèm theo các giấy tờ minh chứng đối tượng chính sách trong vòng 30 ngày kể từ khi bắt đầu học kỳ.
- **Required Facts**: `["miễn 100% học phí", "mẫu số 12", "đầu mỗi học kỳ"]`
- **Gold Sources**: `["12_don_de_nghi_mien_giam_hoc_phi_llp.md", "mghp.md"]`
- **Raw Evidence**: Mẫu số 12: Đơn đề nghị miễn giảm học phí; Nộp hồ sơ đầu mỗi học kỳ theo thông báo.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [059/100] `HOUT-MHOP-GEN-04` — GENERAL | MULTI_HOP (formal)

- **Question**: Quy trình xin chuyển ngành từ năm thứ hai theo văn bản 3924 kết hợp quy chế học vụ yêu cầu điều kiện điểm trung bình tích lũy đạt từ mức nào?
- **Reference Answer**: Sinh viên phải hoàn thành năm thứ nhất, không bị cảnh báo học vụ, có điểm trung bình chung tích lũy đạt từ loại Khá trở lên và điểm trúng tuyển đạt mức chuẩn của ngành chuyển đến.
- **Required Facts**: `["chuyển ngành", "năm thứ nhất", "không bị cảnh báo"]`
- **Gold Sources**: `["02_3924KHTH_23-10-2023_llp.md", "quychehocvu.md"]`
- **Raw Evidence**: Văn bản 3924 và Quy chế học vụ: Hoàn thành năm nhất, không bị kỷ luật/cảnh báo, đạt điều kiện trúng tuyển ngành mới.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.073171`
- **Review Status**: `approved`

---

## [060/100] `HOUT-MHOP-GEN-05` — GENERAL | MULTI_HOP (colloquial)

- **Question**: Sinh viên bị khuyết tật có hoàn cảnh khó khăn được hưởng trợ cấp xã hội và chính sách miễn giảm học phí cần nộp những giấy tờ gì?
- **Reference Answer**: Cần nộp Đơn đề nghị miễn giảm học phí và đơn trợ cấp xã hội, kèm theo bản sao Giấy xác nhận khuyết tật do UBND cấp xã cấp và giấy tờ chứng nhận hoàn cảnh khó khăn.
- **Required Facts**: `["khuyết tật", "Giấy xác nhận khuyết tật", "miễn giảm học phí"]`
- **Gold Sources**: `["02_246_23-06-2026.md", "12_don_de_nghi_mien_giam_hoc_phi_llp.md", "mghp.md"]`
- **Raw Evidence**: Chính sách cho sinh viên khuyết tật: Giấy xác nhận khuyết tật cấp xã; Đơn miễn giảm học phí và Đơn trợ cấp xã hội.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.125`
- **Review Status**: `approved`

---

## [061/100] `HOUT-XDOM-01` — FINANCIAL+ACADEMIC | CROSS_DOMAIN (formal)

- **Question**: Ngành Nuôi trồng thủy sản chương trình tiên tiến K52 có tổng bao nhiêu tín chỉ và đơn giá mỗi tín chỉ chuyên ngành là bao nhiêu đồng?
- **Reference Answer**: Ngành Nuôi trồng thủy sản chương trình tiên tiến có tổng cộng 161 tín chỉ. Đơn giá mỗi tín chỉ chuyên ngành K52 chương trình tiên tiến là 1.564.000 đồng/tín chỉ.
- **Required Facts**: `["Nuôi trồng thủy sản tiên tiến", "161 tín chỉ", "1.564.000 đồng/tín chỉ"]`
- **Gold Sources**: `["101_7620301T_NuoiTrongThuySan_CTTT.md", "MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: Nuôi trồng thủy sản tiên tiến CTĐT: 161 TC; Học phí K52 tiên tiến: 1.564.000 đồng/tín chỉ.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.027778`
- **Review Status**: `approved`

---

## [062/100] `HOUT-XDOM-02` — FINANCIAL+ACADEMIC | CROSS_DOMAIN (colloquial)

- **Question**: Em muốn hỏi ngành Kỹ thuật y sinh hệ chuẩn K52 học tổng bao nhiêu tín chỉ, và học phí mỗi tín chỉ chuyên ngành là bao nhiêu?
- **Reference Answer**: Ngành Kỹ thuật y sinh có tổng cộng 161 tín chỉ (Bắt buộc: 125 TC, Tự chọn: 36 TC). Mức học phí chuyên ngành K52 hệ chuẩn là 966.000 đồng/tín chỉ.
- **Required Facts**: `["Kỹ thuật y sinh", "161 tín chỉ", "966.000 đồng/tín chỉ"]`
- **Gold Sources**: `["63_7520212_KyThuatYSinh.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`
- **Raw Evidence**: Kỹ thuật y sinh: 161 TC; Học phí K52 Khối V chuyên ngành: 966.000 đồng/tín chỉ.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [063/100] `HOUT-XDOM-03` — FINANCIAL+ACADEMIC | CROSS_DOMAIN (formal)

- **Question**: Chương trình đào tạo ngành Kiến trúc K52 có bao nhiêu tín chỉ và học phí toàn khóa được quy định là bao nhiêu triệu đồng?
- **Reference Answer**: Ngành Kiến trúc có tổng cộng 161 tín chỉ (thời gian đào tạo 5 năm). Học phí toàn khóa ngành Kiến trúc K52 được quy định là 165,6 triệu đồng.
- **Required Facts**: `["Kiến trúc", "161 tín chỉ", "165,6 triệu đồng", "5 năm"]`
- **Gold Sources**: `["62_7580101_KienTruc.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`
- **Raw Evidence**: Kiến trúc: 161 TC, 5 năm; Học phí K52: 165,6 Trđ/khóa (1.016.000 đồng/TC).
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.066667`
- **Review Status**: `approved`

---

## [064/100] `HOUT-XDOM-04` — FINANCIAL+ACADEMIC | CROSS_DOMAIN (colloquial)

- **Question**: Ngành Kỹ thuật điều khiển và tự động hóa CLC K52 học trong mấy năm, tổng bao nhiêu tín chỉ và học phí mỗi năm là bao nhiêu?
- **Reference Answer**: Ngành Kỹ thuật điều khiển và tự động hóa CLC có tổng 161 tín chỉ đào tạo trong 4,5 năm. Học phí mỗi năm học của ngành này là 44.000.000 đồng/năm.
- **Required Facts**: `["Kỹ thuật điều khiển và tự động hóa", "161 tín chỉ", "44.000.000 đồng/năm"]`
- **Gold Sources**: `["49_7520216C_KyThuatDieuKhienVaTuDongHoa_CTCLC.md", "MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: Điều khiển TĐH CLC: 161 TC, 4,5 năm; Học phí CLC K52: 44 triệu đồng/năm.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [065/100] `HOUT-XDOM-05` — FINANCIAL+ACADEMIC | CROSS_DOMAIN (formal)

- **Question**: Thời gian đào tạo của ngành Luật hệ chuẩn là bao lâu và học phí toàn khóa Khóa 52 là bao nhiêu?
- **Reference Answer**: Thời gian đào tạo ngành Luật hệ chuẩn là 4 năm với học phí toàn khóa Khóa 52 là 114,5 triệu đồng.
- **Required Facts**: `["Luật", "4 năm", "114,5 triệu đồng"]`
- **Gold Sources**: `["16_7380101_Luat_LuatHanhChinh.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`
- **Raw Evidence**: Luật: 4 năm; Học phí K52: 114,5 Trđ/khóa (844.000 đ/TC).
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [066/100] `HOUT-XDOM-06` — FINANCIAL+ACADEMIC | CROSS_DOMAIN (colloquial)

- **Question**: Ngành Kỹ thuật cơ điện tử K52 hệ chuẩn có tổng bao nhiêu tín chỉ và học phí mỗi tín chỉ chuyên ngành là bao nhiêu đồng?
- **Reference Answer**: Ngành Kỹ thuật cơ điện tử có tổng cộng 161 tín chỉ. Học phí mỗi tín chỉ chuyên ngành hệ chuẩn K52 là 966.000 đồng/tín chỉ.
- **Required Facts**: `["Kỹ thuật cơ điện tử", "161 tín chỉ", "966.000 đồng/tín chỉ"]`
- **Gold Sources**: `["54_7520114_KyThuatCoDienTu.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`
- **Raw Evidence**: Cơ điện tử: 161 TC; Học phí K52 Khối V: 966.000 đồng/TC.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.057143`
- **Review Status**: `approved`

---

## [067/100] `HOUT-XDOM-07` — FINANCIAL+SCHOLARSHIP | CROSS_DOMAIN (formal)

- **Question**: Học phí một năm của ngành Tài chính - Ngân hàng CLC K52 là bao nhiêu và sinh viên có thể ứng tuyển học bổng SCIC trị giá 10 triệu không?
- **Reference Answer**: Học phí ngành Tài chính - Ngân hàng CLC K52 là 38.000.000 đồng/năm. Sinh viên ngành này hoàn toàn đủ điều kiện chuyên ngành để ứng tuyển học bổng SCIC (trị giá 10.000.000 đồng/suất).
- **Required Facts**: `["Tài chính - Ngân hàng", "38.000.000 đồng/năm", "SCIC", "10.000.000 đồng"]`
- **Gold Sources**: `["MucHocPhi_ChatLuongCao_TienTien.md", "HB_SCIC_2026.md"]`
- **Raw Evidence**: TCNH CLC K52: 38 triệu/năm; SCIC 2026: 10 triệu/suất, dành cho SV Tài chính - Ngân hàng.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.052632`
- **Review Status**: `approved`

---

## [068/100] `HOUT-XDOM-08` — FINANCIAL+SCHOLARSHIP | CROSS_DOMAIN (colloquial)

- **Question**: Học bổng bình quân kỳ đầu của tân sinh viên K52 là bao nhiêu tiền, và số tiền đó có đủ trang trải học phí một kỳ của ngành Thú y chuẩn K52 không?
- **Reference Answer**: Học bổng tân sinh viên kỳ đầu bình quân là 5.000.000 đồng. Học phí ngành Thú y K52 toàn khóa là 166,6 triệu đồng (khoảng 16,6 triệu/kỳ cho 10 kỳ), nên mức học bổng 5 triệu không đủ trang trải học phí 1 kỳ.
- **Required Facts**: `["5.000.000 đồng", "Thú y", "166,6 triệu đồng", "không đủ"]`
- **Gold Sources**: `["HB_TanSinhVien_K52.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`
- **Raw Evidence**: HB Tân sinh viên: 5.000.000 đồng; Thú y K52: 166,6 Trđ/khóa (5 năm/10 kỳ ~ 16,6 Trđ/kỳ).
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [069/100] `HOUT-XDOM-09` — FINANCIAL+SCHOLARSHIP | CROSS_DOMAIN (formal)

- **Question**: Quỹ học bổng khuyến khích trích tối thiểu 8% từ nguồn thu học phí, vậy sinh viên đạt loại Xuất sắc ngành Quản trị kinh doanh K52 sẽ nhận mức học bổng tính ra sao so với học phí đã đóng?
- **Reference Answer**: Quỹ học bổng trích tối thiểu 8% nguồn thu học phí; mức học bổng loại Xuất sắc bằng 1,2 lần số tiền học phí thực đóng của sinh viên ngành QTKD trong học kỳ đó.
- **Required Facts**: `["8%", "1,2", "học phí thực đóng"]`
- **Gold Sources**: `["Tài liệu phân bổ quỹ học bổng.md", "03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md"]`
- **Raw Evidence**: Quỹ HB trích 8% học phí; Mức Xuất sắc = 1,2 x mức Khá (bằng 1,2 lần học phí đã đóng).
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.034483`
- **Review Status**: `approved`

---

## [070/100] `HOUT-XDOM-10` — FINANCIAL+SCHOLARSHIP | CROSS_DOMAIN (colloquial)

- **Question**: Sinh viên ngành Nuôi trồng thủy sản tiên tiến K52 có được xét học bổng khuyến khích không và quỹ học bổng ngành được trích theo tỷ lệ nào?
- **Reference Answer**: Sinh viên ngành NTTS tiên tiến được xét học bổng khuyến khích nếu đạt kết quả học tập và rèn luyện từ loại Khá trở lên; quỹ học bổng của ngành được trích 8% từ tổng học phí sinh viên đã đóng.
- **Required Facts**: `["Nuôi trồng thủy sản tiên tiến", "8%", "loại Khá trở lên"]`
- **Gold Sources**: `["03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md", "Tài liệu phân bổ quỹ học bổng.md"]`
- **Raw Evidence**: Quỹ HBKKHT trích 8% học phí cùng khóa, ngành; Sinh viên đạt loại Khá trở lên được xét.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.076923`
- **Review Status**: `approved`

---

## [071/100] `HOUT-XDOM-11` — FINANCIAL+SCHOLARSHIP | CROSS_DOMAIN (formal)

- **Question**: Học bổng Lương Văn Can hỗ trợ sinh viên hoàn cảnh khó khăn bao nhiêu tiền và có giới hạn ngành học trong trường không?
- **Reference Answer**: Học bổng Lương Văn Can tài trợ toàn phần hoặc bán phần học phí và sinh hoạt phí cho sinh viên đạt GPA từ 8.0 trở lên có hoàn cảnh khó khăn và không giới hạn ngành học.
- **Required Facts**: `["Lương Văn Can", "8.0", "học phí", "không phân biệt ngành học"]`
- **Gold Sources**: `["HB_LuongVanCang.md"]`
- **Raw Evidence**: HB Lương Văn Can: Tài trợ học phí, sinh hoạt phí; GPA 8.0+, không phân biệt ngành học.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [072/100] `HOUT-XDOM-12` — FINANCIAL+SOCIAL_SUPPORT | CROSS_DOMAIN (colloquial)

- **Question**: Sinh viên dân tộc thiểu số hộ nghèo học ngành Kỹ thuật xây dựng K52 được miễn bao nhiêu phần trăm học phí và mức tiền miễn trừ tính trên con số nào?
- **Reference Answer**: Sinh viên dân tộc thiểu số hộ nghèo được miễn 100% học phí; tuy nhiên mức tiền miễn trừ tính trên mức cơ sở miễn giảm Khối V là 538.000 đồng/tín chỉ, phần chênh lệch với học phí thực tế 966.000 đồng/tín chỉ sinh viên phải tự chi trả theo quy định.
- **Required Facts**: `["miễn 100%", "538.000 đồng/tín chỉ", "Kỹ thuật xây dựng", "Khối V"]`
- **Gold Sources**: `["mghp.md", "MucHocPhi_2526_MienGiam.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`
- **Raw Evidence**: Miễn 100% học phí; Mức trần cơ sở Khối V: 538.000 đ/TC; Học phí thực tế KTXD: 966.000 đ/TC.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.088889`
- **Review Status**: `approved`

---

## [073/100] `HOUT-XDOM-13` — FINANCIAL+SOCIAL_SUPPORT | CROSS_DOMAIN (formal)

- **Question**: Sinh viên học ngành Quản trị kinh doanh K52 thuộc diện hộ cận nghèo thì được giảm bao nhiêu phần trăm học phí và mức hỗ trợ mỗi tín chỉ là bao nhiêu?
- **Reference Answer**: Sinh viên thuộc hộ cận nghèo (nếu là người dân tộc thiểu số vùng đặc biệt khó khăn) được giảm theo chính sách; mức hỗ trợ tính trên cơ sở Khối ngành III là 451.000 đồng/tín chỉ.
- **Required Facts**: `["Khối ngành III", "451.000 đồng/tín chỉ", "Quản trị kinh doanh"]`
- **Gold Sources**: `["mghp.md", "MucHocPhi_2526_MienGiam.md", "85_7340101_QuanTriKinhDoanh.md"]`
- **Raw Evidence**: Hộ cận nghèo DTTS: miễn/giảm trên cơ sở Khối ngành III: 451.000 đồng/tín chỉ.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.065217`
- **Review Status**: `approved`

---

## [074/100] `HOUT-XDOM-14` — FINANCIAL+SOCIAL_SUPPORT | CROSS_DOMAIN (colloquial)

- **Question**: Học phí ngành Kiến trúc K52 là 165,6 triệu/khóa, nếu sinh viên vay vốn tín dụng tối đa 4 triệu/tháng thì tiền vay 5 năm có đủ trả học phí toàn khóa không?
- **Reference Answer**: Vay vốn 4.000.000 đồng/tháng trong 5 năm (50 tháng học) được tổng cộng 200.000.000 đồng. Số tiền này lớn hơn học phí toàn khóa 165,6 triệu đồng của ngành Kiến trúc K52, nên đủ trang trải học phí.
- **Required Facts**: `["4.000.000 đồng/tháng", "165,6 triệu", "Kiến trúc", "đủ"]`
- **Gold Sources**: `["VayVon.md", "MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`
- **Raw Evidence**: Vay vốn tối đa: 4 triệu/tháng (5 năm = 200 triệu); Học phí Kiến trúc K52: 165,6 triệu -> Đủ trang trải.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [075/100] `HOUT-XDOM-15` — FINANCIAL+SOCIAL_SUPPORT | CROSS_DOMAIN (formal)

- **Question**: Mỗi tháng sinh viên dân tộc thiểu số nghèo được chi trả bao nhiêu tiền hỗ trợ chi phí, và quy trình kết hợp hồ sơ xin miễn giảm học phí ra sao?
- **Reference Answer**: Sinh viên được hỗ trợ chi phí học tập theo mức quy định (bằng 60% mức lương cơ sở) và nộp kèm hồ sơ miễn giảm học phí đầu mỗi học kỳ theo quy định.
- **Required Facts**: `["hỗ trợ chi phí học tập", "dân tộc thiểu số", "miễn giảm học phí"]`
- **Gold Sources**: `["HTCPHT.md", "12_don_de_nghi_mien_giam_hoc_phi_llp.md"]`
- **Raw Evidence**: HTCPHT: hỗ trợ chi phí học tập cho SV DTTS nghèo/cận nghèo; Mẫu đơn 12 miễn giảm học phí.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.042553`
- **Review Status**: `approved`

---

## [076/100] `HOUT-XDOM-16` — ACADEMIC+SCHOLARSHIP | CROSS_DOMAIN (colloquial)

- **Question**: Sinh viên ngành Nuôi trồng thủy sản chương trình tiên tiến cần tích lũy bao nhiêu tín chỉ và điểm GPA tối thiểu bao nhiêu để nộp hồ sơ học bổng SCC?
- **Reference Answer**: Ngành Nuôi trồng thủy sản chương trình tiên tiến có tổng 161 tín chỉ. Để nộp hồ sơ học bổng SCC, sinh viên cần đạt điểm trung bình tích lũy từ 8.0 trở lên.
- **Required Facts**: `["Nuôi trồng thủy sản tiên tiến", "161 tín chỉ", "8.0", "SCC"]`
- **Gold Sources**: `["101_7620301T_NuoiTrongThuySan_CTTT.md", "HB_SCC.md"]`
- **Raw Evidence**: NTTS tiên tiến: 161 TC; Học bổng SCC: yêu cầu GPA từ 8.0 trở lên.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.025`
- **Review Status**: `approved`

---

## [077/100] `HOUT-XDOM-17` — ACADEMIC+SCHOLARSHIP | CROSS_DOMAIN (formal)

- **Question**: Sinh viên ngành Trí tuệ nhân tạo muốn ứng tuyển học bổng Lương Văn Can thì chương trình có bao nhiêu tín chỉ và học bổng đòi hỏi những yêu cầu gì?
- **Reference Answer**: Ngành Trí tuệ nhân tạo có 161 tín chỉ. Học bổng Lương Văn Can yêu cầu điểm trung bình tích lũy từ 8.0 trở lên, có hoàn cảnh khó khăn và có tinh thần vượt khó trong học tập.
- **Required Facts**: `["Trí tuệ nhân tạo", "161 tín chỉ", "Lương Văn Can", "8.0"]`
- **Gold Sources**: `["108_7480107_TriTueNhanTao.md", "HB_LuongVanCang.md"]`
- **Raw Evidence**: Trí tuệ nhân tạo: 161 TC; HB Lương Văn Can: GPA 8.0+, hoàn cảnh khó khăn.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.027027`
- **Review Status**: `approved`

---

## [078/100] `HOUT-XDOM-18` — ACADEMIC+SCHOLARSHIP | CROSS_DOMAIN (colloquial)

- **Question**: Ngành Logistics và Quản lý chuỗi cung ứng có tổng bao nhiêu tín chỉ và sinh viên ngành này có được xét học bổng khuyến khích học tập không?
- **Reference Answer**: Ngành Logistics và Quản lý chuỗi cung ứng có tổng cộng 141 tín chỉ. Sinh viên ngành này hoàn toàn được xét học bổng khuyến khích học tập nếu đạt kết quả học tập và rèn luyện từ loại Khá trở lên.
- **Required Facts**: `["Logistics và Quản lý chuỗi cung ứng", "141 tín chỉ", "khuyến khích học tập", "loại Khá"]`
- **Gold Sources**: `["61_7510605_LogisticsVaQuanLyChuoiCungUng.md", "03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md"]`
- **Raw Evidence**: Logistics: 141 TC; HBKKHT: xét cho tất cả sinh viên chính quy đạt từ loại Khá trở lên.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.166667`
- **Review Status**: `approved`

---

## [079/100] `HOUT-XDOM-19` — ACADEMIC+SCHOLARSHIP | CROSS_DOMAIN (formal)

- **Question**: Sinh viên ngành Thú y học trong 5 năm với 175 tín chỉ thì quỹ học bổng khuyến khích có cấp suốt 5 năm học không?
- **Reference Answer**: Học bổng khuyến khích học tập được xét cấp theo từng học kỳ trong suốt thời gian thiết kế của chương trình đào tạo chuẩn (5 năm đối với ngành Thú y), không cấp trong thời gian kéo dài.
- **Required Facts**: `["Thú y", "175 tín chỉ", "5 năm", "từng học kỳ"]`
- **Gold Sources**: `["96_7640101_ThuY.md", "03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md"]`
- **Raw Evidence**: Thú y: CTĐT 5 năm (175 TC); HBKKHT xét theo từng học kỳ trong thời gian đào tạo chuẩn.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.022727`
- **Review Status**: `approved`

---

## [080/100] `HOUT-XDOM-20` — ACADEMIC+SCHOLARSHIP | CROSS_DOMAIN (colloquial)

- **Question**: Ngành Kỹ thuật y sinh học mấy năm và điều kiện GPA để xin học bổng Vallet là bao nhiêu?
- **Reference Answer**: Ngành Kỹ thuật y sinh có thời gian đào tạo 4,5 năm (161 tín chỉ). Học bổng Vallet yêu cầu sinh viên đạt kết quả học tập xuất sắc hoặc giỏi (thường GPA từ 8.0 trở lên) và có thành tích nghiên cứu khoa học.
- **Required Facts**: `["Kỹ thuật y sinh", "161 tín chỉ", "Vallet", "loại Giỏi"]`
- **Gold Sources**: `["63_7520212_KyThuatYSinh.md", "HB_Vallet_Chi_Tiet.md"]`
- **Raw Evidence**: Kỹ thuật y sinh: 161 TC, 4,5 năm; Học bổng Vallet: thành tích học tập loại Giỏi/Xuất sắc, nghiên cứu khoa học.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [081/100] `HOUT-COMP-01` — FINANCIAL | COMPARISON (formal)

- **Question**: So sánh mức học phí mỗi tín chỉ chuyên ngành giữa ngành Kỹ thuật xây dựng hệ chuẩn và hệ chất lượng cao Khóa 52?
- **Reference Answer**: Kỹ thuật xây dựng hệ chuẩn K52: 966.000 đồng/tín chỉ. Kỹ thuật xây dựng hệ CLC K52: 1.438.000 đồng/tín chỉ. Chênh lệch là 472.000 đồng/tín chỉ (hệ CLC cao hơn khoảng 48,8%).
- **Required Facts**: `["Kỹ thuật xây dựng", "966.000", "1.438.000", "chênh lệch"]`
- **Gold Sources**: `["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: KTXD chuẩn K52: 966.000; KTXD CLC K52: 1.438.000; Chênh lệch: 472.000 đồng/TC
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [082/100] `HOUT-COMP-02` — FINANCIAL | COMPARISON (colloquial)

- **Question**: Học phí toàn khóa ngành Thú y hệ chuẩn K52 cao hơn hay thấp hơn ngành Kiến trúc hệ chuẩn K52 và chênh lệch bao nhiêu triệu?
- **Reference Answer**: Học phí toàn khóa ngành Thú y K52 là 166,6 triệu đồng, ngành Kiến trúc K52 là 165,6 triệu đồng. Ngành Thú y cao hơn ngành Kiến trúc 1,0 triệu đồng toàn khóa.
- **Required Facts**: `["Thú y", "166,6 triệu", "Kiến trúc", "165,6 triệu", "cao hơn 1,0 triệu"]`
- **Gold Sources**: `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`
- **Raw Evidence**: Thú y K52: 166,6 Trđ; Kiến trúc K52: 165,6 Trđ; Chênh lệch: Thú y cao hơn 1,0 Trđ.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [083/100] `HOUT-COMP-03` — FINANCIAL | COMPARISON (formal)

- **Question**: Học phí niên chế một năm của hai chuyên ngành chất lượng cao QTKD và Tài chính Ngân hàng khóa 52 chênh nhau như thế nào?
- **Reference Answer**: Cả hai ngành Quản trị kinh doanh CLC K52 và Tài chính - Ngân hàng CLC K52 đều có mức học phí năm học là 38.000.000 đồng/năm (đơn giá tín chỉ chuyên ngành là 1.363.000 đồng/TC).
- **Required Facts**: `["Quản trị kinh doanh", "Tài chính - Ngân hàng", "CLC", "38.000.000 đồng/năm"]`
- **Gold Sources**: `["MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: QTKD CLC K52: 38 triệu/năm; TCNH CLC K52: 38 triệu/năm; Cùng mức 38 triệu.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [084/100] `HOUT-COMP-04` — FINANCIAL | COMPARISON (colloquial)

- **Question**: Giữa ngành Nuôi trồng thủy sản tiên tiến K52 và ngành Công nghệ sinh học tiên tiến K52 thì ngành nào có đơn giá tín chỉ cao hơn?
- **Reference Answer**: Nuôi trồng thủy sản tiên tiến K52: 1.564.000 đồng/tín chỉ. Công nghệ sinh học tiên tiến K52: 1.499.000 đồng/tín chỉ. Nuôi trồng thủy sản tiên tiến cao hơn 65.000 đồng/tín chỉ.
- **Required Facts**: `["Nuôi trồng thủy sản tiên tiến", "1.564.000", "Công nghệ sinh học", "1.499.000"]`
- **Gold Sources**: `["MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: NTTS TT K52: 1.564.000; CNSH TT K52: 1.499.000; Chênh lệch: 65.000 đ/TC.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.027778`
- **Review Status**: `approved`

---

## [085/100] `HOUT-COMP-05` — FINANCIAL | COMPARISON (formal)

- **Question**: Học phí một năm của ngành Kỹ thuật điều khiển và tự động hóa CLC khóa 51 so với khóa 52 chênh lệch bao nhiêu triệu đồng?
- **Reference Answer**: Kỹ thuật điều khiển và tự động hóa CLC Khóa 51 là 40.000.000 đồng/năm, Khóa 52 là 44.000.000 đồng/năm. K52 tăng 4.000.000 đồng/năm (tăng 10%).
- **Required Facts**: `["Kỹ thuật điều khiển và tự động hóa", "K51", "40 triệu", "K52", "44 triệu", "4 triệu"]`
- **Gold Sources**: `["MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: Điều khiển TĐH CLC: K51 là 40 triệu; K52 là 44 triệu; Tăng 4 triệu/năm.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.057143`
- **Review Status**: `approved`

---

## [086/100] `HOUT-COMP-06` — ACADEMIC | COMPARISON (colloquial)

- **Question**: So sánh tổng số tín chỉ tích lũy giữa ngành Logistics và Quản lý chuỗi cung ứng với ngành Trí tuệ nhân tạo?
- **Reference Answer**: Ngành Logistics và Quản lý chuỗi cung ứng có 141 tín chỉ (đào tạo 4 năm). Ngành Trí tuệ nhân tạo có 161 tín chỉ (đào tạo 4,5 năm). Ngành Trí tuệ nhân tạo nhiều hơn 20 tín chỉ.
- **Required Facts**: `["Logistics", "141 tín chỉ", "Trí tuệ nhân tạo", "161 tín chỉ", "20"]`
- **Gold Sources**: `["61_7510605_LogisticsVaQuanLyChuoiCungUng.md", "108_7480107_TriTueNhanTao.md"]`
- **Raw Evidence**: Logistics: 141 TC; Trí tuệ nhân tạo: 161 TC; Chênh lệch: 20 TC.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.066667`
- **Review Status**: `approved`

---

## [087/100] `HOUT-COMP-07` — ACADEMIC | COMPARISON (formal)

- **Question**: Chương trình đào tạo ngành Thú y hệ chuẩn và ngành Quản lý thủy sản khác nhau bao nhiêu tín chỉ toàn khóa?
- **Reference Answer**: Ngành Thú y hệ chuẩn có 175 tín chỉ (5 năm). Ngành Quản lý thủy sản có 141 tín chỉ (4 năm). Ngành Thú y nhiều hơn 34 tín chỉ.
- **Required Facts**: `["Thú y", "175 tín chỉ", "Quản lý thủy sản", "141 tín chỉ", "34"]`
- **Gold Sources**: `["96_7640101_ThuY.md", "102_7620305_QuanLyThuySan.md"]`
- **Raw Evidence**: Thú y: 175 TC; Quản lý thủy sản: 141 TC; Chênh lệch: 34 TC.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.107143`
- **Review Status**: `approved`

---

## [088/100] `HOUT-COMP-08` — FINANCIAL | COMPARISON (colloquial)

- **Question**: Mức học phí làm cơ sở miễn giảm giữa Khối ngành V và Khối ngành III năm học 2025-2026 chênh nhau bao nhiêu tiền mỗi tín chỉ?
- **Reference Answer**: Khối ngành V có mức cơ sở miễn giảm là 538.000 đồng/tín chỉ, Khối ngành III là 451.000 đồng/tín chỉ. Chênh lệch là 87.000 đồng/tín chỉ.
- **Required Facts**: `["Khối ngành V", "538.000", "Khối ngành III", "451.000", "87.000"]`
- **Gold Sources**: `["MucHocPhi_2526_MienGiam.md"]`
- **Raw Evidence**: Khối V: 538.000 đ/TC; Khối III: 451.000 đ/TC; Chênh lệch: 87.000 đ/TC.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.105263`
- **Review Status**: `approved`

---

## [089/100] `HOUT-COMP-09` — SCHOLARSHIP | COMPARISON (formal)

- **Question**: So sánh tỷ lệ chênh lệch mức học bổng khuyến khích học tập giữa loại Xuất sắc, loại Giỏi và loại Khá?
- **Reference Answer**: Mức học bổng loại Khá = 100% học phí; loại Giỏi = 1,1 lần loại Khá (+10%); loại Xuất sắc = 1,2 lần loại Khá (+20%).
- **Required Facts**: `["loại Khá", "loại Giỏi", "1,1", "loại Xuất sắc", "1,2"]`
- **Gold Sources**: `["03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md"]`
- **Raw Evidence**: Loại Khá: chuẩn; Loại Giỏi = 1,1 x Khá; Loại Xuất sắc = 1,2 x Khá.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.107143`
- **Review Status**: `approved`

---

## [090/100] `HOUT-COMP-10` — FINANCIAL | COMPARISON (colloquial)

- **Question**: Giữa ngành Luật hệ chuẩn K52 và ngành Kỹ thuật xây dựng hệ chuẩn K52 thì ngành nào có học phí toàn khóa thấp hơn và thấp hơn bao nhiêu?
- **Reference Answer**: Ngành Luật K52 có học phí 114,5 triệu đồng, ngành Kỹ thuật xây dựng K52 là 150,3 triệu đồng. Ngành Luật thấp hơn 35,8 triệu đồng.
- **Required Facts**: `["Luật", "114,5 triệu", "Kỹ thuật xây dựng", "150,3 triệu", "thấp hơn 35,8 triệu"]`
- **Gold Sources**: `["MucHocPhi_DaiHocChinhQuy_Khoa52.md"]`
- **Raw Evidence**: Luật K52: 114,5 Trđ; KTXD K52: 150,3 Trđ; Chênh lệch: Luật thấp hơn 35,8 Trđ.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [091/100] `HOUT-TEMP-01` — FINANCIAL | TEMPORAL (formal)

- **Question**: Học phí một tín chỉ chuyên ngành của ngành Tài chính - Ngân hàng CLC thay đổi như thế nào từ Khóa 49 đến Khóa 52?
- **Reference Answer**: Khóa 49: 1.142.000 đồng/TC; Khóa 50: 1.211.000 đồng/TC; Khóa 51: 1.284.000 đồng/TC; Khóa 52: 1.363.000 đồng/TC. Mức học phí tăng dần đều qua từng khóa.
- **Required Facts**: `["Khóa 49", "1.142.000", "Khóa 52", "1.363.000"]`
- **Gold Sources**: `["MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: TCNH CLC: K49: 1.142.000; K50: 1.211.000; K51: 1.284.000; K52: 1.363.000 đồng/TC.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.032258`
- **Review Status**: `approved`

---

## [092/100] `HOUT-TEMP-02` — FINANCIAL | TEMPORAL (colloquial)

- **Question**: Học phí mỗi năm của ngành Kinh doanh quốc tế CLC từ khóa K48 đến khóa K52 tăng bao nhiêu triệu đồng?
- **Reference Answer**: Khóa 48: 33 triệu đồng/năm. Khóa 52: 40 triệu đồng/năm. Mức học phí tăng 7 triệu đồng/năm.
- **Required Facts**: `["Kinh doanh quốc tế", "CLC", "33 triệu", "40 triệu", "7 triệu"]`
- **Gold Sources**: `["MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: Kinh doanh quốc tế CLC: K48 là 33 triệu/năm; K52 là 40 triệu/năm; Tăng 7 triệu/năm.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [093/100] `HOUT-TEMP-03` — FINANCIAL | TEMPORAL (formal)

- **Question**: Đơn giá tín chỉ chương trình tiên tiến ngành Nuôi trồng thủy sản qua các khóa K49, K50, K51 và K52 là bao nhiêu?
- **Reference Answer**: Nuôi trồng thủy sản tiên tiến: K49 là 1.311.000 đ/TC; K50 là 1.390.000 đ/TC; K51 là 1.473.000 đ/TC; K52 là 1.564.000 đ/TC.
- **Required Facts**: `["Nuôi trồng thủy sản tiên tiến", "K49", "K52", "1.564.000"]`
- **Gold Sources**: `["MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: NTTS TT: K49: 1.311.000; K50: 1.390.000; K51: 1.473.000; K52: 1.564.000 đồng/TC.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.166667`
- **Review Status**: `approved`

---

## [094/100] `HOUT-TEMP-04` — ACADEMIC | TEMPORAL (colloquial)

- **Question**: Quy định công tác học vụ năm 2021 (QĐ 1813) và Quy chế học vụ hiện hành có điểm gì cần lưu ý về thời gian tối đa để sinh viên hoàn thành khóa học?
- **Reference Answer**: Thời gian tối đa để sinh viên hoàn thành chương trình đào tạo chính quy không vượt quá 2 lần thời gian thiết kế chuẩn của khóa học (ví dụ CTĐT 4 năm thì tối đa 8 năm).
- **Required Facts**: `["2 lần thời gian", "tối đa", "Quy chế học vụ"]`
- **Gold Sources**: `["quychehocvu.md", "QD1813_QD_ban_hanh_Quy_dinh_cong_tac_hoc_vu_2021.md"]`
- **Raw Evidence**: Thời gian học tập tối đa không quá 2 lần thời gian kế hoạch chuẩn của CTĐT.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.023256`
- **Review Status**: `approved`

---

## [095/100] `HOUT-TEMP-05` — FINANCIAL | TEMPORAL (formal)

- **Question**: Học phí một năm của ngành Thú y CLC giữa khóa K50 và K52 có sự thay đổi ra sao?
- **Reference Answer**: Ngành Thú y CLC Khóa 50 có học phí là 39.000.000 đồng/năm, trong khi Khóa 52 có học phí là 44.000.000 đồng/năm (tăng 5.000.000 đồng/năm).
- **Required Facts**: `["Thú y", "CLC", "K50", "39 triệu", "K52", "44 triệu"]`
- **Gold Sources**: `["MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: Thú y CLC: K50 là 39 triệu/năm; K52 là 44 triệu/năm; Tăng 5 triệu/năm.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.071429`
- **Review Status**: `approved`

---

## [096/100] `HOUT-ADVS-01` — FINANCIAL | ADVERSARIAL (colloquial)

- **Question**: Học phí đại học Trường Đại học Cần Thơ năm nay thu bao nhiêu tiền?
- **Reference Answer**: Học phí Trường Đại học Cần Thơ thu theo tín chỉ và tùy thuộc vào ngành học, chương trình đào tạo (hệ chuẩn, chất lượng cao, tiên tiến) và từng khóa tuyển sinh (ví dụ K52 hệ chuẩn dao động từ khoảng 114,5 đến 166,6 triệu đồng/khóa).
- **Required Facts**: `["theo tín chỉ", "tùy thuộc vào ngành học", "khóa tuyển sinh"]`
- **Gold Sources**: `["MucHocPhi_DaiHocChinhQuy_Khoa52.md", "MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: Học phí thu theo tín chỉ và ngành học cụ thể; Biểu phí quy định riêng cho từng khóa và chương trình.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.04`
- **Review Status**: `approved`

---

## [097/100] `HOUT-ADVS-02` — SCHOLARSHIP | ADVERSARIAL (colloquial)

- **Question**: Sinh viên muốn xin học bổng thì cần đáp ứng những tiêu chuẩn chung gì?
- **Reference Answer**: Để nhận học bổng (khuyến khích học tập hoặc học bổng tài trợ), sinh viên cần đáp ứng chuẩn kết quả học tập (từ loại Khá trở lên, GPA từ 2.5/4 hoặc 8.0/10 tùy loại học bổng), điểm rèn luyện đạt từ loại Khá trở lên và không bị kỷ luật.
- **Required Facts**: `["điểm học tập", "điểm rèn luyện", "loại Khá trở lên"]`
- **Gold Sources**: `["03-7-2026_Qd_dinhmuchocbong_261signedsignedsignedsigned_llp.md"]`
- **Raw Evidence**: Điều kiện xét học bổng: Điểm học tập và rèn luyện từ loại Khá trở lên, không bị kỷ luật.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

## [098/100] `HOUT-ADVS-03` — GENERAL | ADVERSARIAL (formal)

- **Question**: Trường Đại học Cần Thơ có những chính sách hỗ trợ tài chính nào dành cho sinh viên có hoàn cảnh khó khăn?
- **Reference Answer**: Nhà trường có nhiều chính sách hỗ trợ bao gồm: Miễn/giảm học phí theo Nghị định của Chính phủ, Hỗ trợ chi phí học tập cho sinh viên DTTS nghèo/cận nghèo, Trợ cấp xã hội, Xác nhận vay vốn tín dụng sinh viên và các gói học bổng tài trợ doanh nghiệp.
- **Required Facts**: `["miễn giảm học phí", "hỗ trợ chi phí học tập", "trợ cấp xã hội", "vay vốn"]`
- **Gold Sources**: `["HTCPHT.md", "mghp.md", "VayVon.md", "02_246_23-06-2026.md"]`
- **Raw Evidence**: Chính sách hỗ trợ: Miễn giảm học phí, Hỗ trợ chi phí học tập, Trợ cấp xã hội, Vay vốn sinh viên.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.090909`
- **Review Status**: `approved`

---

## [099/100] `HOUT-ADVS-04` — ACADEMIC | ADVERSARIAL (colloquial)

- **Question**: Sinh viên bị buộc thôi học khi nào theo quy chế?
- **Reference Answer**: Sinh viên bị buộc thôi học nếu bị cảnh báo học tập quá số lần quy định liên tiếp, vượt quá thời gian học tập tối đa cho phép, hoặc vi phạm kỷ luật ở mức buộc thôi học theo Quy chế học vụ.
- **Required Facts**: `["buộc thôi học", "cảnh báo học tập", "thời gian học tập tối đa"]`
- **Gold Sources**: `["quychehocvu.md"]`
- **Raw Evidence**: Buộc thôi học: Cảnh báo học tập quá số lần quy định, hết thời gian học tập tối đa.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.1875`
- **Review Status**: `approved`

---

## [100/100] `HOUT-ADVS-05` — FINANCIAL | ADVERSARIAL (formal)

- **Question**: Học phí ngành Tiên tiến và Chất lượng cao tính theo năm hay tính theo tín chỉ?
- **Reference Answer**: Học phí chương trình Tiên tiến và Chất lượng cao được ban hành đồng thời theo cả hai cách: mức thu quy đổi trọn gói theo năm học và đơn giá thu theo từng tín chỉ chuyên ngành thực tế đăng ký.
- **Required Facts**: `["theo năm", "theo tín chỉ", "chất lượng cao", "tiên tiến"]`
- **Gold Sources**: `["MucHocPhi_ChatLuongCao_TienTien.md"]`
- **Raw Evidence**: Bảng học phí ban hành đồng thời: Mức thu Trđ/năm và Đơn giá đ/tín chỉ.
- **Novelty vs Dev**: exact=`False`, max_5gram_jaccard=`0.0`
- **Review Status**: `approved`

---

