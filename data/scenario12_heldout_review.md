# Scenario 1–2 held-out review

> Bộ này là **author-reviewed held-out set**, không phải independent annotation.
> Kiểm tra từng case rồi đổi `[ ] Approved` thành `[x] Approved`. Sau đó chạy
> `wsl_venv/bin/python scripts/prepare_scenario12_datasets.py --apply-review`.

## Quota

- `actual_tuition`: 20
- `academic_rules`: 6
- `scholarship`: 5
- `student_loan`: 4
- `social_support`: 4
- `other`: 4
- `academic_program`: 3
- `exemption_policy`: 2
- `exemption_basis`: 2

## HOUT-TUI-01 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu toàn khóa của ngành Thú y, chương trình chuẩn, khóa 52 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Thú y, chương trình chuẩn, khóa 52, năm học 2026-2027 là 166.600.000 đồng toàn khóa.

**Required facts:** `["Thú y", "52", "166600000", "2026-2027"]`

**Gold source:** `MucHocPhi_DaiHocChinhQuy_Khoa52.md`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Thú y, chương trình chuẩn, khóa 52, năm học 2026-2027 là 166.600.000 đồng toàn khóa.

**Novelty:** exact=`False`, 5-gram=`0.026316`, embedding=`0.564333`

## HOUT-TUI-02 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu toàn khóa của ngành Kỹ thuật y sinh, chương trình chuẩn, khóa 52 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Kỹ thuật y sinh, chương trình chuẩn, khóa 52, năm học 2026-2027 là 150.300.000 đồng toàn khóa.

**Required facts:** `["Kỹ thuật y sinh", "52", "150300000", "2026-2027"]`

**Gold source:** `MucHocPhi_DaiHocChinhQuy_Khoa52.md`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Kỹ thuật y sinh, chương trình chuẩn, khóa 52, năm học 2026-2027 là 150.300.000 đồng toàn khóa.

**Novelty:** exact=`False`, 5-gram=`0.025`, embedding=`0.478358`

## HOUT-TUI-03 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu toàn khóa của ngành Kỹ thuật xây dựng công trình thủy, chương trình chuẩn, khóa 52 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Kỹ thuật xây dựng công trình thủy, chương trình chuẩn, khóa 52, năm học 2026-2027 là 150.300.000 đồng toàn khóa.

**Required facts:** `["Kỹ thuật xây dựng công trình thủy", "52", "150300000", "2026-2027"]`

**Gold source:** `MucHocPhi_DaiHocChinhQuy_Khoa52.md`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Kỹ thuật xây dựng công trình thủy, chương trình chuẩn, khóa 52, năm học 2026-2027 là 150.300.000 đồng toàn khóa.

**Novelty:** exact=`False`, 5-gram=`0.023256`, embedding=`0.443253`

## HOUT-TUI-04 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi năm học của ngành Công nghệ sinh học, chương trình tiên tiến, khóa 52 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Công nghệ sinh học, chương trình tiên tiến, khóa 52, năm học 2026-2027 là 44.000.000 đồng mỗi năm học.

**Required facts:** `["Công nghệ sinh học", "52", "44000000", "2026-2027"]`

**Gold source:** `MucHocPhi_ChatLuongCao_TienTien.md`

**Evidence excerpt:** I. Học phí cố định theo khóa học (triệu đồng/năm học) | Chương trình Tiên tiến | Mức thu của ngành Công nghệ sinh học, chương trình tiên tiến, khóa 52, năm học 2026-2027 là 44.000.000 đồng mỗi năm học.

**Novelty:** exact=`False`, 5-gram=`0.025`, embedding=`0.497318`

## HOUT-TUI-05 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi tín chỉ của ngành Nuôi trồng thủy sản, chương trình tiên tiến, khóa 49 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Nuôi trồng thủy sản, chương trình tiên tiến, khóa 49, năm học 2026-2027 là 1.309.000 đồng mỗi tín chỉ.

**Required facts:** `["Nuôi trồng thủy sản", "49", "1309000", "2026-2027"]`

**Gold source:** `MucHocPhi_ChatLuongCao_TienTien.md`

**Evidence excerpt:** II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ) | Chương trình Tiên tiến (đồng/tín chỉ) | Mức thu của ngành Nuôi trồng thủy sản, chương trình tiên tiến, khóa 49, năm học 2026-2027 là 1.309.000 đồng mỗi tín chỉ.

**Novelty:** exact=`False`, 5-gram=`0.025`, embedding=`0.588779`

## HOUT-TUI-06 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi tín chỉ của ngành Quản lý xây dựng, chương trình chuẩn, khóa 52 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Quản lý xây dựng, chương trình chuẩn, khóa 52, năm học 2026-2027 là 966.000 đồng mỗi tín chỉ.

**Required facts:** `["Quản lý xây dựng", "52", "966000", "2026-2027"]`

**Gold source:** `MucHocPhi_DaiHocChinhQuy_Khoa52.md`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Quản lý xây dựng, chương trình chuẩn, khóa 52, năm học 2026-2027 là 966.000 đồng mỗi tín chỉ.

**Novelty:** exact=`False`, 5-gram=`0.02439`, embedding=`0.664836`

## HOUT-TUI-07 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi tín chỉ của ngành Kỹ thuật điều khiển và tự động hóa, chương trình chuẩn, khóa 52 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Kỹ thuật điều khiển và tự động hóa, chương trình chuẩn, khóa 52, năm học 2026-2027 là 966.000 đồng mỗi tín chỉ.

**Required facts:** `["Kỹ thuật điều khiển và tự động hóa", "52", "966000", "2026-2027"]`

**Gold source:** `MucHocPhi_DaiHocChinhQuy_Khoa52.md`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Kỹ thuật điều khiển và tự động hóa, chương trình chuẩn, khóa 52, năm học 2026-2027 là 966.000 đồng mỗi tín chỉ.

**Novelty:** exact=`False`, 5-gram=`0.022222`, embedding=`0.530873`

## HOUT-TUI-08 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi năm học của ngành Tài chính – Ngân hàng, chương trình chất lượng cao, khóa 49 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Tài chính – Ngân hàng, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 33.000.000 đồng mỗi năm học.

