import logging
from typing import Dict, List
import json
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def extract_tags_for_component(
    component: str,
    content: str,
    tag_terms: Dict[str, List[str]]
) -> List[str]:
    """
    Identify tags for a component review based on tagging master terms.

    Returns:
    - list of matched tags (may be empty)
    """

    print("tag_terms : ",tag_terms)

    if not tag_terms:
        return []

    tags_description = "\n".join(
        [
            f"- {tag}: terms -> {', '.join(terms)}"
            for tag, terms in tag_terms.items()
        ]
    )

    print("tags_description : ",tags_description)

    prompt = f"""
    You are a strict tagging system used in production analytics.

    Task:
    Identify which tags apply to the given COMPONENT review text.

    CRITICAL RULES (DO NOT BREAK):
    - Use ONLY the tags provided below.
    - A tag applies ONLY IF:
    1) One or more of its terms appear in the text AND
    2) The term is clearly referring to the GIVEN COMPONENT context.
    - Do NOT tag based on vague word presence alone.
    - Do NOT infer or assume meaning.
    - Do NOT invent new tags.
    - Do NOT modify or rewrite the text.
    - If NO tags apply, return an EMPTY JSON array: [].
    - Return ONLY valid JSON. No explanations. No markdown.

    Component under analysis:
    {component}

    Allowed tags and their terms:
    {tags_description}

    Component review text:
    \"\"\"{content}\"\"\"

    Output format (JSON array of strings):
    ["tag_1", "tag_2"]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=150
        )

        raw = response.choices[0].message.content.strip()
        logger.debug(f"Raw tagging output: {raw}")
        print(f"Raw tagging output: {raw}")

        if not raw:
            return []

        result = json.loads(raw)

        if not isinstance(result, list):
            return []

        return [str(tag) for tag in result]

    except Exception as e:
        logger.error(f"Tagging extraction failed: {e}")
        raise
