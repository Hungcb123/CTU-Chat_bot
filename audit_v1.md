# Audit Section 3 — kiến trúc PAPER_V14

Ngày rà soát: 2026-09-25  
Phạm vi: `data/PAPER_V14/sections/03-proposed-model.tex`, hình kiến trúc, code ứng dụng và script đánh giá V13.  
Hướng dẫn đối chiếu: `../rule paper/guild_writting.md`, nhất là yêu cầu Methods mô tả đủ để hiểu/tái lập, phân biệt dữ kiện với suy luận và viết alt text đúng nội dung hình.

## Kết luận

Section 3 mô tả đúng khung bốn specialist của ứng dụng, nhưng đang gộp **luồng ứng dụng** với **pipeline thí nghiệm V13** như thể chúng hoàn toàn giống nhau. Cần nêu rõ hai phạm vi trước khi dùng Section 3 làm mô tả phương pháp cho các kết quả trong bài.

## Phát hiện cần xử lý

### 1. Cao — kiến trúc ứng dụng và thực thi thí nghiệm khác nhau

- `app/agents/graph.py` dòng 184–668 xây `StateGraph`: supervisor có thể viết lại câu hỏi, sửa route, đưa academic trực tiếp đến graph agent, đưa financial/scholarship/general qua retrieval, rồi kết thúc ở `END`.
- `scripts/run_v13_architecture_experiment.py` dòng 301–495 tự triển khai supervisor → `retrieve_configurations` → specialist. Hàm này không gọi `build_agent_graph` và không thực hiện bước viết lại câu hỏi của graph ứng dụng.
- `03-proposed-model.tex` dòng 23 và 37 mô tả luồng ứng dụng nhưng không phân định với luồng đã dùng để tạo bảng kết quả.

**Đề nghị:** thêm đoạn hoặc bảng “application implementation versus evaluated configuration”. Nêu rõ bước nào được tái sử dụng, bước nào được mô phỏng/đổi trong harness V13; điều chỉnh Methods và giới hạn suy luận nếu chênh lệch này ảnh hưởng claim kiến trúc.

### 2. Cao — mô tả truy xuất liên lĩnh vực quá rộng

- `03-proposed-model.tex` dòng 59 nói retrieval layer thu thập bằng chứng từ *all relevant sources* trước khi trao cho một owner.
- Trong ứng dụng, `app/agents/graph.py` dòng 381–399 gọi `build_retrieval_lanes` theo intent đã sửa; không có bước mở rộng mọi domain liên quan một cách tổng quát.
- Trong harness, `scripts/scenario12_common.py` dòng 488–525 mở thêm một số lane khi phát hiện tín hiệu học vụ, học phí hoặc học bổng, rồi gộp ứng viên. Đây là bộ quy tắc theo tín hiệu câu hỏi, không bảo đảm bao phủ mọi nguồn liên quan.
- Specialist không gọi specialist khác (`app/agents/graph.py` dòng 663–666); nhận định này trong Section 3 là đúng.

**Đề nghị:** đổi *all relevant sources* thành *selected relevant evidence lanes* và mô tả điều kiện mở rộng lane trong bản đánh giá. Không khẳng định mọi công cụ nằm ngoài quyền của owner đều được thay bằng evidence prefetch.

### 3. Trung bình — thông số retrieval đang lấy từ hai cấu hình

- `03-proposed-model.tex` dòng 53 nêu pool ứng viên có lọc và không lọc, ngưỡng rerank 0.20, tối thiểu hai ứng viên, graph quota và tối đa bảy đoạn. Các bước này xuất hiện trong `scripts/scenario12_common.py` dòng 449–576, với `top_k=7` tại `scripts/run_v13_architecture_experiment.py` dòng 67.
- Retriever ứng dụng tại `app/services/rag_engine.py` dòng 86–89, 843–1030 mặc định trả tối đa sáu đoạn và không bật ngưỡng rerank 0.20. Ứng dụng gọi lane có metadata filter trong `app/agents/graph.py` dòng 381–399; không thực hiện cùng phép pool với nhánh không lọc như harness.
- Công thức RRF trong Section 3 là dạng không trọng số. Code ứng dụng có thể tăng trọng số BM25 lên 1.5 khi phát hiện lexical anchors (`app/services/rag_engine.py` dòng 927–964); harness dùng cả nhánh thích ứng và nhánh không thích ứng (`scripts/scenario12_common.py` dòng 473–525).

