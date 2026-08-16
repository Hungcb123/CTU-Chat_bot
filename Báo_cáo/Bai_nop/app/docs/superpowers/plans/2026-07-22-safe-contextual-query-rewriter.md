# Safe Contextual Query Rewriter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ngăn rewriter tự thêm chương trình, ngân hàng, loại học bổng, hệ đào tạo hoặc con số không có trong câu hỏi; vẫn giải quyết đúng các câu follow-up mơ hồ dựa trên lịch sử.

**Architecture:** Câu hỏi rõ được dùng nguyên văn cho router, tuition lookup và retrieval nên không gọi Groq. Chỉ câu follow-up thật sự mơ hồ mới được contextualize bằng câu hỏi người dùng gần nhất; kết quả rewrite phải qua bộ kiểm tra deterministic trước khi được dùng, nếu không đạt thì fallback về câu gốc. Gemini vẫn luôn nhận câu hỏi gốc và không có thay đổi ở retrieval, metadata hoặc index.

**Tech Stack:** FastAPI, LangChain `ChatGroq`, Python `re`, `dataclasses`, `unittest`, Redis chat history.

## Global Constraints

- Không sửa dữ liệu Markdown, metadata, Qdrant schema, chunker, reranker hoặc tool.
- Không thêm dependency mới và không thêm LLM call mới.
- Không dùng rewriter để mở rộng sang nguồn/chương trình khác; metadata lane đã chịu trách nhiệm giới hạn miền tìm kiếm.
- Câu rõ phải giữ nguyên 100%; câu mơ hồ không có lịch sử phải fallback về câu gốc.
- Chỉ lấy câu hỏi người dùng gần nhất làm ngữ cảnh rewrite; không đưa câu trả lời AI vào prompt rewriter.
- Thay đổi này không yêu cầu reindex; chỉ cần restart FastAPI.

---

### Task 1: Khóa hợp đồng an toàn của rewriter bằng unit test

**Files:**
- Modify: `tests/test_query_intent.py`
- Modify: `app/services/query_intent.py:66-92`

**Interfaces:**
- Produces: `should_rewrite_query(query: str, previous_user_query: str | None) -> bool`
- Produces: `validate_rewritten_query(original_query: str, rewritten_query: str, previous_user_query: str | None) -> tuple[bool, str]`
- Consumes: `_normalise()` và `_classify_one()` hiện có trong `app/services/query_intent.py`

- [ ] **Step 1: Viết test câu rõ không được rewrite**

```python
from app.services.query_intent import should_rewrite_query

def test_clear_queries_skip_rewriter(self):
    clear_queries = (
        "Mức vay tối đa để mua máy tính học trực tuyến là bao nhiêu?",
        "Mỗi suất học bổng SCC trị giá bao nhiêu?",
        "Học phí tiến sĩ khóa 2026 là bao nhiêu?",
        "Học phí đào tạo từ xa khóa 2027 là bao nhiêu?",
        "Sinh viên sư phạm được hỗ trợ sinh hoạt phí bao nhiêu?",
    )
    for query in clear_queries:
        with self.subTest(query=query):
            self.assertFalse(should_rewrite_query(query, None))
```

- [ ] **Step 2: Viết test chỉ follow-up mơ hồ có lịch sử mới được rewrite**

```python
def test_only_vague_follow_up_with_user_context_is_rewritten(self):
    self.assertTrue(
        should_rewrite_query(
            "Vậy K52 thì sao?",
            "Học phí ngành CNTT CLC K51 là bao nhiêu?",
        )
    )
    self.assertFalse(should_rewrite_query("Vậy K52 thì sao?", None))
```

- [ ] **Step 3: Viết test validator từ chối entity và con số được tự thêm**

```python
from app.services.query_intent import validate_rewritten_query

def test_rewrite_rejects_unrelated_entities(self):
    cases = (
        (
            "Mức vay mua máy tính là bao nhiêu?",
            None,
            "Mức vay mua máy tính qua NHCSXH và VietinBank là bao nhiêu?",
        ),
        (
            "Mỗi suất học bổng SCC trị giá bao nhiêu?",
            None,
            "Học bổng SCC và học bổng khuyến khích học tập trị giá bao nhiêu?",
        ),
        (
            "Vậy K52 thì sao?",
            "Học phí CNTT CLC K51 là bao nhiêu?",
            "Học phí CNTT đại trà K52 là 966.000 đồng/tín chỉ?",
        ),
    )
    for original, previous, rewritten in cases:
        with self.subTest(rewritten=rewritten):
            accepted, _ = validate_rewritten_query(
                original_query=original,
                rewritten_query=rewritten,
                previous_user_query=previous,
            )
            self.assertFalse(accepted)
```

