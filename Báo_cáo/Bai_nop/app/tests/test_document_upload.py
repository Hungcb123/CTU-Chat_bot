from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException
from pydantic import BaseModel


def _load_document_module():
    """Load app.api.document without importing auth/database/LLM dependencies."""

    auth_stub = types.ModuleType("app.api.auth")

    async def require_admin():
        return None

    auth_stub.require_admin = require_admin

    schema_stub = types.ModuleType("app.models.schema")

    class User(BaseModel):
        username: str = "hung"

    schema_stub.User = User

    ocr_stub = types.ModuleType("app.services.ocr_service")

    class LlamaParseAsyncClient:
        def __init__(self, api_key: str):
            self.api_key = api_key

        async def parse_pdf_to_markdown(self, _path: str) -> str:
            raise AssertionError("external parser must not be called by unit tests")

    ocr_stub.LlamaParseAsyncClient = LlamaParseAsyncClient

    source_path = Path(__file__).resolve().parents[1] / "app" / "api" / "document.py"
    module_name = "_document_upload_under_test"
    spec = importlib.util.spec_from_file_location(module_name, source_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {source_path}")
    module = importlib.util.module_from_spec(spec)
    stubs = {
        "app.api.auth": auth_stub,
        "app.models.schema": schema_stub,
        "app.services.ocr_service": ocr_stub,
        module_name: module,
    }
    with patch.dict(sys.modules, stubs):
        spec.loader.exec_module(module)
    return module


document = _load_document_module()


class FakeUpload:
    def __init__(
        self,
        data: bytes = b"",
        *,
        filename: str = "document.pdf",
        content_type: str | None = "application/pdf",
    ):
        self.filename = filename
        self.content_type = content_type
        self._stream = io.BytesIO(data)
        self.seek_calls: list[int] = []
        self.read_calls = 0
        self.closed = False

    async def seek(self, offset: int) -> int:
        self.seek_calls.append(offset)
        return self._stream.seek(offset)

    async def read(self, size: int = -1) -> bytes:
        self.read_calls += 1
        return self._stream.read(size)

    async def close(self) -> None:
        self.closed = True
        self._stream.close()


class FilenameValidationTests(unittest.TestCase):
    def test_safe_pdf_filenames_are_accepted(self) -> None:
        for filename in (
            "document.pdf",
            "DOCUMENT.PDF",
            "Mức học phí 2026-2027.pdf",
            "context.pdf",
            "a" * 156 + ".pdf",
        ):
            with self.subTest(filename=filename):
                self.assertEqual(document._validate_pdf_filename(filename), filename)

    def test_path_traversal_and_absolute_paths_are_rejected(self) -> None:
        for filename in (
            "../evil.pdf",
            "..\\evil.pdf",
            "folder/evil.pdf",
            "folder\\evil.pdf",
            "C:\\temp\\evil.pdf",
            "/tmp/evil.pdf",
        ):
            with self.subTest(filename=filename):
                with self.assertRaises(HTTPException) as raised:
                    document._validate_pdf_filename(filename)
                self.assertEqual(raised.exception.status_code, 400)

    def test_invalid_extensions_characters_lengths_and_reserved_names_are_rejected(self) -> None:
        invalid_names = (
            None,
            "",
            ".",
            "..",
            "document.txt",
            "document.pdf.exe",
            "document?.pdf",
            "document\x00.pdf",
            "document.pdf ",
            "document.pdf.",
            "a" * 157 + ".pdf",
            "CON.pdf",
            "con.notes.pdf",
            "COM1.pdf",
            "lpt9.PDF",
            "NUL.pdf",
        )
        for filename in invalid_names:
            with self.subTest(filename=filename):
                with self.assertRaises(HTTPException) as raised:
                    document._validate_pdf_filename(filename)
                self.assertEqual(raised.exception.status_code, 400)


class MimeValidationTests(unittest.TestCase):
    def test_media_type_is_normalized_before_allowlist_check(self) -> None:
        cases = {
            "application/pdf": "application/pdf",
            " APPLICATION/PDF ; charset=binary": "application/pdf",
            "application/x-pdf": "application/x-pdf",
            "text/plain; charset=utf-8": "text/plain",
            None: "",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(document._normalise_media_type(raw), expected)

        self.assertIn(
            document._normalise_media_type("APPLICATION/PDF; charset=binary"),
            document.ALLOWED_PDF_MEDIA_TYPES,
        )
        self.assertNotIn(
            document._normalise_media_type("text/plain"),
            document.ALLOWED_PDF_MEDIA_TYPES,
        )


class PdfContentValidationTests(unittest.IsolatedAsyncioTestCase):
    async def test_exactly_five_mib_pdf_is_accepted(self) -> None:
        payload = b"%PDF-" + b"x" * (document.MAX_PDF_SIZE - 5)
        upload = FakeUpload(payload)
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "accepted.pdf"

            await document._save_validated_pdf(upload, destination)

            self.assertEqual(destination.stat().st_size, document.MAX_PDF_SIZE)
            self.assertEqual(destination.read_bytes()[:5], b"%PDF-")
            self.assertEqual(upload.seek_calls, [0])

    async def test_more_than_five_mib_is_rejected_with_413(self) -> None:
        payload = b"%PDF-" + b"x" * (document.MAX_PDF_SIZE - 4)
        upload = FakeUpload(payload)
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "oversized.pdf"

            with self.assertRaises(HTTPException) as raised:
                await document._save_validated_pdf(upload, destination)

            self.assertEqual(raised.exception.status_code, 413)
            self.assertLess(destination.stat().st_size, len(payload))

    async def test_forged_or_short_pdf_header_is_rejected_before_writing(self) -> None:
        for payload in (b"plain text", b"%PDF", b"", b"%pdf-1.7"):
            with self.subTest(payload=payload):
                upload = FakeUpload(payload)
                with tempfile.TemporaryDirectory() as temp_dir:
                    destination = Path(temp_dir) / "forged.pdf"
                    with self.assertRaises(HTTPException) as raised:
                        await document._save_validated_pdf(upload, destination)
                    self.assertEqual(raised.exception.status_code, 400)
                    self.assertFalse(destination.exists())


class EndpointInputValidationTests(unittest.IsolatedAsyncioTestCase):
    async def _call_upload(
        self,
        upload: FakeUpload,
        *,
        document_class: str,
        academic_year: str | None,
    ):
        return await document.upload_document(
            request=SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace())),
            file=upload,
            document_class=document_class,
            academic_year=academic_year,
            _admin=SimpleNamespace(username="hung"),
        )

    async def test_invalid_document_class_and_academic_year_return_422(self) -> None:
        cases = (
            ("unknown", None),
            ("tuition_actual_rate", None),
            ("tuition_exemption_basis", "2025-2027"),
            ("tuition_actual_rate", "2026/2027"),
        )
        for document_class, academic_year in cases:
            with self.subTest(
                document_class=document_class, academic_year=academic_year
            ):
                upload = FakeUpload(filename="document.pdf")
                with self.assertRaises(HTTPException) as raised:
                    await self._call_upload(
                        upload,
                        document_class=document_class,
                        academic_year=academic_year,
                    )
                self.assertEqual(raised.exception.status_code, 422)
                self.assertEqual(upload.read_calls, 0)
                self.assertTrue(upload.closed)

    async def test_valid_class_with_disallowed_mime_returns_415_before_reading(self) -> None:
        upload = FakeUpload(filename="document.pdf", content_type="text/plain")

        with self.assertRaises(HTTPException) as raised:
            await self._call_upload(
                upload,
                document_class="scholarship",
                academic_year=None,
            )

        self.assertEqual(raised.exception.status_code, 415)
        self.assertEqual(upload.read_calls, 0)
        self.assertTrue(upload.closed)

    async def test_path_traversal_filename_returns_400_before_other_work(self) -> None:
        upload = FakeUpload(filename="../document.pdf")

        with self.assertRaises(HTTPException) as raised:
            await self._call_upload(
                upload,
                document_class="scholarship",
                academic_year=None,
            )

        self.assertEqual(raised.exception.status_code, 400)
        self.assertEqual(upload.read_calls, 0)
        self.assertTrue(upload.closed)


class UploadTransactionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_root = Path(self.temp_dir.name) / "data"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    async def _run_pipeline(
        self,
        *,
        ingest_result: bool,
        move_error: Exception | None = None,
    ) -> SimpleNamespace:
        upload = FakeUpload(
            b"%PDF-1.7\ntransaction-test",
            filename="document.pdf",
            content_type="application/pdf",
        )
        parser = SimpleNamespace(
            parse_pdf_to_markdown=AsyncMock(return_value="# Parsed document\n")
        )
        parser_class = MagicMock(return_value=parser)
        clean_mock = MagicMock()

        metadata_payload = {
            "domain": "tuition",
            "content_kind": "rate_table",
            "fee_kind": "actual_tuition",
            "academic_year": "2026-2027",
            "status": "active",
            "original_filename": "document.pdf",
            "uploaded_by": "hung",
            "uploaded_at": "2026-07-17T00:00:00+00:00",
        }
        metadata_entry = MagicMock()
        metadata_entry.as_dict.return_value = metadata_payload
        catalog = MagicMock()
        catalog.add_uploaded_document.return_value = metadata_entry

        engine = MagicMock()
        engine.ingest_markdown_document.return_value = ingest_result
        request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(engine=engine)))

        def successful_move(source: Path, destination: Path) -> None:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())
            source.unlink()

        move_mock = MagicMock(
            side_effect=move_error if move_error is not None else successful_move
        )
        log_exception_mock = MagicMock()
        uuid_mock = MagicMock(
            side_effect=(
                SimpleNamespace(hex="ingest-run-123"),
                SimpleNamespace(hex="input-file-456"),
            )
        )

        response = None
        error = None
        with (
            patch.object(document, "DATA_ROOT", self.data_root),
            patch.dict(document.os.environ, {"LLAMA_CLOUD_API_KEY": "test-key"}),
            patch.object(document, "uuid4", uuid_mock),
            patch.object(document, "LlamaParseAsyncClient", parser_class),
            patch.object(document, "clean_markdown_file", clean_mock),
            patch.object(document.logger, "exception", log_exception_mock),
            patch.object(
                document.DocumentMetadataCatalog,
                "load",
                return_value=catalog,
            ),
            patch.object(document, "_move_without_overwrite", move_mock),
        ):
            try:
                response = await document.upload_document(
                    request=request,
                    file=upload,
                    document_class="tuition_actual_rate",
                    academic_year="2026-2027",
                    _admin=SimpleNamespace(username="hung"),
                )
            except HTTPException as exc:
                error = exc

        return SimpleNamespace(
            response=response,
            error=error,
            upload=upload,
            parser=parser,
            parser_class=parser_class,
            clean=clean_mock,
            catalog=catalog,
            engine=engine,
            move=move_mock,
            log_exception=log_exception_mock,
            uuid=uuid_mock,
            metadata=metadata_payload,
            markdown_path=self.data_root / "markdown" / "document.md",
            input_path=self.data_root / "input" / "input-file-456.pdf",
            done_path=self.data_root / "done" / "document.pdf",
        )

    async def test_success_passes_ingest_run_id_and_returns_source_metadata(self) -> None:
        result = await self._run_pipeline(ingest_result=True)

        self.assertIsNone(result.error)
        self.assertEqual(result.response["status"], "success")
        self.assertEqual(result.response["source"], "document.md")
        self.assertEqual(result.response["metadata"], result.metadata)
        result.engine.ingest_markdown_document.assert_called_once_with(
            str(result.markdown_path),
            ingest_run_id="ingest-run-123",
        )
        result.engine.purge_document.assert_not_called()
        result.catalog.remove_uploaded_document.assert_not_called()
        result.catalog.add_uploaded_document.assert_called_once_with(
            source="document.md",
            document_class="tuition_actual_rate",
            academic_year="2026-2027",
            original_filename="document.pdf",
            uploaded_by="hung",
        )
        result.parser.parse_pdf_to_markdown.assert_awaited_once_with(
            str(result.input_path)
        )
        result.clean.assert_called_once_with(result.markdown_path)
        result.move.assert_called_once_with(result.input_path, result.done_path)
        self.assertTrue(result.markdown_path.exists())
        self.assertTrue(result.done_path.exists())
        self.assertFalse(result.input_path.exists())
        self.assertTrue(result.upload.closed)

    async def test_partial_ingest_failure_purges_same_run_and_removes_artifacts(self) -> None:
        result = await self._run_pipeline(ingest_result=False)

        self.assertIsNotNone(result.error)
        self.assertEqual(result.error.status_code, 500)
        result.engine.ingest_markdown_document.assert_called_once_with(
            str(result.markdown_path),
            ingest_run_id="ingest-run-123",
        )
        result.engine.purge_document.assert_called_once_with(
            "document.md",
            ingest_run_id="ingest-run-123",
        )
        result.catalog.remove_uploaded_document.assert_called_once_with(
            "document.md",
            missing_ok=True,
        )
        result.move.assert_not_called()
        result.log_exception.assert_not_called()
        self.assertFalse(result.markdown_path.exists())
        self.assertFalse(result.input_path.exists())
        self.assertFalse(result.done_path.exists())
        self.assertTrue(result.upload.closed)

    async def test_pdf_move_failure_after_ingest_rolls_back_everything(self) -> None:
        result = await self._run_pipeline(
            ingest_result=True,
            move_error=OSError("disk write failed"),
        )

        self.assertIsNotNone(result.error)
        self.assertEqual(result.error.status_code, 500)
        result.log_exception.assert_called_once()
        result.move.assert_called_once_with(result.input_path, result.done_path)
        result.engine.purge_document.assert_called_once_with(
            "document.md",
            ingest_run_id="ingest-run-123",
        )
        result.catalog.remove_uploaded_document.assert_called_once_with(
            "document.md",
            missing_ok=True,
        )
        self.assertFalse(result.markdown_path.exists())
        self.assertFalse(result.input_path.exists())
        self.assertFalse(result.done_path.exists())
        self.assertTrue(result.upload.closed)


if __name__ == "__main__":
    unittest.main()
