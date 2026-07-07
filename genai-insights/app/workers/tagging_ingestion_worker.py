import logging

from app.db.session import SessionLocal
from app.models.tagging import Tagging
from app.core.config import DATA_DIR
import pandas as pd
logger = logging.getLogger(__name__)


def ingest_tagging_csv_to_db(csv_path: str):
    """
    Ingest tagging rules from CSV into tagging table.

    CSV columns:
    - tag
    - tag_display_name (ignored)
    - component (single value, NOT comma separated)
    - terms (comma separated string, stored as-is)
    """

    csv_path = DATA_DIR / csv_path
    df = load_csv(csv_path)

    if df.empty:
        logger.info("No tagging records found in CSV")
        print("No taggign records found in CSV")
        return

    db = SessionLocal()
    inserted_count = 0

    try:
        for idx, row in df.iterrows():

            tag = safe_trim(row.get("tag"), 100)
            component = safe_trim(row.get("component"), 50)
            terms = safe_trim(row.get("terms"), None)

            # Mandatory validation
            if not tag or not component or not terms:
                logger.warning(
                    f"Skipping invalid tagging row at CSV index {idx}"
                )
                print(f"Skipping invalid tagging row at CSV index {idx}")
                continue

            tagging = Tagging(
                component=component,
                tag=tag,
                terms=terms
            )

            db.add(tagging)
            inserted_count += 1

        db.commit()
        logger.info(
            f"Successfully ingested {inserted_count} tagging rows"
        )
        print(f"Successfully ingested {inserted_count} tagging rows")

    except Exception as e:
        db.rollback()
        logger.error(
            f"Tagging CSV ingestion failed, rollback done: {e}"
        )
        raise

    finally:
        db.close()


def safe_trim(value: str | None, max_len: int | None) -> str | None:
    if value is None:
        return None

    value = str(value).strip()
    if not value:
        return None

    if max_len:
        return value[:max_len]

    return value

def load_csv(csv_path: str) -> pd.DataFrame:
    """
    Load CSV with robust encoding handling.
    """

    try:
        try:
            # First attempt: UTF-8
            df = pd.read_csv(csv_path, encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning(
                "UTF-8 decode failed, retrying with latin-1 encoding"
            )
            print("UTF-8 decode failed, retrying with latin-1 encoding")
            # Fallback: latin-1 (Windows-friendly)
            df = pd.read_csv(csv_path, encoding="latin-1")
        
        return df

    except Exception as e:
        logger.error(f"CSV loading failed: {e}")
        print(f"CSV loading failed: {e}")
        raise CSVProcessingError(str(e))