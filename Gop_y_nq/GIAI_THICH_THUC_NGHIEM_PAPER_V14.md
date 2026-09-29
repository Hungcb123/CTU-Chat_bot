# Giải thích thực nghiệm của PAPER_V14

Tài liệu này tổng hợp các câu hỏi và phần giải thích về thực nghiệm được sử dụng trong bài báo `data/PAPER_V14/main.pdf`.

## 1. Source nào được dùng để chạy thực nghiệm?

### Scenario 1 và Scenario 2

- Source chạy: `scripts/run_v13_architecture_experiment.py`
- Log hoàn chỉnh: `logs/v13_architecture/run_20260923_155602/results.jsonl`
- Metadata: `logs/v13_architecture/run_20260923_155602/metadata.json`
- Benchmark: `data/scenario12_heldout_100.jsonl`
- Chấm lại bằng nhãn đã xác minh: `scripts/recompute_verified_stats.py`
- Kiểm toán số liệu: `scripts/audit_table1_integrity.py`
- Kết quả chấm lại: `report/recomputed_stats.txt`

Batch `run_20260923_155602` có đủ 700 bản ghi cho bảy cấu hình. Batch `run_20260923_152038` chỉ có 153 bản ghi nên là lượt chạy chưa hoàn tất.

### Scenario 3

- Source chạy: `scripts/run_multi_vs_single_agent_v6_ambiguity.py`
- Log: `logs/multi_vs_single_v6/20260922T045842Z/`
- Kết quả tổng hợp: `logs/multi_vs_single_v6/20260922T045842Z/comparison.md`

## 2. Thực nghiệm đang kiểm tra điều gì?

Câu hỏi nghiên cứu chính là:

> Chia chatbot thành nhiều agent chuyên môn có hiệu quả hơn một agent làm tất cả hay không?

Thực nghiệm được chia thành ba nhóm.

## 3. Scenario 1 — So sánh kiến trúc chatbot

Ba cách tổ chức được kiểm tra trên cùng 100 câu hỏi:

1. **Single Agent:** một agent nhìn thấy toàn bộ 11 công cụ.
2. **Routed Generic:** router chia câu hỏi theo lĩnh vực, nhưng agent sử dụng prompt chung.
3. **CTU-Chat:** router chuyển câu hỏi đến agent chuyên môn; mỗi agent có prompt và phạm vi công cụ riêng.

### Kỹ thuật kiểm tra

- Cùng mô hình `Gemini 2.5 Flash Lite`.
- Cùng dữ liệu, công cụ và kết quả truy xuất.
- `temperature = 0` để giảm tính ngẫu nhiên.
- Dùng paired bootstrap để ước lượng khoảng tin cậy.
- Dùng kiểm định McNemar để so sánh kết quả đúng/sai theo từng câu hỏi.

### Tiêu chí kiểm tra

- **E2E Success:** câu trả lời chứa ít nhất 50% các ý bắt buộc trong đáp án chuẩn.
- **Fact Coverage:** tỷ lệ thông tin bắt buộc được câu trả lời bao phủ.
- **Source Recall/AP:** hệ thống có tìm đúng tài liệu nguồn hay không.
- **Tool selection/execution:** có chọn và chạy đúng công cụ hay không.
- **Input/output tokens:** chi phí token.
- **Latency:** thời gian trả lời.

### Kết quả

| Hệ thống | E2E | Fact Coverage | Input token | Thời gian trung bình |
|---|---:|---:|---:|---:|
| Single Agent | 66,0% | 57,5% | 6.296 | 5,16 giây |
| Routed Generic | 66,0% | 54,2% | 3.473 | 8,92 giây |
| CTU-Chat | **76,0%** | **61,0%** | 3.690 | 10,65 giây |

CTU-Chat cao hơn Single Agent 10 điểm phần trăm E2E và sử dụng ít hơn khoảng 41,4% input token. Đổi lại, hệ thống chậm hơn vì phải thực hiện thêm bước định tuyến và gọi agent chuyên môn. Kiểm định McNemar cho kết quả `p = 0,0414`.

## 4. Scenario 2 — Loại bỏ từng thành phần

Kỹ thuật này gọi là **ablation study**: mỗi lần chỉ bỏ hoặc thay một thành phần của CTU-Chat để xem thành phần đó ảnh hưởng thế nào.

Các cấu hình gồm:

- Bỏ prompt chuyên môn.
- Bỏ cô lập công cụ, cho agent nhìn thấy toàn bộ công cụ.
- Thay Neo4j và dữ liệu cấu trúc bằng Text-RAG đồng nhất.
- Bỏ tính toán học phí xác định.
- Bỏ bước sửa route.

### Kết quả chính