- [ ] **Step 4: Viết test validator chấp nhận contextualization bảo toàn entity**

```python
def test_rewrite_accepts_entity_preserving_follow_up(self):
    accepted, reason = validate_rewritten_query(
        original_query="Vậy K52 thì sao?",
        rewritten_query="Học phí ngành Công nghệ thông tin chương trình chất lượng cao Khóa 52 là bao nhiêu?",
        previous_user_query="Học phí ngành CNTT CLC K51 là bao nhiêu?",
    )
    self.assertTrue(accepted, reason)
```

- [ ] **Step 5: Chạy test để xác nhận đang FAIL trước khi triển khai**

Run:

```bash
./wsl_venv/bin/python -m unittest tests.test_query_intent -v
```

Expected: FAIL vì hai hàm mới chưa tồn tại.

- [ ] **Step 6: Triển khai hai hàm pure tối thiểu**

`should_rewrite_query()` chỉ trả `True` khi `_is_vague_follow_up(query)` là `True` và `previous_user_query` không rỗng.

`validate_rewritten_query()` thực hiện đúng các kiểm tra sau theo thứ tự:

```python
_PROTECTED_ENTITY_GROUPS = (
    ("nhcsxh", "ngan hang chinh sach xa hoi"),
    ("vietinbank",),
    ("clc", "chat luong cao"),
    ("tien tien",),
    ("dai tra", "chuong trinh chuan", "he chuan"),
    ("mien giam", "co so tinh mien giam", "lam co so de tinh mien giam"),
    ("scc",),
    ("vallet",),
    ("panasonic",),
    ("luong van can",),
    ("shinhan",),
    ("scic",),
    ("thap sang niem tin",),
)
```

- Reject output rỗng, nhiều dòng, dài hơn 320 ký tự hoặc có câu trả lời/meta-text như `"tôi không"`, `"xin lỗi"`, `"không thể"`, `"dựa trên"`, `"câu trả lời"`.
- Tạo `allowed_text = original_query + previous_user_query`.
- Với mỗi nhóm entity, nếu rewrite có nhóm đó nhưng `allowed_text` không có thì reject.
- Mọi token số trong rewrite phải đã xuất hiện trong `allowed_text`; việc đổi `K52` thành `Khóa 52` vẫn hợp lệ vì cùng token `52`.
- Chuẩn hóa alias `CNTT/Công nghệ thông tin`, `CLC/Chất lượng cao`, `GDQP/Giáo dục quốc phòng` và `K52/Khóa 52`; sau đó reject mọi content token mới ngoài câu hiện tại + câu người dùng trước đó.
- Nếu intent rõ của `previous_user_query` khác intent rewrite thì reject.
- Trả `(True, "accepted")` nếu toàn bộ kiểm tra đạt; không sửa nội dung rewrite trong validator.

- [ ] **Step 7: Chạy test và xác nhận PASS**

Run:

```bash
./wsl_venv/bin/python -m unittest tests.test_query_intent -v
```

Expected: toàn bộ test query intent PASS.

---

### Task 2: Biến query expansion thành contextualizer có điều kiện

**Files:**
- Modify: `app/api/chat.py:18-23`
- Modify: `app/api/chat.py:89-140`
- Test: `tests/test_query_intent.py`

**Interfaces:**
- Consumes: `should_rewrite_query()` và `validate_rewritten_query()` từ Task 1
- Produces: `search_query`, `rewrite_status`, `rewrite_reason`

- [ ] **Step 1: Import hai helper mới**

```python
from app.services.query_intent import (
    ...,
    should_rewrite_query,
    validate_rewritten_query,
)
```

- [ ] **Step 2: Chỉ lấy câu hỏi người dùng gần nhất làm ngữ cảnh**

Sau khi tạo `chat_history`, lấy ngữ cảnh bằng:

```python
previous_user_query = next(
    (
        message.content
        for message in reversed(chat_history)
        if isinstance(message, HumanMessage)
    ),
    None,
)
```

