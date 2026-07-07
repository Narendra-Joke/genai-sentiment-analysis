from fastapi import APIRouter, BackgroundTasks, Query
from app.workers.component_classification_worker import run_component_classification
import logging
from app.core.exception import GenAIException
import sys
from app.db.session import SessionLocal
from app.models.jobstatus import JobStatus

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/component",
    tags=["Component Extraction & Classification"]
)


@router.post("/run")
def run_component_job(
    background_tasks: BackgroundTasks,
    batch_size: int = Query(5, ge=1, le=25)
):
    """
    Triggers overall-phone component extraction & classification asynchronously.
    """

    try:
        db = SessionLocal()

        job = JobStatus(
            job_type="component",
            status="PENDING"
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        background_tasks.add_task(
        run_component_classification,
        job.id,
        batch_size
        )

        return {
            "status": "COMPONENT_EXTRACTION_AND_CLASSIFICATION_STARTED",
            "job_id": job.id,
            "batch_size": batch_size
        }
    except Exception as e:
        logger.error("Failed to start component extraction & classification", exc_info=True)
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
    
    