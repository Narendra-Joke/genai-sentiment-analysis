import json
import logging
from typing import Dict, List

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
def extract_components_from_review(
    review_text: str,
    component_keywords: Dict[str, List[str]]
) -> Dict[str, str]:

    components_description = "\n".join(
        f"- {comp}: {', '.join(keywords)}"
        for comp, keywords in component_keywords.items()
    )

#     prompt = f"""
# You are a STRICT, production-grade component extraction system.

# TASK:
# From the given product review, extract component-wise review text.

# COMPONENT INPUT:
# You will be given a list of allowed components.
# Each component includes keyword hints to help identification.

# IMPORTANT:
# - The allowed components list is the ONLY source of truth.
# - You must consider ONLY those components.
# - You must NOT assume any fixed component set.

# DETECTION RULES:
# - For each allowed component:
#   - If the review discusses its functionality, behavior, issue,
#     comparison, or user experience, it is considered mentioned.
#   - Keyword hints are GUIDANCE only, not mandatory.
#   - Semantic understanding MAY be used ONLY to decide
#     whether the component is discussed.

# EXTRACTION RULES:
# - Extract ONLY text from the original review.
# - Copy text EXACTLY as written.
# - Do NOT rewrite, paraphrase, summarize, or normalize.
# - Do NOT add new words.
# - Preserve full descriptive or comparative context.
# - Do NOT shorten clauses that carry meaning.
# - Ignore unrelated topics.
# - If a component is not discussed, do NOT include it.

# OUTPUT RULES:
# - Output MUST be a single valid JSON object.
# - Keys MUST be component names from the allowed list.
# - Values MUST be the exact extracted text.
# - If no components are discussed, return {{}}.
# - No explanations, no markdown.

# Allowed components and keyword hints:
# {components_description}

# REVIEW:
# \"\"\"{review_text}\"\"\"
# """

    prompt = f"""
    You are a STRICT, production-grade component extraction system.

    TASK:
    From the given product review, extract component-wise review text.

    COMPONENT INPUT:
    You will be given a list of allowed components.
    Each component includes keyword hints to help identification.

    HARD CONSTRAINT (VERY IMPORTANT):
    - The allowed components list is the ONLY source of truth.
    - You MUST NOT extract any component that is NOT explicitly listed,
    EVEN IF the review clearly mentions it.
    - Mentions of Wi-Fi, Bluetooth, GPS, network, price, etc.
    MUST be ignored unless they appear in the allowed components list.

    DETECTION RULES:
    - For each allowed component:
    - If the review discusses its functionality, behavior, issue,
        comparison, or user experience, it is considered mentioned.
    - Keyword hints are GUIDANCE only, not mandatory.
    - Semantic understanding MAY be used ONLY to decide
        whether the allowed component is discussed.

    EXTRACTION RULES:
    - Extract ONLY text from the original review.
    - Copy text EXACTLY as written.
    - Do NOT rewrite, paraphrase, summarize, or normalize.
    - Do NOT add new words.
    - Preserve full descriptive or comparative context.
    - Ignore unrelated topics.
    - If a component is not discussed, do NOT include it.

    OUTPUT RULES:
    - Output MUST be a single valid JSON object.
    - Keys MUST be component names from the allowed list ONLY.
    - Values MUST be the exact extracted text.
    - If no allowed components are discussed, return {{}}.
    - No explanations, no markdown.

    ====================
    FEW-SHOT EXAMPLES
    ====================

    Allowed components:
    battery,performance,design,audio

    Review:
    "battery is good, but wifi is not stable connectivity but performance was better and it's lightweight mobile phone"

    Output:
    {{
    "battery": "battery is good",
    "performance": "performance was better",
    "design": "it's lightweight mobile phone"
    }}

    ---
    Allowed components:
    display,camera

    Review:
    "The screen looks amazing until you tilt it and suddenly the color shifts like it’s broken, but the camera somehow still takes vibrant photos even in low light."

    Output:
    {{
    "display": "The screen looks amazing until you tilt it and suddenly the color shifts like it’s broken",
    "camera": "the camera somehow still takes vibrant photos even in low light"
    }}

    ---
    # NEGATIVE EXAMPLE (CRITICAL)
    Allowed components:
    camera,display,design

    Review:
    "Beautiful display with perfect blacks; the camera captures detail; Wi-Fi is stable; Bluetooth drops often."

    Output:
    {{
    "display": "Beautiful display with perfect blacks",
    "camera": "the camera captures detail"
    }}

    ====================
    END EXAMPLES
    ====================

    Allowed components and keyword hints:
    {components_description}

    REVIEW:
    \"\"\"{review_text}\"\"\"
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a deterministic extraction engine."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=400
    )

    content = response.choices[0].message.content.strip()
    if not content:
        return {}

    try:
        result = json.loads(content)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        logger.error("Non-JSON output from OpenAI")

    return {}