**Required facts:** `["Tài chính – Ngân hàng", "49", "33000000", "2026-2027"]`

**Gold source:** `MucHocPhi_ChatLuongCao_TienTien.md`

**Evidence excerpt:** I. Học phí cố định theo khóa học (triệu đồng/năm học) | Chương trình Chất lượng cao | Mức thu của ngành Tài chính – Ngân hàng, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 33.000.000 đồng mỗi năm học.

**Novelty:** exact=`False`, 5-gram=`0.023256`, embedding=`0.599111`

## HOUT-TUI-09 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi tín chỉ của ngành Kinh doanh quốc tế, chương trình chất lượng cao, khóa 49 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Kinh doanh quốc tế, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 1.254.000 đồng mỗi tín chỉ.

**Required facts:** `["Kinh doanh quốc tế", "49", "1254000", "2026-2027"]`

**Gold source:** `MucHocPhi_ChatLuongCao_TienTien.md`

**Evidence excerpt:** II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ) | Chương trình Chất lượng cao (đồng/tín chỉ) | Mức thu của ngành Kinh doanh quốc tế, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 1.254.000 đồng mỗi tín chỉ.

**Novelty:** exact=`False`, 5-gram=`0.023256`, embedding=`0.593271`

## HOUT-TUI-10 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi tín chỉ của ngành Công nghệ kỹ thuật hóa học, chương trình chất lượng cao, khóa 49 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Công nghệ kỹ thuật hóa học, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 1.254.000 đồng mỗi tín chỉ.

**Required facts:** `["Công nghệ kỹ thuật hóa học", "49", "1254000", "2026-2027"]`

**Gold source:** `MucHocPhi_ChatLuongCao_TienTien.md`

**Evidence excerpt:** II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ) | Chương trình Chất lượng cao (đồng/tín chỉ) | Mức thu của ngành Công nghệ kỹ thuật hóa học, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 1.254.000 đồng mỗi tín chỉ.

**Novelty:** exact=`False`, 5-gram=`0.022222`, embedding=`0.582262`

## HOUT-TUI-11 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi năm học của ngành Kinh doanh quốc tế, chương trình chất lượng cao, khóa 50 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Kinh doanh quốc tế, chương trình chất lượng cao, khóa 50, năm học 2026-2027 là 36.000.000 đồng mỗi năm học.

**Required facts:** `["Kinh doanh quốc tế", "50", "36000000", "2026-2027"]`

**Gold source:** `MucHocPhi_ChatLuongCao_TienTien.md`

**Evidence excerpt:** I. Học phí cố định theo khóa học (triệu đồng/năm học) | Chương trình Chất lượng cao | Mức thu của ngành Kinh doanh quốc tế, chương trình chất lượng cao, khóa 50, năm học 2026-2027 là 36.000.000 đồng mỗi năm học.

**Novelty:** exact=`False`, 5-gram=`0.023256`, embedding=`0.559917`

## HOUT-TUI-12 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi tín chỉ của ngành Kỹ thuật điện, chương trình chuẩn, khóa 52 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Kỹ thuật điện, chương trình chuẩn, khóa 52, năm học 2026-2027 là 966.000 đồng mỗi tín chỉ.

**Required facts:** `["Kỹ thuật điện", "52", "966000", "2026-2027"]`

**Gold source:** `MucHocPhi_DaiHocChinhQuy_Khoa52.md`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Kỹ thuật điện, chương trình chuẩn, khóa 52, năm học 2026-2027 là 966.000 đồng mỗi tín chỉ.

**Novelty:** exact=`False`, 5-gram=`0.025`, embedding=`0.506052`

## HOUT-TUI-13 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi năm học của ngành Công nghệ thông tin, chương trình chất lượng cao, khóa 49 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Công nghệ thông tin, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 36.000.000 đồng mỗi năm học.

**Required facts:** `["Công nghệ thông tin", "49", "36000000", "2026-2027"]`

**Gold source:** `MucHocPhi_ChatLuongCao_TienTien.md`

**Evidence excerpt:** I. Học phí cố định theo khóa học (triệu đồng/năm học) | Chương trình Chất lượng cao | Mức thu của ngành Công nghệ thông tin, chương trình chất lượng cao, khóa 49, năm học 2026-2027 là 36.000.000 đồng mỗi năm học.

**Novelty:** exact=`False`, 5-gram=`0.027778`, embedding=`0.602756`

## HOUT-TUI-14 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi năm học của ngành Quản trị kinh doanh, chương trình chất lượng cao, khóa 48 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Quản trị kinh doanh, chương trình chất lượng cao, khóa 48, năm học 2026-2027 là 33.000.000 đồng mỗi năm học.

**Required facts:** `["Quản trị kinh doanh", "48", "33000000", "2026-2027"]`

**Gold source:** `MucHocPhi_ChatLuongCao_TienTien.md`

**Evidence excerpt:** I. Học phí cố định theo khóa học (triệu đồng/năm học) | Chương trình Chất lượng cao | Mức thu của ngành Quản trị kinh doanh, chương trình chất lượng cao, khóa 48, năm học 2026-2027 là 33.000.000 đồng mỗi năm học.

**Novelty:** exact=`False`, 5-gram=`0.023256`, embedding=`0.546184`

## HOUT-TUI-15 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi năm học của ngành Công nghệ thông tin, chương trình chất lượng cao, khóa 45 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Công nghệ thông tin, chương trình chất lượng cao, khóa 45, năm học 2026-2027 là 26.000.000 đồng mỗi năm học.

**Required facts:** `["Công nghệ thông tin", "45", "26000000", "2026-2027"]`

**Gold source:** `MucHocPhi_ChatLuongCao_TienTien.md`

**Evidence excerpt:** I. Học phí cố định theo khóa học (triệu đồng/năm học) | Chương trình Chất lượng cao | Mức thu của ngành Công nghệ thông tin, chương trình chất lượng cao, khóa 45, năm học 2026-2027 là 26.000.000 đồng mỗi năm học.

