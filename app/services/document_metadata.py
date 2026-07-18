"""Canonical business metadata for documents in the RAG corpus.

The JSON manifest owned by this module is deliberately independent from the
technical metadata produced while indexing (checksum, ingest run, timestamps,
and so on).  It is the source of truth for business filters such as
``fee_kind=actual_tuition``.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Literal, TypeVar

import portalocker
from pydantic import BaseModel, ConfigDict, field_validator, model_validator


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "data" / "document_metadata.json"
DEFAULT_MARKDOWN_DIR = PROJECT_ROOT / "data" / "markdown"
METADATA_SCHEMA_VERSION = 1
INITIAL_CORPUS_SOURCE_COUNT = 46

_ACADEMIC_YEAR_PATTERN = re.compile(r"^(?P<start>\d{4})-(?P<end>\d{4})$")
_T = TypeVar("_T")


class Domain(str, Enum):
    TUITION = "tuition"
    SCHOLARSHIP = "scholarship"
    STUDENT_LOAN = "student_loan"
    SOCIAL_SUPPORT = "social_support"
    OTHER = "other"


class ContentKind(str, Enum):
    RATE_TABLE = "rate_table"
    EXEMPTION_POLICY = "exemption_policy"
    POLICY = "policy"
    PROCEDURE = "procedure"
    ANNOUNCEMENT = "announcement"
    FORM = "form"
    OTHER = "other"


class FeeKind(str, Enum):
    ACTUAL_TUITION = "actual_tuition"
    EXEMPTION_BASIS = "exemption_basis"
    NOT_APPLICABLE = "not_applicable"


class MetadataStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class DocumentClass(str, Enum):
    TUITION_ACTUAL_RATE = "tuition_actual_rate"
    TUITION_EXEMPTION_BASIS = "tuition_exemption_basis"
    TUITION_EXEMPTION_POLICY = "tuition_exemption_policy"
    SCHOLARSHIP = "scholarship"
    STUDENT_LOAN = "student_loan"
    SOCIAL_SUPPORT = "social_support"
    OTHER = "other"


class MetadataCatalogError(ValueError):
    """Base error for catalog validation or mutation failures."""


class DocumentAlreadyExistsError(MetadataCatalogError):
    pass


class DocumentNotFoundError(MetadataCatalogError):
    pass


class StaticDocumentRemovalError(MetadataCatalogError):
    pass


class DuplicateJsonKeyError(MetadataCatalogError):
    pass


def _validate_source_name(source: str) -> str:
    if not isinstance(source, str) or not source:
        raise ValueError("source must be a non-empty string")
    if source != source.strip():
        raise ValueError("source must not contain surrounding whitespace")
    if "\x00" in source or "/" in source or "\\" in source:
        raise ValueError("source must be a Markdown basename, not a path")
    if source in {".", ".."} or not source.casefold().endswith(".md"):
        raise ValueError("source must be a .md basename")
    return source


def _validate_original_filename(filename: str) -> str:
    if not isinstance(filename, str) or not filename:
        raise ValueError("original_filename must be a non-empty string")
    if filename != filename.strip():
        raise ValueError("original_filename must not contain surrounding whitespace")
    if "\x00" in filename or "/" in filename or "\\" in filename:
        raise ValueError("original_filename must be a basename, not a path")
    if filename in {".", ".."}:
        raise ValueError("original_filename is invalid")
    return filename


class DocumentMetadata(BaseModel):
    """Validated business metadata for one Markdown source."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    domain: Domain
    content_kind: ContentKind
    fee_kind: FeeKind
    academic_year: str | None
    status: MetadataStatus
    original_filename: str | None = None
    uploaded_by: str | None = None
    uploaded_at: datetime | None = None

    @field_validator("academic_year")
    @classmethod
    def validate_academic_year(cls, value: str | None) -> str | None:
        if value is None:
            return None
        match = _ACADEMIC_YEAR_PATTERN.fullmatch(value)
        if not match:
            raise ValueError("academic_year must use YYYY-YYYY format")
        start = int(match.group("start"))
        end = int(match.group("end"))
        if end != start + 1:
            raise ValueError("academic_year end year must equal start year + 1")
        return value

    @field_validator("original_filename")
    @classmethod
    def validate_original_filename(cls, value: str | None) -> str | None:
        return None if value is None else _validate_original_filename(value)

    @field_validator("uploaded_by")
    @classmethod
    def validate_uploaded_by(cls, value: str | None) -> str | None:
        if value is not None and not value:
            raise ValueError("uploaded_by must not be empty")
        return value

    @field_validator("uploaded_at")
    @classmethod
    def validate_uploaded_at(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("uploaded_at must include a timezone")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_business_rules(self) -> "DocumentMetadata":
        is_tuition_rate = self.fee_kind in {
            FeeKind.ACTUAL_TUITION,
            FeeKind.EXEMPTION_BASIS,
        }
        if is_tuition_rate:
            if self.domain is not Domain.TUITION:
                raise ValueError("tuition fee kinds require domain=tuition")
            if self.content_kind is not ContentKind.RATE_TABLE:
                raise ValueError("tuition fee kinds require content_kind=rate_table")
            if self.academic_year is None:
                raise ValueError("tuition rate tables require academic_year")
        elif self.domain is not Domain.TUITION and self.fee_kind is not FeeKind.NOT_APPLICABLE:
            raise ValueError("non-tuition documents require fee_kind=not_applicable")

        if self.domain is Domain.TUITION and self.content_kind is ContentKind.RATE_TABLE:
            if not is_tuition_rate:
                raise ValueError("tuition rate tables require a concrete fee_kind")

        if self.content_kind is ContentKind.EXEMPTION_POLICY:
            if self.domain is not Domain.TUITION or self.fee_kind is not FeeKind.NOT_APPLICABLE:
                raise ValueError(
                    "exemption_policy requires domain=tuition and fee_kind=not_applicable"
                )

        audit_values = (self.original_filename, self.uploaded_by, self.uploaded_at)
        if any(value is not None for value in audit_values) and not all(
            value is not None for value in audit_values
        ):
            raise ValueError(
                "original_filename, uploaded_by and uploaded_at must be provided together"
            )
        return self

    def as_dict(self) -> dict[str, Any]:
        """Return normalized JSON-compatible metadata for Qdrant/JSONB."""

        result: dict[str, Any] = {
            "domain": self.domain.value,
            "content_kind": self.content_kind.value,
            "fee_kind": self.fee_kind.value,
            "academic_year": self.academic_year,
            "status": self.status.value,
        }
        if self.original_filename is not None:
            result.update(
                {
                    "original_filename": self.original_filename,
                    "uploaded_by": self.uploaded_by,
                    "uploaded_at": self.uploaded_at.isoformat(),
                }
            )
        return result


class DocumentMetadataManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[METADATA_SCHEMA_VERSION]
    documents: dict[str, DocumentMetadata]

    @field_validator("documents")
    @classmethod
    def validate_document_sources(
        cls, documents: dict[str, DocumentMetadata]
    ) -> dict[str, DocumentMetadata]:
        casefolded: dict[str, str] = {}
        for source in documents:
            _validate_source_name(source)
            folded = source.casefold()
            previous = casefolded.get(folded)
            if previous is not None:
                raise ValueError(
                    f"document sources differ only by case: {previous!r} and {source!r}"
                )
            casefolded[folded] = source
        return documents


class CatalogPreflightReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    valid: bool
    manifest_path: str
    markdown_dir: str
    manifest_count: int
    markdown_count: int
    missing_entries: tuple[str, ...] = ()
    orphan_entries: tuple[str, ...] = ()
    invalid_utf8_files: tuple[str, ...] = ()
    manifest_errors: tuple[str, ...] = ()
    filesystem_errors: tuple[str, ...] = ()

    def raise_for_errors(self) -> None:
        if not self.valid:
            details = "; ".join(
                [
                    *(f"missing metadata: {name}" for name in self.missing_entries),
                    *(f"orphan metadata: {name}" for name in self.orphan_entries),
                    *(f"invalid UTF-8: {name}" for name in self.invalid_utf8_files),
                    *self.manifest_errors,
                    *self.filesystem_errors,
                ]
            )
            raise MetadataCatalogError(f"metadata catalog preflight failed: {details}")


DOCUMENT_CLASS_MAPPING = MappingProxyType(
    {
        DocumentClass.TUITION_ACTUAL_RATE: (
            Domain.TUITION,
            ContentKind.RATE_TABLE,
            FeeKind.ACTUAL_TUITION,
        ),
        DocumentClass.TUITION_EXEMPTION_BASIS: (
            Domain.TUITION,
            ContentKind.RATE_TABLE,
            FeeKind.EXEMPTION_BASIS,
        ),
        DocumentClass.TUITION_EXEMPTION_POLICY: (
            Domain.TUITION,
            ContentKind.EXEMPTION_POLICY,
            FeeKind.NOT_APPLICABLE,
        ),
        DocumentClass.SCHOLARSHIP: (
            Domain.SCHOLARSHIP,
            ContentKind.OTHER,
            FeeKind.NOT_APPLICABLE,
        ),
        DocumentClass.STUDENT_LOAN: (
            Domain.STUDENT_LOAN,
            ContentKind.OTHER,
            FeeKind.NOT_APPLICABLE,
        ),
        DocumentClass.SOCIAL_SUPPORT: (
            Domain.SOCIAL_SUPPORT,
            ContentKind.OTHER,
            FeeKind.NOT_APPLICABLE,
        ),
        DocumentClass.OTHER: (
            Domain.OTHER,
            ContentKind.OTHER,
            FeeKind.NOT_APPLICABLE,
        ),
    }
)


def normalize_document_class(
    document_class: str | DocumentClass,
    academic_year: str | None = None,
) -> dict[str, Any]:
    """Map the upload form's class to server-owned normalized metadata."""

    try:
        normalized_class = DocumentClass(document_class)
    except (TypeError, ValueError) as exc:
        allowed = ", ".join(item.value for item in DocumentClass)
        raise MetadataCatalogError(
            f"unsupported document_class {document_class!r}; expected one of: {allowed}"
        ) from exc

    if academic_year == "":
        academic_year = None
    domain, content_kind, fee_kind = DOCUMENT_CLASS_MAPPING[normalized_class]
    metadata = DocumentMetadata(
        domain=domain,
        content_kind=content_kind,
        fee_kind=fee_kind,
        academic_year=academic_year,
        status=MetadataStatus.ACTIVE,
    )
    return metadata.as_dict()


def _object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKeyError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _read_manifest(path: Path) -> DocumentMetadataManifest:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise MetadataCatalogError(f"cannot read metadata manifest {path}: {exc}") from exc
    try:
        raw_data = json.loads(raw_text, object_pairs_hook=_object_without_duplicate_keys)
    except (json.JSONDecodeError, DuplicateJsonKeyError) as exc:
        raise MetadataCatalogError(f"invalid metadata manifest JSON {path}: {exc}") from exc
    try:
        return DocumentMetadataManifest.model_validate(raw_data)
    except ValueError as exc:
        raise MetadataCatalogError(f"invalid metadata manifest {path}: {exc}") from exc


def _manifest_json(manifest: DocumentMetadataManifest) -> str:
    documents = {
        source: metadata.as_dict()
        for source, metadata in sorted(manifest.documents.items(), key=lambda item: item[0].casefold())
    }
    payload = {
        "schema_version": manifest.schema_version,
        "documents": documents,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _atomic_write_manifest(path: Path, manifest: DocumentMetadataManifest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(_manifest_json(manifest))
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def _scan_markdown_directory(
    markdown_dir: Path,
) -> tuple[set[str], tuple[str, ...], tuple[str, ...]]:
    if not markdown_dir.exists():
        return set(), (), (f"Markdown directory does not exist: {markdown_dir}",)
    if not markdown_dir.is_dir():
        return set(), (), (f"Markdown path is not a directory: {markdown_dir}",)

    sources: set[str] = set()
    invalid_utf8: list[str] = []
    filesystem_errors: list[str] = []
    try:
        candidates = sorted(
            (
                entry
                for entry in markdown_dir.iterdir()
                if entry.is_file() and entry.suffix.casefold() == ".md"
            ),
            key=lambda entry: entry.name.casefold(),
        )
    except OSError as exc:
        return set(), (), (f"cannot list Markdown directory {markdown_dir}: {exc}",)

    for path in candidates:
        sources.add(path.name)
        try:
            path.read_text(encoding="utf-8")
        except UnicodeError:
            invalid_utf8.append(path.name)
        except OSError as exc:
            filesystem_errors.append(f"cannot read {path.name}: {exc}")
    return sources, tuple(invalid_utf8), tuple(filesystem_errors)


class DocumentMetadataCatalog:
    """Read and atomically mutate the canonical document metadata manifest."""

    def __init__(self, manifest_path: Path, manifest: DocumentMetadataManifest):
        self.manifest_path = manifest_path
        self._manifest = manifest

    @classmethod
    def load(
        cls, manifest_path: str | Path | None = None
    ) -> "DocumentMetadataCatalog":
        path = Path(manifest_path or DEFAULT_MANIFEST_PATH).resolve()
        return cls(path, _read_manifest(path))

    @property
    def schema_version(self) -> int:
        return self._manifest.schema_version

    @property
    def sources(self) -> tuple[str, ...]:
        return tuple(sorted(self._manifest.documents, key=str.casefold))

    def reload(self) -> "DocumentMetadataCatalog":
        self._manifest = _read_manifest(self.manifest_path)
        return self

    def get(self, source: str) -> DocumentMetadata:
        source = _validate_source_name(source)
        try:
            return self._manifest.documents[source]
        except KeyError as exc:
            raise DocumentNotFoundError(f"metadata not found for source {source!r}") from exc

    def get_payload(self, source: str) -> dict[str, Any]:
        return self.get(source).as_dict()

    def preflight(
        self, markdown_dir: str | Path = DEFAULT_MARKDOWN_DIR
    ) -> CatalogPreflightReport:
        directory = Path(markdown_dir).resolve()
        markdown_sources, invalid_utf8, filesystem_errors = _scan_markdown_directory(
            directory
        )
        manifest_sources = set(self._manifest.documents)
        missing = tuple(sorted(markdown_sources - manifest_sources, key=str.casefold))
        orphan = tuple(sorted(manifest_sources - markdown_sources, key=str.casefold))
        valid = not (missing or orphan or invalid_utf8 or filesystem_errors)
        return CatalogPreflightReport(
            valid=valid,
            manifest_path=str(self.manifest_path),
            markdown_dir=str(directory),
            manifest_count=len(manifest_sources),
            markdown_count=len(markdown_sources),
            missing_entries=missing,
            orphan_entries=orphan,
            invalid_utf8_files=invalid_utf8,
            filesystem_errors=filesystem_errors,
        )

    def _mutate(
        self,
        mutation: Callable[
            [dict[str, DocumentMetadata]], tuple[dict[str, DocumentMetadata], _T]
        ],
    ) -> _T:
        lock_path = self.manifest_path.with_name(self.manifest_path.name + ".lock")
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with portalocker.Lock(
            str(lock_path), mode="a+", encoding="utf-8", timeout=10
        ):
            current = _read_manifest(self.manifest_path)
            documents, result = mutation(dict(current.documents))
            updated = DocumentMetadataManifest(
                schema_version=METADATA_SCHEMA_VERSION,
                documents=documents,
            )
            _atomic_write_manifest(self.manifest_path, updated)
            self._manifest = updated
            return result

    def add_uploaded_document(
        self,
        *,
        source: str,
        document_class: str | DocumentClass,
        academic_year: str | None,
        original_filename: str,
        uploaded_by: str,
        uploaded_at: datetime | None = None,
    ) -> DocumentMetadata:
        source = _validate_source_name(source)
        original_filename = _validate_original_filename(original_filename)
        normalized = normalize_document_class(document_class, academic_year)
        metadata = DocumentMetadata(
            **normalized,
            original_filename=original_filename,
            uploaded_by=uploaded_by,
            uploaded_at=uploaded_at or datetime.now(timezone.utc),
        )

        def add(
            documents: dict[str, DocumentMetadata],
        ) -> tuple[dict[str, DocumentMetadata], DocumentMetadata]:
            existing = {name.casefold(): name for name in documents}
            if source.casefold() in existing:
                raise DocumentAlreadyExistsError(
                    f"metadata already exists for source {existing[source.casefold()]!r}"
                )
            documents[source] = metadata
            return documents, metadata

        return self._mutate(add)

    def remove_uploaded_document(
        self, source: str, *, missing_ok: bool = False
    ) -> DocumentMetadata | None:
        source = _validate_source_name(source)

        def remove(
            documents: dict[str, DocumentMetadata],
        ) -> tuple[dict[str, DocumentMetadata], DocumentMetadata | None]:
            metadata = documents.get(source)
            if metadata is None:
                if missing_ok:
                    return documents, None
                raise DocumentNotFoundError(f"metadata not found for source {source!r}")
            if metadata.uploaded_at is None:
                raise StaticDocumentRemovalError(
                    f"source {source!r} is part of the static catalog"
                )
            del documents[source]
            return documents, metadata

        return self._mutate(remove)

    def remove_document(
        self, source: str, *, missing_ok: bool = False
    ) -> DocumentMetadata | None:
        """Backward-compatible name for upload rollback/removal."""

        return self.remove_uploaded_document(source, missing_ok=missing_ok)


def load_catalog(
    catalog_path: str | Path | None = None,
) -> DocumentMetadataCatalog:
    return DocumentMetadataCatalog.load(catalog_path)


def get_document_metadata(
    source: str, catalog_path: str | Path | None = None
) -> dict[str, Any]:
    return load_catalog(catalog_path).get_payload(source)


def validate_catalog(
    md_dir: str | Path = DEFAULT_MARKDOWN_DIR,
    catalog_path: str | Path | None = None,
) -> CatalogPreflightReport:
    path = Path(catalog_path or DEFAULT_MANIFEST_PATH).resolve()
    directory = Path(md_dir).resolve()
    markdown_sources, invalid_utf8, filesystem_errors = _scan_markdown_directory(
        directory
    )
    try:
        catalog = DocumentMetadataCatalog.load(path)
    except MetadataCatalogError as exc:
        return CatalogPreflightReport(
            valid=False,
            manifest_path=str(path),
            markdown_dir=str(directory),
            manifest_count=0,
            markdown_count=len(markdown_sources),
            invalid_utf8_files=invalid_utf8,
            manifest_errors=(str(exc),),
            filesystem_errors=filesystem_errors,
        )
    return catalog.preflight(directory)


def preflight_catalog(
    manifest_path: str | Path | None = None,
    markdown_dir: str | Path = DEFAULT_MARKDOWN_DIR,
) -> CatalogPreflightReport:
    """Alias with argument order convenient for reindex commands."""

    return validate_catalog(md_dir=markdown_dir, catalog_path=manifest_path)


__all__ = [
    "CatalogPreflightReport",
    "ContentKind",
    "DEFAULT_MANIFEST_PATH",
    "DEFAULT_MARKDOWN_DIR",
    "DOCUMENT_CLASS_MAPPING",
    "DocumentAlreadyExistsError",
    "DocumentClass",
    "DocumentMetadata",
    "DocumentMetadataCatalog",
    "DocumentNotFoundError",
    "Domain",
    "FeeKind",
    "INITIAL_CORPUS_SOURCE_COUNT",
    "METADATA_SCHEMA_VERSION",
    "MetadataCatalogError",
    "MetadataStatus",
    "StaticDocumentRemovalError",
    "get_document_metadata",
    "load_catalog",
    "normalize_document_class",
    "preflight_catalog",
    "validate_catalog",
]
