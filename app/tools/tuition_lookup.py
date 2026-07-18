from langchain.tools import tool

from app.services.tuition_catalog import TuitionRateCatalog


@tool
def tra_cuu_hoc_phi(cau_hoi: str) -> str:
    """Tra cứu chính xác học phí thực tế theo ngành, chương trình và khóa tuyển sinh."""

    return TuitionRateCatalog.load().lookup(cau_hoi).message
