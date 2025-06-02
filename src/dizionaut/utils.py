"""
Utility functions used throughout the bot.
"""

import textwrap

# Supported languages with flags and codes
LANGUAGES = (
    ("🇧🇬 Bulgarian", "bg"),
    ("🇨🇿 Czech", "cs"),
    ("🇬🇧 English", "en"),
    ("🇫🇷 French", "fr"),
    ("🇩🇪 German", "de"),
    ("🇭🇷 Croatian", "hr"),
    ("🇮🇹 Italian", "it"),
    ("🇵🇱 Polish", "pl"),
    ("🇵🇹 Portuguese", "pt"),
    ("🇷🇺 Russian", "ru"),
    ("🇷🇸 Serbian", "sr"),
    ("🇸🇰 Slovak", "sk"),
    ("🇪🇸 Spanish", "es"),
    ("🇺🇦 Ukrainian", "uk"),
)


def get_lang_name(lang_code: str) -> str:
    """
    Return the language name (with flag) for a given language code.

    Args:
        lang_code (str): ISO language code.

    Returns:
        str: Human-readable language name with flag, or raw code if not found.
    """
    lang_name = next((name for name, code in LANGUAGES if code == lang_code), lang_code)
    return lang_name


def format_ml(text: str) -> str:
    """
    Normalize multi-line string by removing common indentation and trimming whitespace.

    Args:
        text (str): A raw multi-line string.

    Returns:
        str: Cleaned and dedented string.
    """
    return textwrap.dedent(text).strip()


def format_translation_result(
    translations: list[tuple[dict, float]],
    from_lang: str,
    to_lang: str,
    lang_name_fn: callable,
    quality_marker_fn: callable,
) -> str:
    """
    Format a list of scored translations into a user-readable message.

    Args:
        translations (list): List of (translation_dict, score) tuples.
        from_lang (str): Source language code.
        to_lang (str): Target language code.
        lang_name_fn (callable): Function to get the human-readable name for a language code.
        quality_marker_fn (callable): Function to get a marker (emoji) for a score.

    Returns:
        str: Formatted message string.
    """
    lines = [
        f"{quality_marker_fn(score)} {t['translation']} ({int(score * 100)}%)"
        for t, score in translations
    ]
    lang_info = f"{lang_name_fn(from_lang)} → {lang_name_fn(to_lang)}"
    return f"📘 Translation ({lang_info}):\n\n" + "\n".join(lines)
