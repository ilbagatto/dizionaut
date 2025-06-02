from dizionaut.utils import format_translation_result

def test_format_translation_result_basic():
    translations = [
        ({"translation": "gatto"}, 0.82),
        ({"translation": "micio"}, 0.70),
    ]
    def mock_lang_name(code): return {"it": "🇮🇹 Italian", "en": "🇬🇧 English"}.get(code, code)
    def mock_marker(score): return "🟢" if score > 0.75 else "🟡"

    result = format_translation_result(
        translations,
        from_lang="it",
        to_lang="en",
        lang_name_fn=mock_lang_name,
        quality_marker_fn=mock_marker
    )

    assert "🟢 gatto (82%)" in result
    assert "🟡 micio (70%)" in result
    assert "🇮🇹 Italian → 🇬🇧 English" in result