**Novelty:** exact=`False`, 5-gram=`0.027778`, embedding=`0.618557`

## HOUT-TUI-16 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi tín chỉ của ngành Truyền thông đa phương tiện, chương trình chuẩn, khóa 52 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Truyền thông đa phương tiện, chương trình chuẩn, khóa 52, năm học 2026-2027 là 844.000 đồng mỗi tín chỉ.

**Required facts:** `["Truyền thông đa phương tiện", "52", "844000", "2026-2027"]`

**Gold source:** `MucHocPhi_DaiHocChinhQuy_Khoa52.md`

**Evidence excerpt:** Mức học phí theo tín chỉ | Bảng học phí đại trà Khóa 52 | Mức thu của ngành Truyền thông đa phương tiện, chương trình chuẩn, khóa 52, năm học 2026-2027 là 844.000 đồng mỗi tín chỉ.

**Novelty:** exact=`False`, 5-gram=`0.02381`, embedding=`0.57479`

## HOUT-TUI-17 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi tín chỉ của ngành QT DV Du lịch và Lữ hành, chương trình chất lượng cao, khóa 48 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành QT DV Du lịch và Lữ hành, chương trình chất lượng cao, khóa 48, năm học 2026-2027 là 1.161.000 đồng mỗi tín chỉ.

**Required facts:** `["QT DV Du lịch và Lữ hành", "48", "1161000", "2026-2027"]`

**Gold source:** `MucHocPhi_ChatLuongCao_TienTien.md`

**Evidence excerpt:** II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ) | Chương trình Chất lượng cao (đồng/tín chỉ) | Mức thu của ngành QT DV Du lịch và Lữ hành, chương trình chất lượng cao, khóa 48, năm học 2026-2027 là 1.161.000 đồng mỗi tín chỉ.

**Novelty:** exact=`False`, 5-gram=`0.021739`, embedding=`0.539788`

## HOUT-TUI-18 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi tín chỉ của ngành Ngôn ngữ Anh, chương trình chất lượng cao, khóa 45 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Ngôn ngữ Anh, chương trình chất lượng cao, khóa 45, năm học 2026-2027 là 771.000 đồng mỗi tín chỉ.

**Required facts:** `["Ngôn ngữ Anh", "45", "771000", "2026-2027"]`

**Gold source:** `MucHocPhi_ChatLuongCao_TienTien.md`

**Evidence excerpt:** II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ) | Chương trình Chất lượng cao (đồng/tín chỉ) | Mức thu của ngành Ngôn ngữ Anh, chương trình chất lượng cao, khóa 45, năm học 2026-2027 là 771.000 đồng mỗi tín chỉ.

**Novelty:** exact=`False`, 5-gram=`0.02381`, embedding=`0.630295`

## HOUT-TUI-19 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi tín chỉ của ngành Kỹ thuật điện, chương trình chất lượng cao, khóa 45 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Kỹ thuật điện, chương trình chất lượng cao, khóa 45, năm học 2026-2027 là 876.000 đồng mỗi tín chỉ.

**Required facts:** `["Kỹ thuật điện", "45", "876000", "2026-2027"]`

**Gold source:** `MucHocPhi_ChatLuongCao_TienTien.md`

**Evidence excerpt:** II. Học phí cố định tính theo tín chỉ (đồng/tín chỉ) | Chương trình Chất lượng cao (đồng/tín chỉ) | Mức thu của ngành Kỹ thuật điện, chương trình chất lượng cao, khóa 45, năm học 2026-2027 là 876.000 đồng mỗi tín chỉ.

**Novelty:** exact=`False`, 5-gram=`0.02381`, embedding=`0.519905`

## HOUT-TUI-20 — actual_tuition

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Cho mình xin đúng mức thu mỗi năm học của ngành Kỹ thuật xây dựng, chương trình chất lượng cao, khóa 47 trong năm học 2026-2027?

**Reference answer:** Mức thu của ngành Kỹ thuật xây dựng, chương trình chất lượng cao, khóa 47, năm học 2026-2027 là 30.000.000 đồng mỗi năm học.

**Required facts:** `["Kỹ thuật xây dựng", "47", "30000000", "2026-2027"]`

**Gold source:** `MucHocPhi_ChatLuongCao_TienTien.md`

**Evidence excerpt:** I. Học phí cố định theo khóa học (triệu đồng/năm học) | Chương trình Chất lượng cao | Mức thu của ngành Kỹ thuật xây dựng, chương trình chất lượng cao, khóa 47, năm học 2026-2027 là 30.000.000 đồng mỗi năm học.

**Novelty:** exact=`False`, 5-gram=`0.023256`, embedding=`0.478608`

## HOUT-ACADEMIC-RULES-01 — academic_rules

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Sinh viên Trường Đại học Cần Thơ được miễn thi và tính điểm cho bao nhiêu học phần khi tham gia các kỳ thi Olympic toàn quốc hoặc cuộc thi Robocon?

**Reference answer:** Sinh viên được xem xét miễn thi và tính điểm cho một học phần trong những học phần mà sinh viên có đăng ký học trong học kỳ tham gia kỳ thi/cuộc thi, với khối lượng không quá 4 tín chỉ. Nếu sinh viên tham gia nhiều kỳ thi/cuộc thi trong một học kỳ thì chỉ được xét miễn thi và tính điểm cho không quá 2 học phần.

**Required facts:** `["Sinh viên được xem xét miễn thi và tính điểm cho một học phần", "Khối lượng học phần được miễn không quá 4 tín chỉ", "Sinh viên tham gia nhiều kỳ thi/cuộc thi trong một học kỳ chỉ được xét miễn thi và tính điểm cho không quá 2 học phần"]`

**Gold source:** `QD2457_Quy_dinh_xet_mien_va_cong_nhan_diem_HP_hinh_thuc_CQ_nam_2024_llp.md`

