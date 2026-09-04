
## Hướng dẫn sửa file `rag_engine.py`

 **Bước 1** : Mở `rag_engine.py` và tìm dòng khoảng **691-693**

use_reranker: bool = True,
        hybrid_search: bool = True,
    ) -> List[Document]:

 **Bước 2** : Thay đổi đoạn này:

**        use_reranker: **bool** **=** **True**,**

**        hybrid_search: **bool** **=** **True**,**

**    **)** **->** List**[**Document**]**:**

Thành:

**        use_reranker: **bool** **=** **True**,**

**        hybrid_search: **bool** **=** **True**,**

**        retrieval_mode: **str** **=** **"hybrid_rrf_rerank"**,**

**    **)** **->** List**[**Document**]**:**

 **Bước 3** : Thay đổi docstring (dòng 694):

**        **"""Truy xuất tài liệu theo cơ chế Hybrid Search **(Dense Vector + Sparse BM25) & Re-ranking."""**

Thành:

**        **"""Truy xuất tài liệu theo mô hình retrieval được **chọn cho Table 5.**

**        Chế độ hỗ trợ:**

**        - dense_only: chỉ dùng vector search, **không dùng BM25 và không rerank

**        - sparse_only: chỉ dùng BM25, không dùng **dense và không rerank

**        - hybrid_rrf: dùng cả dense + BM25 nhưng **không rerank

**        - hybrid_rrf_rerank: dùng cả dense + BM25 **và rerank cuối cùng

**        """**

 **Bước 4** : Thêm code validation và mode handling ngay sau `if not query or not query.strip():` (khoảng dòng 696):

**        **if** **not** query **or** **not** query.strip**(**)**:

**            **return** **[**]**

**        **# Validate và normalize retrieval_mode

**        normalized_mode **=** **(**retrieval_mode **or** **"hybrid_rrf_rerank"**)**.lower**(**)**.strip**(**)**

**        allowed_modes **=** **{**"dense_only"**, **"sparse_only"**, **"hybrid_rrf"**, **"hybrid_rrf_rerank"**}

**        **if** normalized_mode **not** **in** allowed_modes:**

**            **raise** **ValueError**(**

**                **f**"retrieval_mode '**{**retrieval_mode**}**' không hợp lệ. Chỉ hỗ trợ: **{**sorted**(**allowed_modes**)**}**"

**            **)

**        **# Điều chỉnh flags dựa trên mode

**        **if** normalized_mode **==** **"dense_only"**:**

**            hybrid_search **=** **False

**            use_reranker **=** **False

**        **elif** normalized_mode **==** **"sparse_only"**:**

**            hybrid_search **=** **False

**            use_reranker **=** **False

**        **elif** normalized_mode **==** **"hybrid_rrf"**:**

**            hybrid_search **=** **True

**            use_reranker **=** **False

**        **elif** normalized_mode **==** **"hybrid_rrf_rerank"**:**

**            hybrid_search **=** **True

**            use_reranker **=** **bool**(**use_reranker**)**

**        enabled **=** **(

 **Bước 5** : Sửa dòng `dense_docs = list(base_retriever.invoke(query))` để kiểm tra mode:

Thay `if hybrid_search and self.bm25_index and self.bm25_index.is_indexed():`

Thành `if normalized_mode != "sparse_only" and hybrid_search and self.bm25_index and self.bm25_index.is_indexed():`

Sau khi sửa xong, hãy chạy:

python -m py_compile app/services/rag_engine.py

Nếu không có lỗi, file đã OK. Sau đó bạn có thể chạy file test:

`python scripts/test_table5_ragas.py`
