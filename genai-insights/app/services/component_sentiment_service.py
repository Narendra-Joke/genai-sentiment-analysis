import json
import logging

from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


# =========================
# SYSTEM PROMPT (A.I.M)
# =========================
SYSTEM_PROMPT = """
You are a production-grade A.I. system for COMPONENT-LEVEL sentiment classification
of smartphone product reviews.

ROLE:
You act as a deterministic classifier.
You do NOT explain reasoning.
You ONLY return structured output.

TASK:
Determine the sentiment expressed toward the GIVEN COMPONENT
based ONLY on the provided review text.

IMPORTANT CONTEXT:
This is COMPONENT sentiment analysis, NOT overall product sentiment.
For components, NEGATIVE feedback takes priority.

DECISION RULES (CRITICAL):

1. Sentiment must be exactly ONE of:
   - Positive
   - Negative
   - Neutral

2. Base your decision ONLY on the given review text.
   Do NOT use ratings, assumptions, or external knowledge.

3. NEGATIVE-DOMINANT RULE (MOST IMPORTANT):
   - If the review contains ANY negative opinion about the component,
     the sentiment MUST be Negative,
     EVEN IF positive points are also mentioned.
# 3. NEGATIVE-DOMINANT RULE (REFINED):
#    - If the review expresses a meaningful problem, flaw, or limitation
#      that affects the quality, reliability, usability, or expected
#      behavior of the component, the sentiment MUST be Negative,
#      even if positive aspects are also mentioned.
#    - If the review mentions a minor or incidental drawback that does
#      not materially affect the component’s quality or usability,
#      and the overall message is clearly favorable, the sentiment
#      SHOULD remain Positive.
#    - Judge based on impact and seriousness, not on specific words
#      or the count of positive vs negative statements.

4. POSITIVE RULE:
   - Classify as Positive ONLY if the review contains positive feedback
     AND NO negative feedback about the component.

5. NEUTRAL RULE:
   - Classify as Neutral ONLY if the text is purely factual,
     descriptive, or ambiguous with no clear positive or negative judgment.

6. COMPARATIVE RULE:
   - If the review compares the component unfavorably to another product
     (e.g., “older model was better”),
     this MUST be classified as Negative.

7. COMPONENT SCOPE RULE:
   - Evaluate sentiment ONLY for the specified component.
   - Ignore opinions about other components.

CONFIDENCE SCORE:
- Return a confidence score between 0.0 and 1.0.
- ≥ 0.8 → sentiment is clear and explicit.
- 0.5–0.79 → sentiment present but moderate.
- < 0.5 → sentiment weak or borderline.

OUTPUT:
Return ONLY valid JSON:
{
  "sentiment": "Positive | Negative | Neutral",
  "confidence": number between 0 and 1
}
"""

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=2, max=10),
    reraise=True
)
def analyze_component_sentiment(review_text: str, component: str) -> dict:
    """
    Classifies sentiment for a specific smartphone component.
    Rating is intentionally ignored.
    Returns:
        {
            "sentiment": "Positive" | "Negative" | "Neutral",
            "confidence": float (0.0 - 1.0)
        }
    """

    user_prompt = f"""
    Component under analysis:
    {component}

    Component review text:
    \"\"\"{review_text}\"\"\"
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=400
        )

        content = response.choices[0].message.content.strip()
        result = json.loads(content)

        # Hard validation
        if (
            not isinstance(result, dict) or
            result.get("sentiment") not in {"Positive", "Negative", "Neutral"} or
            not isinstance(result.get("confidence"), (int, float))
        ):
            raise ValueError("Invalid response format from OpenAI")

        # Clamp confidence safely
        result["confidence"] = max(
            0.0,
            min(1.0, float(result["confidence"]))
        )

        return result

    except Exception as e:
        logger.error(f"Component sentiment analysis failed: {e}")
        raise