import logging
import sys
from app.db.session import SessionLocal
from app.models.opinion_insight import OpinionInsight
from app.services.csv_service import (
    load_csv,
    get_pending_batch,
    mark_as_ingested
)
from app.core.config import DATA_DIR
from sqlalchemy import and_
import pandas as pd
from datetime import datetime, date
from app.core.exception import GenAIException

logger = logging.getLogger(__name__)

def ingest_csv_to_db(csv_path: str, batch_size: int, limit: bool):
    """
    Ingest raw reviews from CSV into opinion_insights table
    in batches. Marks CSV rows as ingested only after
    successful DB commit.
    """
    
    csv_path = DATA_DIR/csv_path

    while True:
        df = load_csv(csv_path)
        pending_df = get_pending_batch(df, batch_size)

        if pending_df.empty:
            logger.info("No pending records to ingest")
            print("No pending records to ingest")
            return
        
        if(limit):
            pass

        db = SessionLocal()
        processed_indices = []

        try:
            for idx, row in pending_df.iterrows():

                # Mandatory logical validation
                if not row["Content"] or not row["Product"]:
                    logger.warning(
                        f"Skipping invalid row at CSV index {idx}"
                    )
                    df.loc[idx, "isIngested"] = -1
                    continue

                # 2. Duplicate review
                # if is_duplicate_review(db, row):
                #     logger.warning(
                #         f"Duplicate review detected. "
                #         f"Marking isIngested = -1 at CSV index {idx}"
                #     )
                #     df.loc[idx, "isIngested"] = -1
                #     continue

                review = OpinionInsight(
                    product_name=row["Product"],
                    content=clean_nan(row["Content"]),
                    author=safe_trim(clean_nan(row.get("Author")),255),
                    country=row.get("Country"),
                    rating=clean_nan(row.get("Rating")),
                    source=row.get("Source"),
                    review_date=parse_review_date(row.get("Date")),
                    sentiment_classified=0,
                    component_classified=0
                )

                db.add(review)
                processed_indices.append(idx)

            db.commit()

            # Update CSV only AFTER DB commit
            mark_as_ingested(df, processed_indices, csv_path)

            logger.info(
                f"Successfully ingested {len(processed_indices)} reviews"
            )
            
            if(limit):
                print(f"{batch_size} records successfully ingested")
                break
        except Exception as e:
            db.rollback()
            logger.error(f"CSV ingestion failed, rollback done: {e}",exc_info=True)
            raise GenAIException(e,sys)

        finally:
            db.close()

def is_duplicate_review(db, row) -> bool:
    return db.query(OpinionInsight).filter(
        and_(
            OpinionInsight.product_name == row["Product"],
            OpinionInsight.content == row["Content"],
            OpinionInsight.source == row["Source"]
        )
    ).first() is not None

def clean_nan(value):
    if pd.isna(value):
        return None
    return value

def parse_review_date(value) -> date | None:
    """
    Safely parse review date from CSV.

    Expected format: MM/DD/YYYY (e.g., 01/31/2026)
    Returns datetime.date or None.
    """

    # Handle NaN, None, empty
    if value is None or pd.isna(value):
        return None

    # Handle string date
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None

        try:
            return datetime.strptime(value, "%m/%d/%Y").date()
        except ValueError:
            return None

    # Handle datetime (rare but safe)
    if isinstance(value, datetime):
        return value.date()

    # Handle date object
    if isinstance(value, date):
        return value

    return None

def safe_trim(value: str | None, max_len: int) -> str | None:
    if value is None:
        return None

    value = str(value).strip()
    if not value:
        return None

    return value[:max_len]