Không nối `AIMessage` vào prompt rewriter. `chat_history` đầy đủ vẫn được giữ nguyên cho Gemini ở bước generation.

- [ ] **Step 3: Bỏ toàn bộ luật mở rộng bắt buộc hiện tại**

Xóa các luật ép thêm:

- cả NHCSXH và VietinBank;
- cả học bổng khuyến khích và học bổng doanh nghiệp;
- từ `Đại trà` khi người dùng không nói;
- cụm miễn giảm được thêm một cách suy diễn.

Thay prompt bằng contextualizer ngắn:

```python
rewrite_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Bạn chỉ làm rõ đại từ hoặc phần bị lược bỏ trong câu hỏi hiện tại "
        "bằng câu hỏi trước đó của người dùng. Không thêm ngân hàng, học bổng, "
        "chương trình đào tạo, ngành, khóa, năm học, chính sách, con số hoặc "
        "điều kiện không có trong hai câu. Không trả lời. Chỉ in một câu truy vấn.",
    ),
    (
        "human",
        "Câu hỏi trước của người dùng: {previous_user_query}\n"
        "Câu hỏi hiện tại: {question}\n"
        "Câu truy vấn độc lập:",
    ),
])
```

- [ ] **Step 4: Skip Groq cho câu rõ và fallback an toàn cho câu mơ hồ**

```python
search_query = request.query
rewrite_status = "skipped"
rewrite_reason = "clear_original_query"

if should_rewrite_query(request.query, previous_user_query):
    candidate = await rewrite_chain.ainvoke({
        "previous_user_query": previous_user_query,
        "question": request.query,
    })
    candidate = candidate.strip().strip('"').strip("'")
    accepted, rewrite_reason = validate_rewritten_query(
        request.query,
        candidate,
        previous_user_query,
    )
    if accepted:
        search_query = candidate
        rewrite_status = "accepted"
    else:
        rewrite_status = "rejected"
```

Nếu Groq lỗi hoặc timeout, giữ `search_query = request.query`; không làm `/chat` trả 500 chỉ vì rewriter phụ bị lỗi.

- [ ] **Step 5: Giữ nguyên quyền ưu tiên của câu gốc**

- `classify_query_intent(request.query, search_query)` vẫn xét câu gốc trước như hiện tại.
- `tuition_catalog.lookup(request.query)` vẫn chạy trước rewrite.
- `rewrite_is_safe_for_lookup()` vẫn là lớp bảo vệ riêng cho structured tuition lookup.
- Gemini vẫn nhận `question=request.query`, không nhận rewrite làm câu hỏi trả lời.

- [ ] **Step 6: Chạy unit test liên quan**

Run:

```bash
./wsl_venv/bin/python -m unittest \
  tests.test_query_intent \
  tests.test_tuition_catalog -v
```

Expected: PASS.

---

### Task 3: Bổ sung observability để biết rewrite được dùng hay bị loại

**Files:**
- Modify: `app/api/chat.py:254-280`

**Interfaces:**
- Consumes: `rewrite_status`, `rewrite_reason`, `previous_user_query`, `search_query`
- Produces: log chẩn đoán không chứa toàn bộ câu trả lời AI cũ

- [ ] **Step 1: Thay log chung bằng log trạng thái có lý do**

```python
logger.info(
    "Query rewrite status=%s reason=%s original=%r search=%r",
    rewrite_status,
    rewrite_reason,
    request.query,
    search_query,
)
```

- [ ] **Step 2: Ghi trạng thái vào `logs/retrieved_docs.log`**

Thêm đúng hai dòng trước danh sách docs:

```python
log_lines.append(f"[REWRITE STATUS]: {rewrite_status} ({rewrite_reason})")
log_lines.append(f"[SEARCH QUERY]: {search_query}")
```

Không ghi lại `previous_user_query` nếu không cần, để log không phình và hạn chế lưu lịch sử người dùng dư thừa.

- [ ] **Step 3: Kiểm tra log bằng unit/static test**

Run:

```bash
./wsl_venv/bin/python -m py_compile app/api/chat.py app/services/query_intent.py
```

Expected: exit code 0.

---

### Task 4: Kiểm thử hồi quy không gọi Gemini trước, rồi mới smoke test `/chat`

