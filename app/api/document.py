import logging
import os
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.api.auth import require_admin
from app.models.schema import User
from app.services.ocr_service import LlamaParseAsyncClient
from app.services.document_metadata import (
    DocumentMetadataCatalog,
    MetadataCatalogError,
    normalize_document_class,
)
from app.utils.clean_md import clean_markdown_file

router = APIRouter(prefix="/document", tags=["Document"])
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"
MAX_PDF_SIZE = 5 * 1024 * 1024
READ_CHUNK_SIZE = 1024 * 1024
ALLOWED_PDF_MEDIA_TYPES = {"application/pdf", "application/x-pdf"}
UNSAFE_FILENAME_CHARS = set('<>:"/\\|?*')
WINDOWS_RESERVED_FILE_STEMS = (
    {"con", "prn", "aux", "nul"}
    | {f"com{index}" for index in range(1, 10)}
    | {f"lpt{index}" for index in range(1, 10)}
)


def _validate_pdf_filename(filename: str | None) -> str:
    if not filename:
        raise HTTPException(status_code=400, detail="Tên file không hợp lệ.")

    if (
        len(filename) > 160
        or filename in {".", ".."}
        or filename != Path(filename).name
        or filename.endswith((" ", "."))
        or any(ord(char) < 32 or char in UNSAFE_FILENAME_CHARS for char in filename)
    ):
        raise HTTPException(status_code=400, detail="Tên file không an toàn.")

    if Path(filename).suffix.casefold() != ".pdf":
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ tải lên file PDF.")

    if filename.split(".", 1)[0].casefold() in WINDOWS_RESERVED_FILE_STEMS:
        raise HTTPException(status_code=400, detail="Tên file không hợp lệ trên hệ thống.")

    return filename


def _normalise_media_type(content_type: str | None) -> str:
    return (content_type or "").partition(";")[0].strip().casefold()


async def _save_validated_pdf(file: UploadFile, destination: Path) -> None:
    await file.seek(0)
    header = await file.read(5)
    if header != b"%PDF-":
        raise HTTPException(status_code=400, detail="Nội dung file không phải PDF hợp lệ.")

    total_size = len(header)
    with destination.open("xb") as output:
        output.write(header)
        while chunk := await file.read(READ_CHUNK_SIZE):
            total_size += len(chunk)
            if total_size > MAX_PDF_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail="File PDF không được vượt quá 5 MiB.",
                )
            output.write(chunk)


def _remove_file(path: Path | None) -> None:
    if path is None:
        return
    try:
        path.unlink(missing_ok=True)
    except OSError:
        logger.warning("Không thể dọn dẹp file tạm %s", path, exc_info=True)


def _move_without_overwrite(source: Path, destination: Path) -> None:
    destination_created = False
    try:
        with source.open("rb") as input_file, destination.open("xb") as output_file:
            destination_created = True
            shutil.copyfileobj(input_file, output_file)
        source.unlink()
    except Exception:
        if destination_created:
            _remove_file(destination)
        raise


