# Thiết kế viết lại dataset theo cách hỏi tự nhiên của sinh viên

## Mục tiêu

Thay `data/dataset.md` bằng bộ 100 câu từ file đính kèm, nhưng loại bỏ việc giả định sinh viên biết tên hoặc số hiệu văn bản pháp lý. Câu hỏi phải giống cách sinh viên thực tế hỏi chatbot, trong khi đáp án mong đợi và file nguồn không thay đổi.

## Phạm vi

- Giữ nguyên 100 ID, đáp án mong đợi và file nguồn trong bản đính kèm.
- Giữ nguyên 89 câu đã có cách hỏi tự nhiên.
- Viết lại đúng 11 câu còn nhắc `Quyết định`, `QĐ`, `Nghị định` hoặc `NĐ`.
- Bổ sung tiêu đề `1. Ngữ cảnh: Miễn giảm học phí & Hỗ trợ chi phí học tập` đang bị thiếu ở đầu file đính kèm.
- Cập nhật unit test parser từ 80 thành 100 câu.
- Không gọi `/chat`, Gemini hoặc Groq trong bước chuyển đổi và kiểm tra dataset.

## Ánh xạ câu hỏi

| ID | Câu hỏi mới |
|---:|---|
| 16 | Em là sinh viên dân tộc thiểu số thuộc hộ nghèo thì được hỗ trợ chi phí học tập bao nhiêu? |
| 17 | Khoản hỗ trợ chi phí học tập cho sinh viên dân tộc thiểu số thuộc hộ nghèo được nhận tối đa mấy tháng trong một năm học? |
| 18 | Sinh viên học văn bằng hai có được nhận hỗ trợ chi phí học tập dành cho sinh viên dân tộc thiểu số thuộc hộ nghèo không? |
| 20 | Nguồn tiền hỗ trợ chi phí học tập cho sinh viên dân tộc thiểu số thuộc hộ nghèo được lấy từ đâu? |
| 21 | Em học sư phạm và đã được Nhà nước hỗ trợ học phí, sinh hoạt phí rồi thì có được nhận thêm hỗ trợ chi phí đào tạo dành cho sinh viên dân tộc thiểu số không? |
| 22 | Sinh viên dân tộc thiểu số thuộc hộ nghèo muốn nộp hồ sơ hỗ trợ chi phí học tập thì nộp trực tiếp ở đâu? |
| 25 | Sinh viên được hỗ trợ chi phí đào tạo dành cho vùng đồng bào dân tộc thiểu số thì nộp hồ sơ ở đâu? |
| 56 | Sinh viên thuộc hộ nghèo hoặc cận nghèo có thể vay tối đa bao nhiêu tiền mỗi tháng để đi học? |
| 61 | Em học ngành STEM thì khoản vay sinh viên có thể dùng cho những chi phí nào và được hỗ trợ tối đa bao nhiêu mỗi tháng? |
| 62 | Em học ngành STEM và muốn vay tiền đi học thì lãi suất mỗi năm là bao nhiêu? |
| 71 | Sinh viên sư phạm được Nhà nước hỗ trợ sinh hoạt phí bao nhiêu mỗi tháng? |

## Quy tắc bảo toàn dữ liệu

Với mỗi ID từ 1 đến 100:

1. `Câu trả lời mong đợi` phải giống nguyên văn bản đính kèm.
2. `Tên file gốc` phải giống nguyên văn bản đính kèm.
3. Chỉ nội dung sau `Câu hỏi <ID>:` của 11 ID nêu trên được thay đổi.
4. ID phải liên tục và không trùng lặp.
5. Bốn nhóm ngữ cảnh phải được giữ theo đúng thứ tự: miễn giảm và hỗ trợ, học phí, vay vốn, học bổng.

## Kiểm tra nghiệm thu

- Parser đọc được đúng 100 câu, ID từ 1 đến 100.
- Có đủ bốn nhóm ngữ cảnh.
- Không câu hỏi nào còn chứa `Quyết định`, `QĐ`, `Nghị định`, `NĐ` hoặc `QĐ-TTg`.
- Đáp án và nguồn của cả 100 câu khớp với bản đính kèm.
- Unit test của `scripts/evaluate_chat_dataset.py` đạt.
- Dry-run đọc được dataset mà không tạo HTTP request.

## Ngoài phạm vi

- Không sửa tài liệu Markdown trong kho RAG.
- Không reindex Qdrant.
- Không thay intent router, retrieval hay prompt Gemini.
- Không đánh giá chất lượng câu trả lời thật trong bước này.
