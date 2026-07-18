from __future__ import annotations

import json
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from app.services import document_metadata as metadata_module
from app.services.document_metadata import (
    DEFAULT_MANIFEST_PATH,
    DEFAULT_MARKDOWN_DIR,
    INITIAL_CORPUS_SOURCE_COUNT,
    ContentKind,
    DocumentAlreadyExistsError,
    DocumentClass,
    DocumentMetadata,
    DocumentMetadataCatalog,
    Domain,
    FeeKind,
    MetadataCatalogError,
    MetadataStatus,
    StaticDocumentRemovalError,
    get_document_metadata,
    normalize_document_class,
    validate_catalog,
)


def _metadata(
    *,
    domain: str = "other",
    content_kind: str = "other",
    fee_kind: str = "not_applicable",
    academic_year: str | None = None,
    status: str = "active",
) -> dict[str, object]:
    return {
        "domain": domain,
        "content_kind": content_kind,
        "fee_kind": fee_kind,
        "academic_year": academic_year,
        "status": status,
    }


def _write_manifest(path: Path, documents: dict[str, dict[str, object]]) -> None:
    path.write_text(
        json.dumps(
            {"schema_version": 1, "documents": documents},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


class CanonicalManifestTests(unittest.TestCase):
    def test_real_manifest_exactly_covers_current_corpus(self) -> None:
        report = validate_catalog(DEFAULT_MARKDOWN_DIR, DEFAULT_MANIFEST_PATH)

        self.assertTrue(report.valid, report.model_dump())
        self.assertEqual(report.manifest_count, INITIAL_CORPUS_SOURCE_COUNT)
        self.assertEqual(report.markdown_count, INITIAL_CORPUS_SOURCE_COUNT)
        self.assertEqual(report.missing_entries, ())
        self.assertEqual(report.orphan_entries, ())

    def test_tuition_sources_have_the_locked_business_classification(self) -> None:
        actual_sources = {
            "MucHocPhi_ChatLuongCao_TienTien.md",
            "MucHocPhi_DaiHocChinhQuy_Khoa51_VeTruoc.md",
            "MucHocPhi_DaiHocChinhQuy_Khoa52.md",
            "MucHocPhi_QuyDinhChung.md",
        }
        for source in actual_sources:
            with self.subTest(source=source):
                payload = get_document_metadata(source)
                self.assertEqual(payload["domain"], "tuition")
                self.assertEqual(payload["content_kind"], "rate_table")
                self.assertEqual(payload["fee_kind"], "actual_tuition")
                self.assertEqual(payload["academic_year"], "2026-2027")

        exemption_basis = get_document_metadata("MucHocPhi_2526_MienGiam.md")
        self.assertEqual(exemption_basis["fee_kind"], "exemption_basis")
        self.assertEqual(exemption_basis["academic_year"], "2025-2026")

        exemption_policy = get_document_metadata("mghp.md")
        self.assertEqual(exemption_policy["content_kind"], "exemption_policy")
        self.assertEqual(exemption_policy["fee_kind"], "not_applicable")

    def test_special_backfill_groups_are_not_misclassified(self) -> None:
        self.assertEqual(
            get_document_metadata("Tài liệu phân bổ quỹ học bổng.md")["domain"],
            "scholarship",
        )
        self.assertEqual(
            get_document_metadata("VayVonChoSVSuPham.md")["domain"],
            "social_support",
        )
        self.assertEqual(
            get_document_metadata("QD_2022.md")["domain"], "student_loan"
        )
        for source in ("03_6175KHTH_10-12-2024.md", "3hk.md", "SoTay.md"):
            with self.subTest(source=source):
                self.assertEqual(get_document_metadata(source)["domain"], "other")


class MetadataValidationTests(unittest.TestCase):
    def test_all_document_classes_have_a_fixed_server_mapping(self) -> None:
        expected = {
            DocumentClass.TUITION_ACTUAL_RATE: (
                "tuition",
                "rate_table",
                "actual_tuition",
            ),
            DocumentClass.TUITION_EXEMPTION_BASIS: (
                "tuition",
                "rate_table",
                "exemption_basis",
            ),
            DocumentClass.TUITION_EXEMPTION_POLICY: (
                "tuition",
                "exemption_policy",
                "not_applicable",
            ),
            DocumentClass.SCHOLARSHIP: ("scholarship", "other", "not_applicable"),
            DocumentClass.STUDENT_LOAN: ("student_loan", "other", "not_applicable"),
            DocumentClass.SOCIAL_SUPPORT: (
                "social_support",
                "other",
                "not_applicable",
            ),
            DocumentClass.OTHER: ("other", "other", "not_applicable"),
        }

        for document_class, classification in expected.items():
            year = (
                "2026-2027"
                if document_class
                in {
                    DocumentClass.TUITION_ACTUAL_RATE,
                    DocumentClass.TUITION_EXEMPTION_BASIS,
                }
                else None
            )
            with self.subTest(document_class=document_class):
                payload = normalize_document_class(document_class, year)
                self.assertEqual(
                    (
                        payload["domain"],
                        payload["content_kind"],
                        payload["fee_kind"],
                    ),
                    classification,
                )
                self.assertEqual(payload["status"], "active")

    def test_tuition_rate_requires_a_consecutive_academic_year(self) -> None:
        for invalid_year in (None, "", "2026", "2026/2027", "2026-2028"):
            with self.subTest(invalid_year=invalid_year):
                with self.assertRaises(ValueError):
                    normalize_document_class("tuition_actual_rate", invalid_year)

    def test_invalid_document_class_is_rejected(self) -> None:
        with self.assertRaisesRegex(MetadataCatalogError, "unsupported document_class"):
            normalize_document_class("tuition_guess", "2026-2027")

    def test_invalid_cross_field_combinations_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            DocumentMetadata(
                domain=Domain.SCHOLARSHIP,
                content_kind=ContentKind.RATE_TABLE,
                fee_kind=FeeKind.ACTUAL_TUITION,
                academic_year="2026-2027",
                status=MetadataStatus.ACTIVE,
            )
        with self.assertRaises(ValueError):
            DocumentMetadata(
                domain=Domain.TUITION,
                content_kind=ContentKind.EXEMPTION_POLICY,
                fee_kind=FeeKind.EXEMPTION_BASIS,
                academic_year="2025-2026",
                status=MetadataStatus.ACTIVE,
            )

    def test_upload_audit_fields_are_all_or_none_and_timezone_aware(self) -> None:
        common = {
            "domain": Domain.OTHER,
            "content_kind": ContentKind.OTHER,
            "fee_kind": FeeKind.NOT_APPLICABLE,
            "academic_year": None,
            "status": MetadataStatus.ACTIVE,
        }
        with self.assertRaises(ValueError):
            DocumentMetadata(**common, original_filename="document.pdf")
        with self.assertRaises(ValueError):
            DocumentMetadata(
                **common,
                original_filename="document.pdf",
                uploaded_by="hung",
                uploaded_at=datetime(2026, 7, 17, 12, 0),
            )


class PreflightTests(unittest.TestCase):
    def test_preflight_reports_missing_orphan_and_invalid_utf8_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            markdown_dir = root / "markdown"
            markdown_dir.mkdir()
            (markdown_dir / "present.md").write_text("valid", encoding="utf-8")
            (markdown_dir / "missing.md").write_text("valid", encoding="utf-8")
            (markdown_dir / "corrupt.md").write_bytes(b"\xff\xfe")
            manifest_path = root / "document_metadata.json"
            _write_manifest(
                manifest_path,
                {
                    "present.md": _metadata(),
                    "orphan.md": _metadata(),
                    "corrupt.md": _metadata(),
                },
            )

            report = validate_catalog(markdown_dir, manifest_path)

            self.assertFalse(report.valid)
            self.assertEqual(report.missing_entries, ("missing.md",))
            self.assertEqual(report.orphan_entries, ("orphan.md",))
            self.assertEqual(report.invalid_utf8_files, ("corrupt.md",))
            with self.assertRaises(MetadataCatalogError):
                report.raise_for_errors()

    def test_preflight_reports_invalid_manifest_instead_of_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            markdown_dir = root / "markdown"
            markdown_dir.mkdir()
            (markdown_dir / "rate.md").write_text("valid", encoding="utf-8")
            manifest_path = root / "document_metadata.json"
            _write_manifest(
                manifest_path,
                {
                    "rate.md": _metadata(
                        domain="tuition",
                        content_kind="rate_table",
                        fee_kind="actual_tuition",
                        academic_year="2026-2028",
                    )
                },
            )

            report = validate_catalog(markdown_dir, manifest_path)

            self.assertFalse(report.valid)
            self.assertEqual(report.manifest_count, 0)
            self.assertTrue(report.manifest_errors)
            self.assertIn("academic_year", report.manifest_errors[0])

    def test_duplicate_json_keys_are_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            markdown_dir = root / "markdown"
            markdown_dir.mkdir()
            manifest_path = root / "document_metadata.json"
            manifest_path.write_text(
                '{"schema_version": 1, "schema_version": 1, "documents": {}}',
                encoding="utf-8",
            )

            report = validate_catalog(markdown_dir, manifest_path)

            self.assertFalse(report.valid)
            self.assertIn("duplicate JSON key", report.manifest_errors[0])


class AtomicCatalogMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.manifest_path = self.root / "document_metadata.json"
        _write_manifest(self.manifest_path, {})

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_add_and_remove_uploaded_document_are_atomic(self) -> None:
        catalog = DocumentMetadataCatalog.load(self.manifest_path)
        uploaded_at = datetime(2026, 7, 17, 5, 30, tzinfo=timezone.utc)
        real_replace = os.replace
        replace_calls: list[tuple[Path, Path]] = []

        def observed_replace(source: str | os.PathLike[str], target: str | os.PathLike[str]) -> None:
            replace_calls.append((Path(source), Path(target)))
            real_replace(source, target)

        with patch.object(metadata_module.os, "replace", side_effect=observed_replace):
            created = catalog.add_uploaded_document(
                source="uploaded.md",
                document_class="tuition_exemption_basis",
                academic_year="2025-2026",
                original_filename="uploaded.pdf",
                uploaded_by="hung",
                uploaded_at=uploaded_at,
            )

        self.assertEqual(created.status, MetadataStatus.ACTIVE)
        self.assertEqual(created.uploaded_by, "hung")
        self.assertEqual(created.uploaded_at, uploaded_at)
        self.assertEqual(len(replace_calls), 1)
        self.assertEqual(replace_calls[0][0].parent, replace_calls[0][1].parent)
        self.assertTrue(os.path.samefile(replace_calls[0][1], self.manifest_path))
        self.assertFalse(list(self.root.glob("*.tmp")))

        persisted = DocumentMetadataCatalog.load(self.manifest_path)
        self.assertEqual(persisted.get("uploaded.md"), created)
        removed = persisted.remove_document("uploaded.md")
        self.assertEqual(removed, created)
        self.assertEqual(DocumentMetadataCatalog.load(self.manifest_path).sources, ())

    def test_duplicate_and_path_traversal_sources_are_rejected(self) -> None:
        catalog = DocumentMetadataCatalog.load(self.manifest_path)
        kwargs = {
            "document_class": "scholarship",
            "academic_year": None,
            "original_filename": "document.pdf",
            "uploaded_by": "hung",
        }
        catalog.add_uploaded_document(source="document.md", **kwargs)
        with self.assertRaises(DocumentAlreadyExistsError):
            catalog.add_uploaded_document(source="DOCUMENT.md", **kwargs)
        with self.assertRaises(ValueError):
            catalog.add_uploaded_document(source="../document.md", **kwargs)

    def test_static_entries_cannot_be_removed_by_upload_rollback_api(self) -> None:
        _write_manifest(self.manifest_path, {"static.md": _metadata()})
        catalog = DocumentMetadataCatalog.load(self.manifest_path)

        with self.assertRaises(StaticDocumentRemovalError):
            catalog.remove_document("static.md")

    def test_concurrent_additions_do_not_overwrite_each_other(self) -> None:
        def add(source: str) -> None:
            DocumentMetadataCatalog.load(self.manifest_path).add_uploaded_document(
                source=source,
                document_class="scholarship",
                academic_year=None,
                original_filename=source.removesuffix(".md") + ".pdf",
                uploaded_by="hung",
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(add, source) for source in ("a.md", "b.md")]
            for future in futures:
                future.result()

        self.assertEqual(
            DocumentMetadataCatalog.load(self.manifest_path).sources, ("a.md", "b.md")
        )


if __name__ == "__main__":
    unittest.main()
