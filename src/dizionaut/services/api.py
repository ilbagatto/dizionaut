import httpx
from loguru import logger
from operator import itemgetter

from dizionaut.services.scoring import score


class TranslationError(Exception):
    """Custom exception for translation errors."""

    pass


TRANSLATION_API_URL = "https://api.mymemory.translated.net/get"


def _deduplicate_translations(
    scored_translations: list[tuple[dict, float]],
) -> list[tuple[dict, float]]:
    seen = {}
    for t, score in scored_translations:
        normalized = t["translation"].strip().lower()
        if normalized not in seen or score > seen[normalized][1]:
            seen[normalized] = (t, score)
    return list(seen.values())


async def translate_text(
    from_lang: str, to_lang: str, phrase: str
) -> list[tuple[dict[any], float]]:
    data = await fetch_translation_data(from_lang, to_lang, phrase)
    matches = data.get("matches", [])
    if not matches:
        raise TranslationError("No translations found.")

    scored = [(t, score(t)) for t in matches]
    scored = _deduplicate_translations(scored)
    scored.sort(key=lambda pair: pair[1], reverse=True)

    return scored


async def fetch_translation_data(from_lang: str, to_lang: str, phrase: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                TRANSLATION_API_URL,
                params={"q": phrase, "langpair": f"{from_lang}|{to_lang}"},
            )
            response.raise_for_status()
            logger.debug(f"Translation response status: {response.status_code}")
            return response.json()
    except Exception:
        logger.exception("Failed to fetch translation data.")
        raise TranslationError("Failed to contact translation service.")
