import httpx
from loguru import logger

class TranslationError(Exception):
    """Custom exception for translation errors."""
    pass

TRANSLATION_API_URL = "https://api.mymemory.translated.net/get"

async def translate_text(from_lang: str, to_lang: str, phrase: str) -> list[dict]:
    data = await fetch_translation_data(from_lang, to_lang, phrase)
    matches = extract_matches(data)
    filtered = filter_single_word_translations(matches)
    top = sort_and_limit_matches(filtered)
    return top

async def fetch_translation_data(from_lang: str, to_lang: str, phrase: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                TRANSLATION_API_URL,
                params={"q": phrase, "langpair": f"{from_lang}|{to_lang}"}
            )
            response.raise_for_status()
            logger.debug(f"Translation response status: {response.status_code}")
            return response.json()
    except Exception:
        logger.exception("Failed to fetch translation data.")
        raise TranslationError("Failed to contact translation service.")

def extract_matches(data: dict) -> list[dict]:
    matches = data.get("matches", [])
    if not matches:
        raise TranslationError("No translations found.")
    return matches

def filter_single_word_translations(matches: list[dict]) -> list[dict]:
    filtered = [
        m for m in matches
        if " " not in m["translation"].strip()
    ]
    if not filtered:
        raise TranslationError("Only multi-word translations found.")
    return filtered

def sort_and_limit_matches(matches: list[dict], limit: int = 5) -> list[dict]:
    return sorted(matches, key=lambda m: -m.get("match", 0))[:limit]