**Evidence excerpt:** SV được Trường ĐHCT cử tham gia và đạt thành tích cao trong các kỳ thi Olympic toàn quốc (Toán học, Vật lý, Hóa học, Tin học, Cơ học,...) do Bộ Giáo dục và Đào tạo tổ chức; cuộc thi Robocon và những kỳ thi/cuộc thi khác do Hiệu trưởng quyết định, SV được xem xét miễn thi và tính điểm cho một học phần trong những học phần mà SV có đăng ký học trong học kỳ tham gia kỳ thi/cuộc thi. Học phần được xét miễn thi do đơn vị phụ trách ngành đào tạo SV xác định và công bố cho SV khi tham gia kỳ thi/cuộc thi; có khối lượng không quá 4 tín chỉ. SV tham gia nhiều kỳ thi/cuộc thi trong một học kỳ chỉ xét miễn thi và tính điểm cho không quá 2 học phần.

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.428329`

## HOUT-ACADEMIC-RULES-02 — academic_rules

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Thời gian tối đa để sinh viên hoàn thành chương trình đào tạo đại học chính quy có thời gian thiết kế là 4,5 năm là bao nhiêu năm?

**Reference answer:** Thời gian học tập tối đa cho phép để sinh viên hoàn thành chương trình đào tạo có thời gian thiết kế là 4,5 năm là 9 năm.

**Required facts:** `["Thời gian thiết kế của chương trình đào tạo là 4,5 năm", "Thời gian học tập tối đa để sinh viên hoàn thành chương trình đào tạo là 9 năm"]`

**Gold source:** `quychehocvu.md`

**Evidence excerpt:** Thời gian học tập tối đa cho phép để SV hoàn thành CTĐT được xác định theo bảng dưới đây:

| Thời gian thiết kế của CTĐT | Thời gian học tập tối đa để SV hoàn thành CTĐT |
| --------------------------- | ---------------------------------------------- |
| 4 năm                       | 8 năm                                          |
| 4,5 năm                     | 9 năm                                          |
| 5 năm                       | 10 năm                                         |

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.539685`

## HOUT-ACADEMIC-RULES-03 — academic_rules

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Theo Quy định công tác học vụ của Trường Đại học Cần Thơ, sinh viên có thể được xét công nhận tốt nghiệp khi nào trong năm?

**Reference answer:** Sinh viên có thể được xét công nhận tốt nghiệp vào các tháng 01, tháng 6 và tháng 8 hàng năm.

**Required facts:** `["Sinh viên có đủ các điều kiện sau đây được xét công nhận tốt nghiệp", "Hằng năm, SV được xét tốt nghiệp vào tháng 01, tháng 6 và tháng 8.", "SV được nhận bằng tốt nghiệp 30 ngày kể từ ngày có quyết định công nhận tốt nghiệp."]`

**Gold source:** `QD1813_QD_ban_hanh_Quy_dinh_cong_tac_hoc_vu_2021.md`

**Evidence excerpt:** Hằng năm, SV được xét tốt nghiệp vào tháng 01, tháng 6 và tháng 8. SV được nhận bằng tốt nghiệp 30 ngày kể từ ngày có quyết định công nhận tốt nghiệp.

**Novelty:** exact=`False`, 5-gram=`0.061224`, embedding=`0.429411`

## HOUT-ACADEMIC-RULES-04 — academic_rules

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Theo quy định, mẫu đơn xin học lại này áp dụng cho trường hợp sinh viên bị đình chỉ học tập như thế nào?

**Reference answer:** Mẫu đơn xin học lại này áp dụng cho sinh viên bị đình chỉ học tập có thời hạn.

**Required facts:** `["mẫu đơn này áp dụng", "sinh viên bị đình chỉ học tập", "có thời hạn"]`

**Gold source:** `3_don_xin_hoc_lai_llp.md`

**Evidence excerpt:** Lưu ý: Mẫu này áp dụng đối với sinh viên bị đình chỉ học tập có thời hạn.

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.416043`

## HOUT-ACADEMIC-RULES-05 — academic_rules

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Theo quy định của Đại học Cần Thơ, sinh viên cần cung cấp những giấy tờ gì khi làm đơn xin tạm nghỉ học vì lý do điều trị bệnh?

**Reference answer:** Khi làm đơn xin tạm nghỉ học vì lý do điều trị bệnh, sinh viên cần nộp kèm hồ sơ hoặc giấy chỉ định của Bác sĩ.

**Required facts:** `["hồ sơ", "giấy chỉ định của Bác sĩ"]`

**Gold source:** `5_don_xin_tam_nghi_hoc_llp.md`

**Evidence excerpt:** Lý do*: Điều trị bệnh . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
(Kèm theo hồ sơ hoặc giấy chỉ định của Bác sĩ nếu có)*

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.386945`

## HOUT-ACADEMIC-RULES-06 — academic_rules

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Để minh chứng cho việc xét tuyển theo phương thức học bạ khi xin chuyển ngành, sinh viên cần nộp những loại giấy tờ nào?

**Reference answer:** Sinh viên cần nộp bản sao học bạ có công chứng hoặc chứng thực.

**Required facts:** `["xét tuyển theo phương thức học bạ", "minh chứng học bạ", "bản sao", "công chứng", "chứng thực"]`

**Gold source:** `7_don_de_nghi_chuyen_ctdt_llp.md`

**Evidence excerpt:** Nếu sử dụng xét tuyển theo phương thức học bạ, thì sinh viên cần minh chứng học bạ (bản sao, công chứng hoặc chứng thực).

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.484178`

## HOUT-SCHOLARSHIP-01 — scholarship

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Mức học bổng bình quân cho học kỳ đầu tiên của học bổng khuyến khích học tập là bao nhiêu?

**Reference answer:** Mức học bổng bình quân cho học kỳ đầu tiên là 5.000.000 đồng/học kỳ/sinh viên.

**Required facts:** `["Mức học bổng bình quân", "học kỳ đầu tiên", "5.000.000 đồng/học kỳ/sinh viên"]`

**Gold source:** `HB_K51_2026.md`

**Evidence excerpt:** Mức học bổng bình quân học kỳ đầu tiên là 5.000.000 đồng/học kỳ/sinh viên.

**Novelty:** exact=`False`, 5-gram=`0.071429`, embedding=`0.476447`

## HOUT-SCHOLARSHIP-02 — scholarship

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Học bổng Thắp sáng Niềm Tin cho tân sinh viên Khóa 52 có mức tối đa là bao nhiêu mỗi năm học và bao gồm những khoản nào?

**Reference answer:** Mức học bổng tối đa là 30.000.000 đồng/năm học, bao gồm học phí và sinh hoạt phí.

**Required facts:** `["30.000.000 đồng/năm học", "Học phí", "Sinh hoạt phí"]`

**Gold source:** `HB_TanSinhVien_K52.md`

**Evidence excerpt:** Mức học bổng: tối đa 30.000.000 đồng/năm học, gồm Học phí + Sinh hoạt phí;

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.608858`

