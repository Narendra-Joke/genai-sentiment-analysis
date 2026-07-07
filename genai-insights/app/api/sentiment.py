from fastapi import APIRouter, BackgroundTasks, Query
from app.workers.sentiment_worker import run_overall_sentiment_classification
import logging
from app.core.exception import GenAIException
import sys
from app.db.session import SessionLocal
from app.models.jobstatus import JobStatus

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sentiment",
    tags=["Sentiment Classification"]
)

@router.post("/run")
def run_sentiment_classification(
    background_tasks: BackgroundTasks,
    batch_size: int = Query(10, ge=1, le=100)
):
    """
    Triggers overall-phone sentiment classification asynchronously.
    """

    try:
        db = SessionLocal()

        job = JobStatus(
            job_type="sentiment",
            status="PENDING"
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        background_tasks.add_task(
        run_overall_sentiment_classification,
        job.id,
        batch_size
        )

        return {
            "job_id": job.id,
            "status": "SENTIMENT_CLASSIFICATION_STARTED",
            "batch_size": batch_size
        }

    except Exception as e:
        logger.error("Failed to start sentiment classification", exc_info=True)
        raise GenAIException(e, sys)

@router.get("/status/{job_id}")
def get_status(job_id: int):
    db = SessionLocal()

    job = db.query(JobStatus).filter(JobStatus.id == job_id).first()

    if not job:
        return {"error": "Job not found"}

    return {
        "job_id": job.id,
        "status": job.status,
        "total": job.total,
        "processed": job.processed
    }