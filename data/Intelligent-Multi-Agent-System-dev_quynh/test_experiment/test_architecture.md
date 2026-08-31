
**1/ Cấu trúc test**

test_dataset.json
       ↓
evaluation_runner.py
       ↓
experiment config
       ↓
BM25 / Dense / Hybrid / Graph / Agent
       ↓
metrics
       ↓
results.csv

**2/ Dataset nên có các field gì**

- có tiếng Việt và tiếng Anh;
- cân bằng theo category;
- mỗi câu có date;
- có source document;
- có required facts;
- câu test được con người xác minh;
- development questions không được lẫn vào test;
- toàn bộ đánh giá dùng một frozen database snapshot


**3/ Test RAGAS**

Test bằng **RAGAS** là đánh giá chất lượng hệ thống RAG bằng cách đưa vào một tập câu hỏi, chạy RAG để lấy  **context + câu trả lời** , rồi RAGAS tính các metric.

Ví dụ dataset:

<pre class="overflow-visible! px-0!" data-start="178" data-end="301"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="relative h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class=""><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>{
  "question": </span><span class="ͼk">"Học phí được tính như thế nào?"</span><span>,
  "ground_truth": </span><span class="ͼk">"Học phí tính theo số tín chỉ đăng ký..."</span><span>
}</span></code></pre></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></div></div></pre>

Sau khi chạy RAG, RAGAS có thể đánh giá:

* **Faithfulness** : câu trả lời có bám đúng tài liệu retrieved không.
* **Answer Relevancy** : câu trả lời có đúng trọng tâm câu hỏi không.
* **Context Precision** : các chunk lấy về có thực sự liên quan không.
* **Context Recall** : retrieval có lấy đủ thông tin cần thiết không.
* **Answer Correctness** : câu trả lời có đúng với đáp án chuẩn không.

Kết quả thường dạng:

<pre class="overflow-visible! px-0!" data-start="716" data-end="852"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>Faithfulness:       0.92
Answer Relevancy:   0.88
Context Precision:  0.85
Context Recall:     0.90
Answer Correctness: 0.87</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

Tức là  **RAGAS không chủ yếu test code có lỗi hay không** , mà test  **chất lượng Retrieval và Generation của RAG** . Với bài báo RAG, các điểm số này có thể dùng để so sánh các cấu hình/experiment khác nhau.