## HOUT-SCHOLARSHIP-03 — scholarship

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Đại học Cần Thơ (CTU) được phân bổ bao nhiêu suất học bổng Vallet cho sinh viên trong năm 2026?

**Reference answer:** Đại học Cần Thơ (CTU) được phân bổ 12 suất học bổng Vallet cho sinh viên trong năm 2026.

**Required facts:** `["Đại học Cần Thơ", "CTU", "12 suất học bổng", "sinh viên", "năm 2026"]`

**Gold source:** `HB_Vallet_Chi_Tiet.md`

**Evidence excerpt:** 1     | Đại học Cần Thơ Phòng Công tác Sinh viên                                                                                                | CTU                     | 12                               |                                                       |

**Novelty:** exact=`False`, 5-gram=`0.041667`, embedding=`0.471154`

## HOUT-SCHOLARSHIP-04 — scholarship

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Năm 2026, có bao nhiêu suất học bổng "SCIC - Nâng bước tài năng trẻ" được trao cho sinh viên Trường Công nghệ Thông tin & Truyền thông, Đại học Cần Thơ và mỗi suất trị giá bao nhiêu?

**Reference answer:** Năm 2026, SCIC dành 05 suất học bổng cho sinh viên Trường Công nghệ Thông tin & Truyền thông, Đại học Cần Thơ, mỗi suất có giá trị 10.000.000 đồng.

**Required facts:** `["05 suất", "10.000.000 đồng", "SCIC", "Trường Công nghệ Thông tin & Truyền thông, Đại học Cần Thơ", "năm 2026"]`

**Gold source:** `HB_SCIC_2026.md`

**Evidence excerpt:** Năm 2026, SCIC dành 05 suất học bổng cho sinh viên theo học tại Trường Công nghệ Thông tin & Truyền thông, Đại học Cần Thơ và giá trị mỗi suất học bổng là 10.000.000 đồng (*Mười triệu đồng*).

**Novelty:** exact=`False`, 5-gram=`0.02439`, embedding=`0.443753`

## HOUT-SCHOLARSHIP-05 — scholarship

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Mức học bổng khuyến khích học tập cho sinh viên Khối V loại Giỏi là bao nhiêu tiền mỗi học kỳ?

**Reference answer:** Mức học bổng khuyến khích học tập cho sinh viên Khối V loại Giỏi là 9.050.000 đồng mỗi học kỳ.

**Required facts:** `["Mức học bổng khuyến khích học tập", "sinh viên Khối V", "loại Giỏi", "9.050.000 đồng/học kỳ"]`

**Gold source:** `Tài liệu phân bổ quỹ học bổng.md`

**Evidence excerpt:** V
                                                                                            | Sức khỏe                                                      | 7.540.000                          | 9.050.000                           | 10.560.000                              |

**Novelty:** exact=`False`, 5-gram=`0.068966`, embedding=`0.602132`

## HOUT-STUDENT-LOAN-01 — student_loan

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Mức vay vốn tối đa cho mỗi học sinh, sinh viên là bao nhiêu theo quy định mới nhất?

**Reference answer:** Mức vay vốn tối đa cho mỗi học sinh, sinh viên là 4.000.000 đồng mỗi tháng.

**Required facts:** `["Mức vay vốn tối đa", "4.000.000 đồng/tháng/học sinh, sinh viên"]`

**Gold source:** `VayVonSinhVien2022.md`

**Evidence excerpt:** Mức vay vốn tối đa là 4.000.000 đồng/tháng/học sinh, sinh viên.

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.513909`

## HOUT-STUDENT-LOAN-02 — student_loan

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Mức sinh hoạt phí tối đa mà người học có thể nhận hàng tháng theo quy định của Quyết định 29/2025/QĐ-TTg là bao nhiêu?

**Reference answer:** Mức sinh hoạt phí và chi phí học tập khác tối đa mà người học có thể nhận hàng tháng là 5 triệu đồng.

**Required facts:** `["Mức sinh hoạt phí tối đa", "5 triệu đồng/tháng", "chi phí học tập khác"]`

**Gold source:** `VayVonVoiNhomNganhKThuat - Copy.md`

**Evidence excerpt:** Tiền sinh hoạt phí và chi phí học tập khác tối đa là 5 triệu đồng/tháng.

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.569225`

## HOUT-STUDENT-LOAN-03 — student_loan

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Học sinh, sinh viên có hoàn cảnh khó khăn có thể vay tối đa bao nhiêu tiền để mua máy tính, thiết bị học tập trực tuyến theo Quyết định 09/2022/QĐ-TTg?

**Reference answer:** Mức vốn cho vay tối đa là 10 triệu đồng cho mỗi học sinh, sinh viên.

**Required facts:** `["Mức vốn cho vay tối đa", "10 triệu đồng/học sinh, sinh viên"]`

**Gold source:** `VayVonMuaMayTinh.md`