**Đề nghị:** gắn rõ các giá trị 0.20, 2 và 7 với *evaluated retrieval configuration*; mô tả riêng mặc định ứng dụng nếu vẫn trình bày hệ thống triển khai. Nếu giữ công thức, nêu trọng số BM25 thích ứng hoặc giới hạn công thức cho nhánh RRF không trọng số.

### 4. Trung bình — alt text không khớp hình

- `03-proposed-model.tex` dòng 18 đặt Redis trong tầng lưu trữ phía dưới, nhưng `data/PAPER_V14/figures/architecture.jpg` đặt **Redis Session** trong Tier 1, cạnh Chat API.
- Alt text nói mũi tên liền là đường truy cập công cụ, trong khi hình cũng dùng mũi tên liền cho luồng Student Query → Chat API → Supervisor và cho routing đến agent.
- Theo `../rule paper/guild_writting.md`, alt text chỉ mô tả điều hình thể hiện và cần truyền đạt đúng quan hệ chính.

**Đề nghị:** sửa vị trí Redis thành Tier 1; mô tả riêng luồng routing, truy cập công cụ và đường nét đứt đến retrieval/evidence stores. Rà lại caption sau khi sửa hình hoặc alt text.

### 5. Cần xác minh — thống kê Neo4j

`03-proposed-model.tex` dòng 29 ghi hơn 1.500 node, 3.800 edge, 113 chương trình, 10 nhãn và 13 loại quan hệ. Code ingest trong `Graph_DB/app/ingest.py` và `Graph_DB/app/ingest_tuition.py` có các nhãn/loại quan hệ tương ứng; số lượng node và edge thực tế **chưa được xác nhận từ một snapshot Neo4j của lần chạy đánh giá**. `app/services/graph_service.py` còn có logic bỏ qua ingest khi database đã có dữ liệu.

**Đề nghị:** lưu truy vấn đếm node/edge/label/relationship, thời điểm và phiên bản dữ liệu; trích số liệu từ đúng snapshot đánh giá. Nếu không có bản ghi, đổi sang mô tả không định lượng.

## Phần đã khớp code

- Bốn specialist và phân bổ công cụ **6 academic / 4 financial / 1 scholarship / 0 general**: `app/main.py` dòng 95–115.
- Academic đi thẳng từ supervisor đến graph agent; ba domain còn lại qua retrieval: `app/agents/graph.py` dòng 626–666.
- Các specialist không chuyển việc trực tiếp cho nhau trong LangGraph: `app/agents/graph.py` dòng 663–666.
- Phép tính học phí còn lại, kiểm tra tỷ lệ giảm trong `[0,100]`, chặn kết quả âm về 0: `app/tools/tuition.py` dòng 4–30.
- Child chunk 400 ký tự, parent target 2.800 ký tự với overlap 100, và BM25 lập chỉ mục child: `app/services/rag_engine.py` dòng 535–546, 1360–1382.

## Kiểm tra theo guild và thứ tự sửa

1. Đánh dấu rõ **ứng dụng triển khai** và **harness đánh giá** trong Section 3/4; đây là việc quan trọng nhất để người đọc hiểu chính xác phương pháp tạo kết quả.
2. Viết lại cross-domain prefetch theo điều kiện lane thực tế, kèm đầu vào/đầu ra của bước định tuyến và truy xuất.
3. Gắn công thức và tham số retrieval với đúng cấu hình; bổ sung phiên bản index/snapshot nếu bài tuyên bố có thể tái lập.
4. Sửa alt text theo hình; xuất sơ đồ vector nếu có nguồn gốc vector.
5. Xác minh số lượng graph từ snapshot trước khi giữ số liệu định lượng.

Audit này là rà soát tĩnh mã nguồn và bản thảo; chưa chạy dịch vụ Neo4j/Redis/Qdrant hoặc tái chạy benchmark.