- Bỏ prompt chuyên môn: E2E giảm khoảng 10 điểm phần trăm.
- Chuyển toàn bộ sang Text-RAG: E2E giảm khoảng 9 điểm và Source Recall giảm 12,3 điểm.
- Bỏ route repair: E2E giảm khoảng 2 điểm.
- Bỏ tính toán xác định: E2E giảm khoảng 4 điểm.
- Cho thấy toàn bộ công cụ: kết quả gần như không đổi khi chỉ có 11 công cụ, nhưng tốn thêm khoảng 1.270 input token.

Hai thành phần có ảnh hưởng rõ nhất là prompt chuyên môn và việc sử dụng đúng loại kho dữ liệu cho từng dạng câu hỏi.

## 5. “Tăng công cụ” nghĩa là gì?

Tăng công cụ nghĩa là tăng số hàm/API mà mô hình phải lựa chọn, không phải tăng số agent hoặc tăng lượng tài liệu.

Thực nghiệm sử dụng ba mức:

- **11 công cụ:** 11 công cụ thật, chưa thêm công cụ gây nhiễu.
- **31 công cụ:** 11 công cụ thật và 20 công cụ gần nghĩa.
- **51 công cụ:** 11 công cụ thật và 40 công cụ gần nghĩa.

Có 10 nhóm công cụ chính. Mỗi nhóm được bổ sung tối đa bốn công cụ gần nghĩa:

```text
Tổng số công cụ = 11 + 10 × mức độ nhiễu
```

Ba mức độ nhiễu được sử dụng là `0`, `2` và `4`, tương ứng với 11, 31 và 51 công cụ.

Các công cụ bổ sung là **semantic neighbors**: tên và chức năng gần giống công cụ đúng, được dùng để kiểm tra khả năng phân biệt của mô hình. Ví dụ:

- Tra cứu mức học phí thực tế.
- Tra cứu học phí theo khóa.
- Tra cứu chính sách học phí.
- Tra cứu cơ sở miễn giảm.
- Tính học phí sau miễn giảm.

Trong thiết kế hiện tại, 51 là mức tối đa đã được chuẩn bị và khóa trước khi chạy. Về lý thuyết có thể tăng thêm, nhưng cần xây dựng thêm các công cụ gần nghĩa hợp lý và thiết kế lại protocol. Vì vậy, kết quả hiện tại chỉ hỗ trợ kết luận trong phạm vi 11–51 công cụ.

## 6. Bốn cách tổ chức nhìn thấy bao nhiêu công cụ?

Ở mỗi mức, cả bốn cách đều hoạt động trên cùng một kho công cụ chung. Tuy nhiên, số công cụ thực sự được đưa vào prompt khác nhau:

- **Full Single Agent:** nhìn thấy toàn bộ 11, 31 hoặc 51 công cụ.
- **Top-10 Single:** chọn tối đa 10 công cụ liên quan từ toàn bộ kho.
- **Routed Generic:** router chọn lĩnh vực, sau đó lấy tối đa 10 công cụ trong lĩnh vực đó.
- **Routed Specialist:** giống Routed Generic nhưng có thêm hướng dẫn chuyên môn để phân biệt các công cụ gần nghĩa.

Tại mức 51 công cụ:

| Cách tổ chức | Số công cụ nhìn thấy | E2E | Input token |
|---|---:|---:|---:|
| Full Single Agent | 51 | 83,3% | 3.722 |
| Top-10 Single | 10 | 78,7% | 1.036 |
| Routed Generic | trung bình 9,8 | 82,7% | 1.340 |
| Routed Specialist | trung bình 9,8 | **88,0%** | 1.770 |

Nhìn thấy nhiều công cụ có thể làm mô hình dễ chọn nhầm và tốn token hơn. Tuy nhiên, ít công cụ chưa chắc tốt hơn: bộ lọc Top-10 có thể loại mất công cụ đúng trước khi mô hình được lựa chọn.

Vì vậy có hai dạng lỗi:

1. **Quá nhiều công cụ:** công cụ đúng có mặt nhưng mô hình chọn nhầm công cụ gần nghĩa.
2. **Lọc quá mạnh:** danh sách ngắn hơn nhưng công cụ đúng bị loại khỏi danh sách.

## 7. Routed Specialist cân bằng hai vấn đề như thế nào?

Quy trình gồm bốn bước:

```text
Câu hỏi
   ↓
1. Router chọn lĩnh vực
   ↓
2. Lọc Top-10 công cụ trong lĩnh vực
   ↓
3. Prompt chuyên môn phân biệt các công cụ gần nghĩa
   ↓
4. Chọn tối đa một công cụ và kiểm tra tham số
```

### Bước 1 — Router chọn lĩnh vực

Router chưa chọn công cụ ngay. Nó trả về dữ liệu có cấu trúc gồm:

- `next_agent`: `academic`, `financial`, `scholarship` hoặc `general`.
- `intent`: ý định chi tiết như `actual_tuition`, `exemption_basis`, `calculation` hoặc `academic_rules`.

