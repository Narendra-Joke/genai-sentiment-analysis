import json
import logging
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

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
    Calls OpenAI to classify overall sentiment of a review.
    Returns dict with keys: sentiment, confidence
    """

    # prompt = f"""
    # You are a professional sentiment classification system used in production analytics.

    # Your task:
    # Determine the OVERALL sentiment of the following smartphone product review.

    # Primary rules:
    # - Classify sentiment strictly as ONE of: Positive, Negative, or Neutral.
    # - Base your decision primarily on the review text.
    # - If the review clearly expresses both positive and negative opinions, treat it as Neutral.

    # Emoji handling:
    # - Emojis may indicate emotional tone.
    # - Do NOT let emojis alone override the textual meaning.

    # Rating-based tie-breaker (IMPORTANT):
    # - Use the rating ONLY if the textual sentiment is weak, ambiguous, or Neutral.
    # - If text is Neutral or unclear:
    #     - Rating ≥ 4.0 → Positive
    #     - Rating ≤ 2.0 → Negative
    #     - Rating == 3.0 → Neutral
    # - If rating is not provided, ignore rating completely.
    # - Do NOT let rating override strong textual sentiment.

    # Confidence score:
    # - Return a confidence score between 0 and 1.
    # - High confidence (≥0.8): sentiment is clear and consistent.
    # - Medium confidence (0.5–0.79): sentiment is present but not strong.
    # - Low confidence (<0.5): sentiment is ambiguous or inferred using rating.

    # Output format:
    # Return ONLY valid JSON in the following structure:
    # {{
    # "sentiment": "Positive | Negative | Neutral",
    # "confidence": number between 0 and 1
    # }}

    # Review text:
    # \"\"\"{review_text}\"\"\"

    # Rating:
    # {rating if rating is not None else "Not Provided"}
    # """

    prompt = f"""
You are a professional sentiment classification system used in production analytics.

Your task:
Determine the OVERALL sentiment of the following smartphone product review.

Primary rules:
- Classify sentiment strictly as ONE of: Positive, Negative, or Neutral.
- Base your decision primarily on the review text.
- If the review clearly expresses BOTH positive and negative opinions about different aspects,
  the sentiment MUST be Neutral.

Important constraints:
- Mixed sentiment MUST remain Neutral.
- Rating MUST NOT override mixed sentiment.
- Use rating ONLY when the textual sentiment is weak, vague, or unclear
  (NOT when both positive and negative opinions are clearly present).

Emoji handling:
- Emojis may indicate emotional tone.
- Do NOT let emojis alone override the textual meaning.

Rating-based tie-breaker (ONLY for weak or unclear text):
- If the text is weak or ambiguous:
    - Rating ≥ 4.0 → Positive
    - Rating ≤ 2.0 → Negative
    - Rating == 3.0 → Neutral
- If rating is not provided, ignore rating completely.

Confidence score rules:
- Return a confidence score between 0 and 1.
- High confidence (≥0.8): sentiment is clearly positive OR clearly negative.
- Medium confidence (0.5–0.79): sentiment is mixed or balanced.
- Low confidence (<0.5): sentiment is weak, vague, or inferred mainly from rating.

Output format:
Return ONLY valid JSON in the following structure:
{{
  "sentiment": "Positive | Negative | Neutral",
  "confidence": number between 0 and 1
}}

Review text:
\"\"\"{review_text}\"\"\"

Rating:
{rating if rating is not None else "Not Provided"}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=120
        )

        content = response.choices[0].message.content.strip()
        result = json.loads(content)

        # Hard validation
        if (
            "sentiment" not in result or
            "confidence" not in result or
            result["sentiment"] not in ["Positive", "Negative", "Neutral"] or
            not isinstance(result["confidence"], (int, float))
        ):
            raise ValueError("Invalid response format from OpenAI")

        # Clamp confidence
        result["confidence"] = max(
            0.0, min(1.0, float(result["confidence"]))
        )

        return result

    except Exception as e:
        logger.error(f"OpenAI sentiment analysis failed: {e}")
        raise