**Evidence excerpt:** Mức vốn cho vay tối đa là 10 triệu đồng/học sinh, sinh viên.

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.705596`

## HOUT-STUDENT-LOAN-04 — student_loan

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Sinh viên cần thực hiện những bước nào để đăng ký mẫu đơn xác nhận vay vốn trên hệ thống quản lý sinh viên của Trường Đại học Cần Thơ?

**Reference answer:** Để đăng ký mẫu đơn xác nhận vay vốn, sinh viên cần đăng nhập vào hệ thống quản lý sinh viên, truy cập menu Kết quả học tập, chuyển sang tab Yêu cầu xác nhận, bấm chọn nút Đăng ký tại giao diện Danh sách các yêu cầu xác nhận, chọn mục "1 - Đơn yêu cầu xác nhận vay vốn" trong danh sách Tên mẫu xác nhận, và cuối cùng bấm nút Thêm.

**Required facts:** `["Đăng nhập vào hệ thống quản lý sinh viên", "Truy cập vào menu Kết quả học tập", "Chuyển sang tab Yêu cầu xác nhận", "Bấm chọn nút Đăng ký", "Chọn mục \"1 - Đơn yêu cầu xác nhận vay vốn\"", "Bấm nút Thêm"]`

**Gold source:** `HuongDanXacNhanVayVon.md`

**Evidence excerpt:** Để đăng ký mẫu đơn xác nhận vay vốn (hoặc các loại giấy xác nhận khác), sinh viên thực hiện theo các bước sau:
- **Bước 1:** Đăng nhập vào hệ thống quản lý sinh viên của Trường Đại học Cần Thơ.
- **Bước 2:** Truy cập vào menu **Kết quả học tập**.
- **Bước 3:** Chuyển sang tab **Yêu cầu xác nhận**.
- **Bước 4:** Tại giao diện Danh sách các yêu cầu xác nhận, bấm chọn nút **Đăng ký**.
- **Bước 5:** Trong danh sách Tên mẫu xác nhận, chọn mục **"1 - Đơn yêu cầu xác nhận vay vốn"**.
- **Bước 6:** Bấm nút **Thêm**. Hệ thống sẽ thông báo đăng ký thành công.

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.686639`

## HOUT-SOCIAL-SUPPORT-01 — social_support

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Theo Thông báo về việc hỗ trợ chi phí đào tạo đại học, sinh viên dân tộc thiểu số thuộc diện nào thì đủ điều kiện nhận hỗ trợ chi phí học tập?

**Reference answer:** Sinh viên dân tộc thiểu số đang học hệ chính quy tại Trường, thuộc hộ nghèo, hộ cận nghèo hoặc ngành Sư phạm nhưng chưa được hưởng chính sách theo Nghị định số 116/2020/NĐ - CP ngày 25/9/2020 của Thủ tướng Chính phủ thì đủ điều kiện nhận hỗ trợ chi phí học tập.

**Required facts:** `["sinh viên dân tộc thiểu số", "hệ chính quy", "hộ nghèo", "hộ cận nghèo", "ngành Sư phạm", "chưa được hưởng chính sách theo Nghị định số 116/2020/NĐ - CP"]`

**Gold source:** `Ho_tro.md`

**Evidence excerpt:** Sinh viên đang học tại Trường hệ chính quy (kể cả sinh viên mới trúng tuyển vào Trường năm 2025 – Khóa 51) là người dân tộc thiểu số theo Quyết định 1227/QĐ – TTg ngày 14/7/2021 thuộc hộ nghèo, hộ cận nghèo hoặc ngành Sư phạm nhưng chưa được hưởng chính sách theo Nghị định số 116/2020/NĐ - CP ngày 25/9/2020 của Thủ tướng Chính phủ.

**Novelty:** exact=`False`, 5-gram=`0.139535`, embedding=`0.74733`

## HOUT-SOCIAL-SUPPORT-02 — social_support

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Sinh viên đã nhận hỗ trợ chi phí học tập năm 2024 cần nộp giấy tờ gì để được xét hỗ trợ chi phí học tập đợt 3 năm 2025?

**Reference answer:** Sinh viên đã được Hỗ trợ chi phí học tập năm 2024 chỉ cần nộp bổ sung Bản sao có công chứng Giấy chứng nhận hộ nghèo, hộ cận nghèo năm 2025 để làm căn cứ xét hỗ trợ chi phí học tập đợt 3 năm 2025.

**Required facts:** `["Bản sao có công chứng Giấy chứng nhận hộ nghèo, hộ cận nghèo", "năm 2025"]`

**Gold source:** `HoTroCp.md`

**Evidence excerpt:** Sinh viên đã được Hỗ trợ chi phí học tập năm 2024 chỉ cần nộp bổ sung Bản sao có công chứng Giấy chứng nhận hộ nghèo, hộ cận nghèo năm 2025 để làm căn cứ xét hỗ trợ chi phí học tập đợt 3 năm 2025.

**Novelty:** exact=`False`, 5-gram=`0.073171`, embedding=`0.529829`

## HOUT-SOCIAL-SUPPORT-03 — social_support

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Sinh viên thuộc diện mồ côi cả cha lẫn mẹ, không nơi nương tựa cần nộp những giấy tờ gì để xin hưởng trợ cấp xã hội?

**Reference answer:** Sinh viên thuộc diện mồ côi cả cha lẫn mẹ, không nơi nương tựa cần nộp đơn xin hưởng trợ cấp xã hội có xác nhận hoàn cảnh khó khăn về kinh tế không có nguồn cung cấp thường xuyên được chính quyền địa phương xác nhận, bản sao (có công chứng) giấy chứng tử của cha mẹ hoặc giấy xác nhận của UBND cấp quận, huyện, thị xã nơi cư trú là sinh viên mồ côi cả cha lẫn mẹ.

**Required facts:** `["đơn xin hưởng trợ cấp xã hội có xác nhận hoàn cảnh khó khăn về kinh tế không có nguồn cung cấp thường xuyên được chính quyền địa phương xác nhận", "bản sao (có công chứng) giấy chứng tử của cha mẹ", "giấy xác nhận của UBND cấp quận, huyện, thị xã nơi cư trú là sinh viên mồ côi cả cha lẫn mẹ"]`

**Gold source:** `Tro_cap_XH.md`

