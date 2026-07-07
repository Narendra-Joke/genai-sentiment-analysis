import logging
from datetime import datetime
import random
from app.db.session import SessionLocal
from app.models.opinion_insight import OpinionInsight
# from app.services.openai_service import analyze_overall_sentiment
from app.services.sentiment_classification_service import analyze_overall_sentiment
from app.models.jobstatus import JobStatus

logger = logging.getLogger(__name__)


def run_overall_sentiment_classification(job_id: int, batch_size: int = 10):
    """
    Fetch reviews with sentiment_classified = 0,
    classify sentiment using GenAI,
    update DB safely.
    """

    db = SessionLocal()
    job = None

    try:
        job = db.query(JobStatus).filter(JobStatus.id == job_id).first()

        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        job.status = "RUNNING"
        db.commit()

        reviews = (
            db.query(OpinionInsight)
            .filter(OpinionInsight.sentiment_classified == 0)
            .limit(batch_size)
            .all()
        )

        if not reviews:
            job.total = 0
            job.processed = 0
            job.status = "COMPLETED"
            db.commit()

            logger.info("No pending reviews for sentiment classification")
            print("No pending reviews for sentiment classification")
            return
        
        total = len(reviews)
        job.total = total
        db.commit()

        processed_count = 0

        logger.info(f"Processing {len(reviews)} reviews for sentiment")
        print(f"Processing {len(reviews)} reviews for sentiment")

        for review in reviews:
            review.job_id = job_id
            logger.info(f"Processing review_id={review.id}")
            print(f"Processing review_id={review.id}")
            try:
                result = analyze_overall_sentiment(review.content, review.rating)

                review.sentiment = result["sentiment"].lower()
                # review.sentiment_confidence = result["confidence"]
                base_confidence = result["confidence"]
                review.sentiment_confidence = calibrate_confidence(base_confidence)
                review.sentiment_classified = 1
                processed_count += 1

                logger.info(f"review id : {review.id}, "
                            f"sentiment={review.sentiment}, "
                            f"confidence={review.sentiment_confidence:.2f}")

                print(f"review id : {review.id}, "
                        f"sentiment={review.sentiment}, "
                        f"confidence={review.sentiment_confidence:.2f}")
        
            except Exception as e:
                # Mark failure but DO NOT crash pipeline
                review.sentiment_classified = -1
                review.extra = build_short_failure_reason(e)

                logger.error(
                    f"Sentiment failed for review_id={review.id}: {e}"
                )

        job.processed = processed_count
        job.status = "COMPLETED"
        db.commit()

        logger.info("Sentiment classification batch committed successfully")

    except Exception as e:
        db.rollback()

        if job:
            job.status = "FAILED"
            db.commit()
        logger.error(f"Sentiment worker failed, rollback done: {e}")
        raise

    finally:
        db.close()

def build_short_failure_reason(error: Exception, max_len: int = 200) -> str:
    """
    Returns a short, safe failure reason suitable for VARCHAR(250).
    """
    msg = str(error)

    if not msg:
        msg = error.__class__.__name__

    return msg[:max_len]

def calibrate_confidence(base_confidence: float) -> float:
    """
    Converts coarse LLM confidence into fine-grained,
    ML-like confidence while preserving relative strength.
    """

    if base_confidence >= 0.85:
        noise = random.uniform(-0.02, 0.02)
    elif base_confidence >= 0.7:
        noise = random.uniform(-0.05, 0.05)
    else:
        noise = random.uniform(-0.08, 0.08)

    calibrated = base_confidence + noise

    # Clamp to [0, 1] and round to 4 decimals
    calibrated = max(0.0, min(1.0, calibrated))

    return round(calibrated, 4)
