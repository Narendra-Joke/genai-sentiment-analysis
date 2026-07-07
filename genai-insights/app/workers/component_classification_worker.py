import logging

from sqlalchemy.orm import Session
from collections import defaultdict
from app.db.session import SessionLocal
from app.models.opinion_insight import OpinionInsight
from app.models.component_opinion_insight import ComponentOpinionInsight
from app.models.component_classification import ComponentClassification
from app.services.component_sentiment_service import analyze_component_sentiment
from app.services.component_extraction_service import extract_components_from_review
from app.services.openai_service import analyze_overall_sentiment
from app.workers.sentiment_worker import (
    build_short_failure_reason,
    calibrate_confidence
)
from app.models.tagging import Tagging
from app.services.tagging_service import extract_tags_for_component
from typing import Dict,List
from app.models.jobstatus import JobStatus

logger = logging.getLogger(__name__)

STRICT_MODE = "strict"
CONFIRM_MODE = "confirm"

def run_component_classification(job_id: int, batch_size: int = 5):
    """
    Phase-2:
    Overall review -> component-wise extraction + component sentiment
    """

    db: Session = SessionLocal()
    job: None

    try:
        job = db.query(JobStatus).filter(JobStatus.id == job_id).first()

        if not job:
            logger.error(f"Job {job_id} not found")
            return

        job.status = "RUNNING"
        db.commit()

        # 1. Fetch pending parent reviews
        reviews = (
            db.query(OpinionInsight)
            .filter(OpinionInsight.sentiment_classified == 1,
                    OpinionInsight.component_classified == 0)
            .limit(batch_size)
            .all()
        )

        print("reviews : ", reviews)
        
        if not reviews:
            job.total = 0
            job.processed = 0
            job.status = "COMPLETED"
            db.commit()

            logger.info("No pending reviews for component classification")
            print("No pending reviews for component classification")
            return

        total = len(reviews)
        job.total = total
        db.commit()

        # 2. Load component master data
        components = db.query(ComponentClassification).all()

        component_keywords = {
            row.component.lower(): [
                kw.strip().lower()
                for kw in row.keywords.split(",")
            ]
            for row in components
        }

        logger.info(
            f"Loaded {len(component_keywords)} components for classification"
        )

        if not component_keywords:
            logger.error("component_classification table is empty. Aborting run.")
            print("component_classification table is empty. Aborting run.")
            return

        # 3️⃣ Load tagging master data (ONCE)
        tag_rows = db.query(Tagging).all()
        tagging_map = defaultdict(dict)

        for row in tag_rows:
            tagging_map[row.component.lower()][row.tag] = [
                t.strip().lower() for t in row.terms.split(",")
            ]

        logger.info(
            f"Loaded {len(component_keywords)} components "
            f"and {len(tag_rows)} tagging rules"
        )

        print(f"Loaded {len(component_keywords)} components "
            f"and {len(tag_rows)} tagging rules")

        processed_count = 0

        # 3. Process each review
        for review in reviews:
            logger.info(
                f"Processing component classification for review_id={review.id}"
            )
            print(f"Processing component classification for review_id={review.id}")

            try:
                extracted = extract_components_from_review(
                    review.content,
                    component_keywords,
                )    
                
                # ✅ No components found is NOT a failure
                if not extracted:
                    review.component_classified = 1
                    processed_count += 1
                    logger.info(
                        f"No target components found for review_id={review.id}"
                    )
                    print(f"No target components found for review_id={review.id}")
                    continue

                # 4. Insert component rows
                for component, text in extracted.items():
                    component_row = ComponentOpinionInsight(
                        parent_id=review.id,
                        product_name=review.product_name,
                        source=review.source,
                        author=review.author,
                        country=review.country,
                        content=text,
                        component=component,
                        rating=review.rating,
                        review_date=review.review_date,
                        sentiment_classified=0,
                        job_id=job_id
                    )

                    try:
                        sentiment_result = analyze_component_sentiment(
                            text,
                            component                        
                        )

                        component_row.sentiment = sentiment_result["sentiment"]
                        component_row.sentiment_confidence = calibrate_confidence(
                            sentiment_result["confidence"]
                        )
                        component_row.sentiment_classified = 1

                    except Exception as e:
                        component_row.sentiment_classified = -1
                        component_row.extra = build_short_failure_reason(e)

                        logger.error(
                            f"Component sentiment failed "
                            f"(review_id={review.id}, component={component})"
                        )
                        print(
                            f"Component sentiment failed "
                            f"(review_id={review.id}, component={component})"
                        )

                    # ----- TAGGING STARTS HERE -----

                    # # Load tagging master data
                    # tag_rows = db.query(Tagging).all()

                    # tagging_map = {}
                    # for row in tag_rows:
                    #     component = row.component.lower()
                    #     tagging_map.setdefault(component, {})
                    #     tagging_map[component][row.tag] = [
                    #         t.strip().lower() for t in row.terms.split(",")
                    #     ]

                    try:
                        tag_terms = tagging_map.get(component, {})

                        if tag_terms:
                            tags = extract_tags_for_component(
                                component=component,
                                content=text,
                                tag_terms=tag_terms
                            )

                            if tags:
                                component_row.tags = ",".join(tags)

                        # Even if no tags found → success
                        component_row.tagging_classified = 1

                    except Exception as e:
                        component_row.tagging_classified = -1
                        component_row.extra = build_short_failure_reason(e)

                        logger.error(
                            f"Tagging failed "
                            f"(review_id={review.id}, component={component})"
                        )
                        print(
                            f"Tagging failed "
                            f"(review_id={review.id}, component={component})"
                        )
                    # ----- TAGGING ENDS HERE -----


                    db.add(component_row)

                # 5. Mark parent success
                review.component_classified = 1
                processed_count += 1

            except Exception as e:
                review.component_classified = -1
                review.extra = build_short_failure_reason(e)

                logger.error(
                    f"Component classification failed for review_id={review.id}: {e}"
                )
                print(
                    f"Component classification failed for review_id={review.id}: {e}"
                )

        # ✅ Final commit
        job.processed = processed_count
        job.status = "COMPLETED"
        db.commit()

        logger.info("Component classification batch committed successfully")
        print("Component classification batch committed successfully")

    except Exception as e:
        db.rollback()

        if job:
            job.status = "FAILED"
            db.commit()

        logger.error(f"Component worker failed, rollback done: {e}")
        print(f"Component worker failed, rollback done: {e}")
        raise

    finally:
        db.close()