**Evidence excerpt:** Sinh viên thuộc diện mồ côi cả cha lẫn mẹ. Hồ sơ cần nộp: đơn xin hưởng trợ cấp xã hội có xác nhận hoàn cảnh khó khăn về kinh tế không có nguồn cung cấp thường xuyên được chính quyền địa phương xác nhận, bản sao (có công chứng) giấy chứng tử của cha mẹ hoặc giấy xác nhận của UBND cấp quận, huyện, thị xã nơi cư trú là sinh viên mồ côi cả cha lẫn mẹ.

**Novelty:** exact=`False`, 5-gram=`0.04878`, embedding=`0.798313`

## HOUT-SOCIAL-SUPPORT-04 — social_support

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Theo Quyết định về Trợ cấp xã hội cho sinh viên của Đại học Cần Thơ, mức trợ cấp xã hội cho mỗi sinh viên thuộc diện hộ nghèo, con mồ côi cả cha lẫn mẹ, hoặc tàn tật trên 40% là bao nhiêu và trong khoảng thời gian nào?

**Reference answer:** Mức trợ cấp là 100.000 đồng/sinh viên/tháng, áp dụng cho học kỳ 2, năm học 2025 – 2026, từ tháng 01/2026 đến tháng 04/2026.

**Required facts:** `["100.000 đồng/sinh viên/tháng", "học kỳ 2", "năm học 2025 – 2026", "tháng 01/2026", "tháng 04/2026"]`

**Gold source:** `TCXH.md`

**Evidence excerpt:** Điều 2. Mức trợ cấp là 100.000 đồng/sinh viên/tháng. Thời gian hưởng trợ cấp xã hội là học kỳ 2, năm học 2025 – 2026 (Từ tháng 01/2026 đến tháng 04/2026).

**Novelty:** exact=`False`, 5-gram=`0.031746`, embedding=`0.526346`

## HOUT-OTHER-01 — other

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Sinh viên có được phép đặt bát hương thờ cúng trong phòng ở Ký túc xá không?

**Reference answer:** Sinh viên không được phép đặt bát hương thờ cúng trong phòng ở và trong khu vực Ký túc xá.

**Required facts:** `["không được đặt bát hương thờ cúng trong phòng ở", "không được đặt bát hương thờ cúng trong khu vực Ký túc xá"]`

**Gold source:** `Noi quy KTX nam 2016_llp.md`

**Evidence excerpt:** Không được đặt bát hương thờ cúng trong phòng ở và trong khu vực KTX; Không nuôi cá, vật nuôi trong phòng ở và khu vực KTX; Không trồng các loại thực vật, cây kiểng, hoa lan trong phòng ở và hành lang các dãy nhà.

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.411692`

## HOUT-OTHER-02 — other

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Trung tâm Chuyển đổi số và Truyền thông của Trường Đại học Cần Thơ có chức năng gì đối với tài khoản và email của sinh viên?

**Reference answer:** Trung tâm Chuyển đổi số và Truyền thông có chức năng xử lý các lỗi kỹ thuật và mật khẩu của tài khoản cũng như email của sinh viên.

**Required facts:** `["Trung tâm Chuyển đổi số và Truyền thông", "xử lý lỗi kỹ thuật", "mật khẩu", "Tài khoản", "email SV"]`

**Gold source:** `SoTay.md`

**Evidence excerpt:** Trung tâm Chuyển đổi số và truyền thông

- Xử lý lỗi kỹ thuật, mật khẩu của Tài khoản và email SV.

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.397031`

## HOUT-OTHER-03 — other

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Sau khi hoàn tất các thủ tục tiếp nhận và xử lý, người có nhu cầu cần chờ bao lâu để nhận được bảng điểm?

**Reference answer:** Người có nhu cầu cần chờ 2 ngày làm việc để nhận bảng điểm.

**Required facts:** `["2 ngày làm việc", "nhận bảng điểm"]`

**Gold source:** `qt_cap_bangdiem_TV_TA_llp.md`

**Evidence excerpt:** Người có nhu cầu đến nơi đăng ký nhận bảng điểm (sau 2 ngày làm việc).

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.305564`

## HOUT-OTHER-04 — other

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Chi phí để cấp một bản sao bằng Bác sĩ thú y là bao nhiêu?

**Reference answer:** Chi phí để cấp một bản sao bằng Bác sĩ thú y là 90.000đ/1 bản.

**Required facts:** `["90.000đ/ 1 bản", "Bằng Bác sĩ thú y"]`

**Gold source:** `Phieu_De_nghi_cap_ban_sao_cap_lai_chinh_sua_NDVB_llp.md`

**Evidence excerpt:** Lệ phí: theo quy định hiện hành90.000đ/ 1 bản – Bằng Bác sĩ thú y50.000đ/ 1 bản – Các văn bằng còn lại

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.279043`

## HOUT-ACADEMIC-PROGRAM-01 — academic_program

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Chương trình đào tạo ngành Trí tuệ nhân tạo tại Trường Đại học Cần Thơ có tổng cộng bao nhiêu tín chỉ?

**Reference answer:** Chương trình đào tạo ngành Trí tuệ nhân tạo tại Trường Đại học Cần Thơ có tổng cộng 161 tín chỉ.

**Required facts:** `["Chương trình đào tạo ngành Trí tuệ nhân tạo", "Trường Đại học Cần Thơ", "161 tín chỉ"]`

**Gold source:** `108_7480107_TriTueNhanTao.md`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 113 TC; Tự chọn: 48 TC)

**Novelty:** exact=`False`, 5-gram=`0.054054`, embedding=`0.428991`

## HOUT-ACADEMIC-PROGRAM-02 — academic_program

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Chương trình đào tạo ngành Logistics và Quản lý chuỗi cung ứng có tổng cộng bao nhiêu tín chỉ?

**Reference answer:** Chương trình đào tạo ngành Logistics và Quản lý chuỗi cung ứng có tổng cộng 141 tín chỉ.

**Required facts:** `["Chương trình đào tạo ngành Logistics và Quản lý chuỗi cung ứng", "tổng cộng", "141 tín chỉ"]`

**Gold source:** `61_7510605_LogisticsVaQuanLyChuoiCungUng.md`

**Evidence excerpt:** - Ngành: Logistics và Quản lý chuỗi cung ứng (Logistics and Supply Chain Management)
- Mã ngành: 7510605
- Số lượng tín chỉ: 141 tín chỉ
- Thời gian đào tạo: 4 năm

