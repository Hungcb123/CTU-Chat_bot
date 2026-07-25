# Natural Student Dataset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thay bộ 80 câu hiện tại bằng bộ 100 câu đã đính kèm và viết lại 11 câu có số hiệu pháp lý thành cách hỏi tự nhiên của sinh viên.

**Architecture:** `data/dataset.md` tiếp tục là nguồn dữ liệu đánh giá duy nhất. `scripts/evaluate_chat_dataset.py` giữ nguyên vì parser đã đọc động; chỉ unit test được nâng lên 100 câu và thêm invariant cấm số hiệu văn bản trong phần câu hỏi.

**Tech Stack:** Markdown, Python 3.11 standard library, `unittest`.

## Global Constraints

- Giữ nguyên đáp án mong đợi và file nguồn của cả 100 câu từ file đính kèm.
- Chỉ viết lại câu hỏi ID 16, 17, 18, 20, 21, 22, 25, 56, 61, 62 và 71.
- Không gọi `/chat`, Gemini hoặc Groq.
- Không sửa tài liệu RAG và không reindex Qdrant.
- Không commit vì worktree đang chứa thay đổi và log của người dùng.

---

### Task 1: Khóa tiêu chí dataset bằng test

**Files:**
- Modify: `tests/test_chat_dataset_eval.py`
- Test: `tests/test_chat_dataset_eval.py`

**Interfaces:**
- Consumes: `parse_dataset(path: Path) -> list[DatasetCase]` từ `scripts/evaluate_chat_dataset.py`.
- Produces: invariant 100 ID liên tục và câu hỏi không phụ thuộc số hiệu pháp lý.

- [x] **Step 1: Đổi test số lượng từ 80 sang 100**

```python
def test_parse_all_100_cases(self):
    cases = parse_dataset(DEFAULT_DATASET)
    self.assertEqual(len(cases), 100)
    self.assertEqual([case.case_id for case in cases], list(range(1, 101)))
    self.assertEqual(cases[0].expected_sources, ("mghp.md",))
    self.assertIn("Học bổng", cases[-1].category)
```

- [x] **Step 2: Thêm test cấm tên/số hiệu pháp lý trong câu hỏi**

```python
def test_questions_do_not_require_legal_document_numbers(self):
    cases = parse_dataset(DEFAULT_DATASET)
    banned = re.compile(
        r"\b(?:quyết định|nghị định|qđ(?:-ttg)?|nđ)\b",
        re.IGNORECASE,
    )
    violations = [case.case_id for case in cases if banned.search(case.question)]
    self.assertEqual(violations, [])
```

Thêm `import re` đầu file test.

- [x] **Step 3: Chạy test để xác nhận dataset cũ thất bại**

Run:

```bash
python -m unittest tests.test_chat_dataset_eval
```

Expected: FAIL vì dataset hiện tại chỉ có 80 câu.

---

### Task 2: Thay dataset và viết lại 11 câu

**Files:**
- Modify: `data/dataset.md`
- Source: `C:\Users\ASUS PC\.codex\attachments\549ac011-cbd6-4514-ba2d-4294714350c3\pasted-text.txt`

**Interfaces:**
- Consumes: bộ 100 câu đính kèm và ánh xạ trong `docs/superpowers/specs/2026-07-19-natural-student-dataset-design.md`.
- Produces: Markdown 100 câu tương thích `parse_dataset()`.

- [x] **Step 1: Thay nội dung dataset bằng bản đính kèm**

Đặt dòng sau ở đầu file vì bản đính kèm thiếu tiêu đề nhóm đầu tiên:

```text
1. Ngữ cảnh: Miễn giảm học phí & Hỗ trợ chi phí học tập
```

Giữ nguyên các tiêu đề nhóm 2, 3, 4 và toàn bộ đáp án/nguồn.

- [x] **Step 2: Thay chính xác 11 câu hỏi**

Áp dụng nguyên văn bảng `Ánh xạ câu hỏi` trong spec cho ID:

```text
16, 17, 18, 20, 21, 22, 25, 56, 61, 62, 71
```

Không thay nội dung sau `Câu trả lời mong đợi:` và `. Tên file gốc:`.

- [x] **Step 3: Chạy unit test**

Run:

```bash
python -m unittest tests.test_chat_dataset_eval
```

Expected: 5 tests PASS.

---

### Task 3: Xác minh bảo toàn dữ liệu và dry-run

**Files:**
- Verify: `data/dataset.md`
- Verify: `scripts/evaluate_chat_dataset.py`

**Interfaces:**
- Consumes: dataset sau chuyển đổi.
- Produces: bằng chứng đủ 100 câu, không đổi đáp án/nguồn, không gọi HTTP.

- [x] **Step 1: So sánh đáp án và nguồn với attachment**

Dùng parser tạm thời đọc hai file; với mỗi ID 1..100, assert:

```python
assert converted.expected_answer == attached.expected_answer
assert converted.expected_sources == attached.expected_sources
```

Expected: 100/100 ID khớp.

- [x] **Step 2: Chạy dry-run**

Run:

```bash
python scripts/evaluate_chat_dataset.py --dry-run
```

Expected:

```text
Parsed 100 cases
Dry-run complete; no HTTP request was made.
```

- [x] **Step 3: Kiểm tra cú pháp và whitespace**

Run:

```bash
python -m py_compile scripts/evaluate_chat_dataset.py tests/test_chat_dataset_eval.py
git diff --check -- data/dataset.md tests/test_chat_dataset_eval.py
```

Expected: exit code 0.
