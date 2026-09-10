"""Re-ingest the 4 updated tuition markdown files into Qdrant, PostgreSQL, and BM25."""

import logging
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
)
logger = logging.getLogger("reingest_tuition")

from app.services.rag_engine import AdvancedChunkingEngine

TARGET_FILES = [
    "MucHocPhi_QuyDinhChung.md",
    "MucHocPhi_DaiHocChinhQuy_Khoa51_VeTruoc.md",
    "MucHocPhi_DaiHocChinhQuy_Khoa52.md",
    "MucHocPhi_ChatLuongCao_TienTien.md",
]


def main():
    logger.info("Initializing AdvancedChunkingEngine...")
    engine = AdvancedChunkingEngine()

    markdown_dir = PROJECT_ROOT / "data" / "markdown"

    for filename in TARGET_FILES:
        filepath = markdown_dir / filename
        if not filepath.exists():
            logger.error("File not found: %s", filepath)
            continue

        logger.info("Purging old records for %s...", filename)
        engine.purge_document(source=filename)

        logger.info("Re-ingesting %s...", filename)
        success = engine.ingest_markdown_document(str(filepath))
        if success:
            logger.info("✅ Successfully re-ingested %s", filename)
        else:
            logger.error("❌ Failed to re-ingest %s", filename)

    logger.info("Re-ingestion process completed!")


if __name__ == "__main__":
    main()