@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    document_class: str = Form(...),
    academic_year: str | None = Form(None),
    _admin: User = Depends(require_admin),
):
    """Upload, parse, clean, and ingest one admin-approved PDF document."""
    input_path: Path | None = None
    markdown_path: Path | None = None
    markdown_created = False
    ingest_attempted = False
    ingest_run_id = uuid4().hex
    completed = False
    catalog_entry_created = False
    catalog: DocumentMetadataCatalog | None = None
    normalized_metadata: dict | None = None
    engine = None

    try:
        original_filename = _validate_pdf_filename(file.filename)

        academic_year = (academic_year or "").strip() or None
        try:
            normalized_metadata = normalize_document_class(document_class, academic_year)
        except (MetadataCatalogError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from None

        media_type = _normalise_media_type(file.content_type)
        if media_type not in ALLOWED_PDF_MEDIA_TYPES:
            raise HTTPException(
                status_code=415,
                detail="File tải lên phải có MIME type application/pdf.",
            )

        api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="Hệ thống chưa được cấu hình LLAMA_CLOUD_API_KEY.",
            )

        input_dir = DATA_ROOT / "input"
        markdown_dir = DATA_ROOT / "markdown"
        done_dir = DATA_ROOT / "done"
        for directory in (input_dir, markdown_dir, done_dir):
            directory.mkdir(parents=True, exist_ok=True)

        original_path = Path(original_filename)
        input_path = input_dir / f"{uuid4().hex}.pdf"
        markdown_path = markdown_dir / f"{original_path.stem}.md"
        done_path = done_dir / original_filename

        if markdown_path.exists() or done_path.exists():
            raise HTTPException(
                status_code=409,
                detail=f"Tài liệu {original_filename} đã tồn tại.",
            )

        await _save_validated_pdf(file, input_path)
        logger.info("Đã nhận file PDF %s dưới tên lưu trữ %s", original_filename, input_path.name)

        client = LlamaParseAsyncClient(api_key=api_key)
        markdown_content = await client.parse_pdf_to_markdown(str(input_path))

        try:
            with markdown_path.open("x", encoding="utf-8") as markdown_file:
                markdown_created = True
                markdown_file.write(markdown_content)
        except FileExistsError:
            raise HTTPException(
                status_code=409,
                detail=f"Tài liệu {original_filename} đã tồn tại.",
            ) from None
        clean_markdown_file(markdown_path)

        try:
            catalog = DocumentMetadataCatalog.load()
            metadata_entry = catalog.add_uploaded_document(
                source=markdown_path.name,
                document_class=document_class,
                academic_year=academic_year,
                original_filename=original_filename,
                uploaded_by=str(_admin.username),
            )
            catalog_entry_created = True
            normalized_metadata = metadata_entry.as_dict()
        except MetadataCatalogError as exc:
            raise HTTPException(
                status_code=409 if "already exists" in str(exc).casefold() else 500,
                detail=f"Không thể ghi metadata tài liệu: {exc}",
            ) from None

        engine = request.app.state.engine
        ingest_attempted = True
        if not engine.ingest_markdown_document(
            str(markdown_path),
            ingest_run_id=ingest_run_id,
        ):
            raise HTTPException(
                status_code=500,
                detail="Không thể lưu tài liệu vào cơ sở dữ liệu vector.",
            )

        try:
            _move_without_overwrite(input_path, done_path)
        except FileExistsError:
            raise HTTPException(
                status_code=409,
                detail=f"Tài liệu {original_filename} đã tồn tại.",
            ) from None

        logger.info("Đã xử lý thành công tài liệu %s", original_filename)
        completed = True
        return {
            "status": "success",
            "message": f"Tài liệu {original_filename} đã được xử lý và học thành công.",
            "source": markdown_path.name,
            "metadata": normalized_metadata,
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Lỗi nội bộ khi xử lý tài liệu upload")
        raise HTTPException(
            status_code=500,
            detail="Không thể xử lý tài liệu do lỗi nội bộ.",
        ) from None
    finally:
        try:
            await file.close()
        except Exception:
            logger.warning("Không thể đóng file upload", exc_info=True)
        _remove_file(input_path)
        if (
            not completed
            and ingest_attempted
            and engine is not None
            and markdown_path is not None
        ):
            try:
                engine.purge_document(
                    markdown_path.name,
                    ingest_run_id=ingest_run_id,
                )
            except Exception:
                logger.error(
                    "Không thể rollback dữ liệu RAG của %s",
                    markdown_path.name,
                    exc_info=True,
                )
        if not completed and catalog_entry_created and catalog is not None and markdown_path is not None:
            try:
                catalog.remove_uploaded_document(markdown_path.name, missing_ok=True)
            except Exception:
                logger.error(
                    "Không thể rollback metadata của %s",
                    markdown_path.name,
                    exc_info=True,
                )
        if markdown_created and not completed:
            _remove_file(markdown_path)