**Files:**
- Modify: `tests/test_query_intent.py`
- Existing: `scripts/test_retriever.py`
- Existing: `scripts/evaluate_chat_dataset.py`

**Interfaces:**
- Consumes: flow rewriter mới từ Tasks 1-3
- Produces: bằng chứng không còn entity injection và không regression 4 lĩnh vực

- [ ] **Step 1: Chạy toàn bộ unit test không cần dịch vụ ngoài**

Run:

```bash
./wsl_venv/bin/python -m unittest \
  tests.test_query_intent \
  tests.test_tuition_catalog \
  tests.test_chat_dataset_eval \
  tests.test_document_metadata -v
```

Expected: PASS.

- [ ] **Step 2: Chạy retrieval-only test**

Run khi Qdrant/PostgreSQL đang hoạt động:

```bash
./wsl_venv/bin/python scripts/test_retriever.py
```

Expected: các assertion học phí thực tế, cơ sở miễn giảm, học bổng, vay vốn và concurrent filter đều PASS; không có Gemini call.

- [ ] **Step 3: Restart app, không reindex**

```bash
./wsl_venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Không chạy `rollout_mvp.sh` và không tạo collection mới vì vector, chunk và metadata không thay đổi.

- [ ] **Step 4: Smoke test 10 câu qua đúng `/chat`**

Dùng session riêng cho tám câu rõ và một session chung cho hai follow-up:

1. `Mức vay tối đa để mua máy tính học trực tuyến là bao nhiêu?`
2. `Mỗi suất học bổng SCC trị giá bao nhiêu?`
3. `Mỗi suất học bổng Panasonic trị giá bao nhiêu?`
4. `Học phí tiến sĩ khóa 2026 là bao nhiêu?`
5. `Học phí đào tạo từ xa khóa 2027 là bao nhiêu một tín chỉ?`
6. `Sinh viên sư phạm được hỗ trợ sinh hoạt phí bao nhiêu mỗi tháng?`
7. `Học phí CNTT CLC K49 là bao nhiêu?`
8. `Hồ sơ học bổng Vallet gồm gì?`
9. Session follow-up, câu đầu: `Học phí CNTT CLC K51 là bao nhiêu?`
10. Cùng session: `Vậy K52 thì sao?`

Expected log:

- Câu 1-9: `rewrite_status=skipped`, `search_query` giống nguyên văn câu gốc.
- Câu 10: `rewrite_status=accepted`; giữ `CNTT`, `CLC`, đổi `K51` thành `K52`; không thêm `Đại trà`, miễn giảm hoặc mức tiền.
- Không câu vay mua máy tính nào bị thêm VietinBank.
- Không câu SCC/Panasonic/Vallet nào bị thêm loại học bổng khác.
- Không câu sau đại học/từ xa nào bị thêm hệ Đại trà.

- [ ] **Step 5: Gate nghiệm thu**

- 100% câu rõ không gọi Groq rewriter.
- 0 rewrite được chấp nhận có entity hoặc con số mới ngoài câu gốc + câu hỏi người dùng gần nhất.
- Follow-up mơ hồ có lịch sử tạo được câu độc lập đúng chủ đề.
- Groq lỗi không làm `/chat` lỗi.
- Router intent, tuition lookup, tool calling và Gemini generation không đổi hành vi ngoài việc nhận context retrieval sạch hơn.
- Không reindex và không thay đổi collection alias.

## Root cause đã xác nhận

Trong `app/api/chat.py:107-120`, prompt hiện tại ép rewriter mở rộng nguồn thay vì chỉ làm rõ câu hỏi. `logs/retrieved_docs.log` cho thấy trực tiếp:

- câu vay mua máy tính bị thêm cả NHCSXH và VietinBank;
- câu SCC/Panasonic bị thêm học bổng khuyến khích và học bổng doanh nghiệp;
- câu tiến sĩ, thạc sĩ, từ xa và dự bị dân tộc bị thêm `Đại trà`;
- toàn bộ AI answer gần đây cũng được đưa vào `history_text`, có thể truyền tiếp chi tiết sai sang rewrite.

Do router metadata đã phân lane và structured tuition lookup đã xử lý ngành/khóa/hệ, query expansion rộng không còn cần thiết. Rewriter chỉ còn một nhiệm vụ: giải quyết đại từ và phần bị lược bỏ trong follow-up.
