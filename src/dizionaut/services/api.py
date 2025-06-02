"""
Service module for accessing the MyMemory translation API.

Handles API requests, response parsing, translation ranking,
and basic error handling.
"""

import httpx
from loguru import logger
from operator import itemgetter

from dizionaut.services.scoring import score


class TranslationError(Exception):
    """
    Custom exception for signaling problems during translation fetching or parsing.
    """
    pass


TRANSLATION_API_URL = "https://api.mymemory.translated.net/get"


def _deduplicate_translations(
    scored_translations: list[tuple[dict, float]],
) -> list[tuple[dict, float]]:
    """
    Remove duplicate translations by normalized string, keeping the highest scored one.

    Args:
        scored_translations (list): List of (translation_dict, score) pairs.

    Returns:
        list: Deduplicated list of (translation_dict, score) pairs.
    """
    seen = {}
    for t, s in scored_translations:
        normalized = t["translation"].strip().lower()
        if normalized not in seen or s > seen[normalized][1]:
            seen[normalized] = (t, s)
    return list(seen.values())


async def translate_text(
    from_lang: str, to_lang: str, phrase: str
) -> list[tuple[dict, float]]:
    """
    Perform a translation request using the MyMemory API.

    Args:
        from_lang (str): Source language code (e.g., 'en').
        to_lang (str): Target language code (e.g., 'it').
        phrase (str): Text to translate.

    Returns:
        list: List of (translation_dict, score) tuples, sorted by score (descending).

    Raises:
        TranslationError: If no translations are returned or request fails.
    """
    data = await fetch_translation_data(from_lang, to_lang, phrase)
    matches = data.get("matches", [])
    if not matches:
        raise TranslationError("No translations found.")

    scored = [(t, score(t)) for t in matches]
    scored = _deduplicate_translations(scored)
    return sorted(scored, key=itemgetter(1), reverse=True)


async def fetch_translation_data(from_lang: str, to_lang: str, phrase: str) -> dict:
    """
    Fetch raw translation response from MyMemory API.

    Args:
        from_lang (str): Source language code.
        to_lang (str): Target language code.
        phrase (str): Text to translate.

    Returns:
        dict: Raw JSON response.

    Raises:
        TranslationError: If the request fails or the response is invalid.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                TRANSLATION_API_URL,
                params={"q": phrase, "langpair": f"{from_lang}|{to_lang}"},
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.exception("Failed to fetch translation data")
        raise TranslationError("API request failed") from e