Ví dụ với câu hỏi:

> Học phí ngành Công nghệ thông tin khóa 52 bao nhiêu?

Router có thể xác định:

```text
agent  = financial
intent = actual_tuition
```

Nhờ đó, các công cụ học vụ, ký túc xá và học bổng bị loại khỏi phạm vi lựa chọn. Một lớp `route repair` còn kiểm tra và sửa các cặp agent–intent không phù hợp với nội dung câu hỏi.

### Bước 2 — Lọc Top-10 trong đúng lĩnh vực

Sau khi chọn lĩnh vực, hệ thống sử dụng BM25 để xếp hạng các công cụ trong lĩnh vực đó theo độ liên quan giữa câu hỏi và mô tả công cụ. Hệ thống chỉ giữ tối đa 10 công cụ.

Điểm khác biệt là:

- Top-10 Single tìm 10 công cụ từ toàn bộ 51 công cụ.
- Routed Specialist trước tiên giới hạn đúng lĩnh vực, sau đó mới tìm Top-10.

### Bước 3 — Prompt “dùng khi / không dùng khi”

Routed Specialist nhận ranh giới cụ thể cho từng công cụ. Ví dụ:

```text
tra_cuu_hoc_phi_graph:
- Dùng khi hỏi mức học phí thực tế theo ngành và khóa.
- Không dùng khi hỏi tổng hóa đơn, phụ thu hoặc lịch sử đóng tiền.

tra_cuu_co_so_mien_giam_graph:
- Dùng khi hỏi mức tiền làm cơ sở tính miễn giảm.
- Không dùng khi hỏi đối tượng, tỷ lệ hoặc hồ sơ miễn giảm.

tinh_toan_hoc_phi:
- Dùng khi cần tính số tiền còn đóng sau miễn giảm và có đủ dữ liệu.
- Không dùng khi hỏi tiền phạt, tiền hoàn hoặc chia đợt.
```

Đây là **contrastive specialist policy**: mô hình được cung cấp cả trường hợp nên dùng và các trường hợp gần giống nhưng không nên dùng.

### Bước 4 — Giới hạn và kiểm tra hành động

Prompt yêu cầu:

- Chọn tối đa một công cụ.
- Không tự bịa tham số còn thiếu.
- Không gọi công cụ ngoài phạm vi.
- Chỉ gọi khi các tham số bắt buộc hợp lệ.

Sau đó schema guard kiểm tra cấu trúc tham số. Nhờ kết hợp router, lọc theo lĩnh vực, prompt đối chiếu và kiểm tra schema, Routed Specialist đạt 88% E2E tại mức 51 công cụ.

Hệ thống vẫn có giới hạn: nếu router chọn sai lĩnh vực hoặc BM25 loại mất công cụ đúng thì prompt chuyên môn phía sau không thể khôi phục công cụ đó. Trong kết quả mức 51, công cụ đúng xuất hiện trong danh sách của Routed Specialist khoảng 98%, không phải 100%.

## 8. “Truyền sai tham số” nghĩa là gì?

Đây là trường hợp mô hình chọn đúng công cụ nhưng cung cấp dữ liệu đầu vào sai, thiếu hoặc đảo vị trí.

Ví dụ công cụ:

```text
tinh_toan_hoc_phi(
  hoc_phi_moi_tin_chi,
  muc_co_so_mien_giam,
  phan_tram_mien_giam
)
```

Với câu hỏi:

> Học phí 966.000 đồng/tín chỉ, mức cơ sở miễn giảm 538.000 đồng và được giảm 70%. Sinh viên còn đóng bao nhiêu?

Gọi đúng:

```text
tinh_toan_hoc_phi(966000, 538000, 70)
```

Gọi sai:

```text
tinh_toan_hoc_phi(966000, 70, 538000)
```

Ở lời gọi sai, mức cơ sở miễn giảm và phần trăm miễn giảm bị đảo vị trí. Vì vậy, dù chọn đúng công cụ, kết quả tính toán vẫn sai hoặc bị schema guard từ chối.

## 9. Kết luận chung

Kết quả thực nghiệm cho thấy CTU-Chat:

- Có E2E cao hơn Single Agent trên benchmark 100 câu hỏi.
- Giảm đáng kể input token nhờ giới hạn phạm vi công cụ.
- Ít bị nhầm công cụ hơn khi kho công cụ có nhiều chức năng gần nghĩa.
- Hưởng lợi rõ từ prompt chuyên môn và cách phân bổ đúng loại dữ liệu.
- Chậm hơn vì cần thêm bước định tuyến và lựa chọn chuyên môn.

Thông điệp chính không phải “càng ít công cụ càng tốt”, mà là:

> Hệ thống cần lọc đúng phạm vi công cụ, giữ được công cụ cần thiết và cung cấp đủ hướng dẫn để phân biệt những công cụ gần nghĩa.