**Novelty:** exact=`False`, 5-gram=`0.058824`, embedding=`0.340789`

## HOUT-ACADEMIC-PROGRAM-03 — academic_program

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Chương trình đào tạo ngành Đảm bảo chất lượng và an toàn thực phẩm tại Trường Đại học Cần Thơ có bao nhiêu tín chỉ bắt buộc?

**Reference answer:** Chương trình đào tạo ngành Đảm bảo chất lượng và an toàn thực phẩm có tổng cộng 161 tín chỉ, trong đó có 117 tín chỉ bắt buộc.

**Required facts:** `["161 tín chỉ", "117 tín chỉ bắt buộc"]`

**Gold source:** `114_7540106_DamBaoChatLuongVaAnToanTthucPham.md`

**Evidence excerpt:** TỔNG CỘNG CHƯƠNG TRÌNH: 161 TC (Bắt buộc: 117 TC; Tự chọn: 44 TC)

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.43795`

## HOUT-EXEMPTION-POLICY-01 — exemption_policy

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Sinh viên thuộc đối tượng nào sẽ được miễn 100% học phí nếu bản thân và cha mẹ hoặc ông bà thuộc hộ nghèo, hộ cận nghèo?

**Reference answer:** Sinh viên là dân tộc thiểu số có cha, mẹ hoặc ông, bà (Trong trường hợp ở với ông bà) thuộc hộ nghèo, hộ cận nghèo theo quy định của Thủ tướng Chính phủ sẽ được miễn 100% học phí.

**Required facts:** `["Sinh viên là dân tộc thiểu số", "cha, mẹ hoặc ông, bà thuộc hộ nghèo, hộ cận nghèo", "miễn 100% học phí"]`

**Gold source:** `mghp.md`

**Evidence excerpt:** Khoản 7-Điều 15: Sinh viên là dân tộc thiểu số có cha, mẹ hoặc ông, bà (Trong trường hợp ở với ông bà) thuộc hộ nghèo, hộ cận nghèo theo quy định của Thủ tướng Chính phủ.

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.594623`

## HOUT-EXEMPTION-POLICY-02 — exemption_policy

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Theo quy định, đơn đề nghị miễn, giảm học phí cần được gửi đến cơ quan nào?

**Reference answer:** Đơn đề nghị miễn, giảm học phí cần được gửi đến Đại học Cần Thơ.

**Required facts:** `["Đơn đề nghị miễn, giảm học phí", "gửi đến", "Đại học Cần Thơ"]`

**Gold source:** `12_don_de_nghi_mien_giam_hoc_phi_llp.md`

**Evidence excerpt:** Kính gửi : Đại học Cần Thơ.

--

# ĐƠN ĐỀ NGHỊ MIỄN, GIẢM HỌC PHÍ

**Novelty:** exact=`False`, 5-gram=`0.0`, embedding=`0.497913`

## HOUT-EXEMPTION-BASIS-01 — exemption_basis

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Mức học phí làm cơ sở tính miễn, giảm học phí cho Khối ngành IV tại Trường Đại học Cần Thơ cho năm học 2025-2026 là bao nhiêu?

**Reference answer:** Mức học phí làm cơ sở tính miễn, giảm học phí cho Khối ngành IV tại Trường Đại học Cần Thơ cho năm học 2025-2026 là 487.000 đồng/tín chỉ.

**Required facts:** `["Mức học phí làm cơ sở tính miễn, giảm học phí", "Khối ngành IV", "Trường Đại học Cần Thơ", "năm học 2025-2026", "487.000 đồng/tín chỉ"]`

**Gold source:** `MucHocPhi_2526_MienGiam.md`

**Evidence excerpt:** Các mức cần tra cứu phổ biến gồm: học phần Giáo dục quốc phòng và An ninh và Khối ngành III là **451.000 đồng/tín chỉ**; Khối ngành IV là **487.000 đồng/tín chỉ**; Khối ngành VI là **753.000 đồng/tín chỉ**; chương trình Tiên tiến Khóa 47 trở về trước là **335.000 đồng/tín chỉ**. Đây đều là mức làm cơ sở tính miễn, giảm, không phải học phí thực tế.

**Novelty:** exact=`False`, 5-gram=`0.102564`, embedding=`0.584711`

## HOUT-EXEMPTION-BASIS-02 — exemption_basis

- [x] Approved
- [x] Question đúng và tự đủ nghĩa
- [x] Answer được source chứng minh
- [x] Required facts đầy đủ
- [x] Gold source đúng

**Question:** Học phần Giáo dục quốc phòng và An ninh có mức học phí cơ sở để tính miễn, giảm học phí là bao nhiêu tiền trên một tín chỉ?

**Reference answer:** Mức học phí cơ sở để tính miễn, giảm học phí cho học phần Giáo dục quốc phòng và An ninh là 451.000 đồng/tín chỉ.

**Required facts:** `["Mức học phí cơ sở để tính miễn, giảm học phí cho học phần Giáo dục quốc phòng và An ninh là 451.000 đồng/tín chỉ."]`

**Gold source:** `MucHocPhi_2526_MienGiam.md`

**Evidence excerpt:** Các mức cần tra cứu phổ biến gồm: học phần Giáo dục quốc phòng và An ninh và Khối ngành III là **451.000 đồng/tín chỉ**; Khối ngành IV là **487.000 đồng/tín chỉ**; Khối ngành VI là **753.000 đồng/tín chỉ**; chương trình Tiên tiến Khóa 47 trở về trước là **335.000 đồng/tín chỉ**. Đây đều là mức làm cơ sở tính miễn, giảm, không phải học phí thực tế.

| TT | Học phần                       | Số tín chỉ | Mức học phí một tín chỉ |
| -- | ------------------------------ | ---------- | ----------------------- |
| 1  | Giáo dục quốc phòng và An ninh | 8          | 451.000                 |

**Novelty:** exact=`False`, 5-gram=`0.181818`, embedding=`0.67224`
