import json
import logging
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


SYSTEM_PROMPT = """
You are a production-grade sentiment classification engine for smartphone product reviews.

Your task is to determine the OVERALL sentiment of a review.

Rules (must follow strictly):

1. Sentiment must be exactly ONE of:
   - Positive
   - Negative
   - Neutral

2. Base sentiment primarily on the review text.
   - If the review contains BOTH positive and negative opinions about different aspects,
     sentiment MUST be Neutral.

3. Do NOT guess sentiment from missing keywords.
   - If explicit component keywords are absent, infer sentiment from intent,
     satisfaction, complaints, frustration, or praise.

4. Rating usage:
   - Use rating ONLY when textual sentiment is weak, vague, or unclear.
   - Rating must NEVER override clearly mixed sentiment.
   - Rating must NEVER override strong textual sentiment.

5. Emoji handling:
   - Emojis may support sentiment.
   - Emojis alone must NOT determine sentiment.

6. Confidence score rules:
   - Return a number between 0.0 and 1.0
   - ≥ 0.8 → sentiment is clear and unambiguous
   - 0.5–0.79 → sentiment is mixed or balanced
   - < 0.5 → sentiment is weak or inferred mainly from rating

Output rules:
- Return ONLY valid JSON
- No explanations
- No extra text

JSON format:
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
def analyze_overall_sentiment(
    review_text: str,
    rating: Optional[float]
) -> dict:
    """
    Classifies the overall sentiment of a smartphone review.
    Returns:
        {
            "sentiment": "Positive" | "Negative" | "Neutral",
            "confidence": float (0.0 - 1.0)
        }
    """

    user_prompt = f"""
    Review:
    \"\"\"{review_text}\"\"\"

    Rating:
    {rating if rating is not None else "Not Provided"}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=120
        )

        content = response.choices[0].message.content.strip()
        result = json.loads(content)

        # Hard validation
        if (
            not isinstance(result, dict) or
            "sentiment" not in result or
            "confidence" not in result or
            result["sentiment"] not in {"Positive", "Negative", "Neutral"} or
            not isinstance(result["confidence"], (int, float))
        ):
            raise ValueError("Invalid response format from OpenAI")

        # Clamp confidence
        result["confidence"] = max(
            0.0,
            min(1.0, float(result["confidence"]))
        )

        return result

    except Exception as e:
        logger.error(f"OpenAI sentiment analysis failed: {e}")
        raise