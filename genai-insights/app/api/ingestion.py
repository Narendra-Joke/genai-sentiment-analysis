from fastapi import APIRouter, BackgroundTasks, Query
from app.workers.csv_ingestion_worker import ingest_csv_to_db
import logging
import sys
from app.core.exception import GenAIException

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ingestion",
    tags=["CSV Ingestion"]
)

@router.post("/run")
def ingest_reviews(
    background_tasks: BackgroundTasks,
    file_name: str = Query(..., description="CSV file name inside data/ folder"),
    batch_size: int = Query(100, ge=1, le=1000),
    limit: bool = Query(True, description="Apply batch limit or process all records")
):
    """
    Triggers CSV → DB ingestion asynchronously.
    """

    try:
        logger.info(
            f"Ingestion requested | file={file_name}, batch_size={batch_size}, limit={limit}"
        )

        background_tasks.add_task(
            ingest_csv_to_db,
            file_name,
            batch_size,
            limit
        )

        return {
            "status": "INGESTION_STARTED",
            "file_name": file_name,
            "batch_size": batch_size
        }
    except Exception as e:
        logger.error("Failed to start ingestion", exc_info=True)
        raise GenAIException(e, sys)
    