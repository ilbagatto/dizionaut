from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    CallbackQuery,
)
from aiogram.filters import Command
from loguru import logger

from ..services.scoring import quality_marker

from .success import handle_success_state

from ..utils import format_ml

from .errors import handle_error_state

from ..services.api import TranslationError, translate_text

from ..states import TranslateState

router = Router()

# Supported languages with flags
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


def get_lang_name(lang_code):
    lang_name = next((name for name, code in LANGUAGES if code == lang_code), lang_code)
    return lang_name


def language_keyboard(prefix: str, excluded_code: str = None) -> InlineKeyboardMarkup:

    def is_enabled(code: str) -> bool:
        return code != excluded_code if excluded_code is not None else True


    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"{prefix}:{code}")]
            for name, code in LANGUAGES
            if is_enabled(code)
        ]
    )


@router.callback_query(F.data == "translate")
async def start_translation(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Please select source language:", reply_markup=language_keyboard("from")
    )
    await state.set_state(TranslateState.from_lang)
    await callback.answer()


@router.callback_query(F.data.startswith("from:"))
async def handle_from_lang(callback: types.CallbackQuery, state: FSMContext):
    lang_code = callback.data.split(":")[1]
    lang_name = get_lang_name(lang_code)
    await state.update_data(from_lang=lang_code)
    await callback.message.edit_text(
        format_ml(
            f"""
            Source language: {lang_name}.
                  
            Now select target language:
            """
        ),
        reply_markup=language_keyboard("to", excluded_code=lang_code),
    )
    await state.set_state(TranslateState.to_lang)
    await callback.answer()


@router.callback_query(F.data.startswith("to:"))
async def handle_to_lang(callback: types.CallbackQuery, state: FSMContext):
    lang_code = callback.data.split(":")[1]
    await state.update_data(to_lang=lang_code)

    data = await state.get_data()
    from_lang = data.get("from_lang")
    to_lang = data.get("to_lang")
    from_lang_name = get_lang_name(from_lang)
    to_lang_name = get_lang_name(to_lang)

    await callback.message.edit_text(
        format_ml(
            f"""
        Source language: {from_lang_name}
        Target language: {to_lang_name}
        
        Enter the word you want to translate:
        """
        )
    )
    await state.set_state(TranslateState.word)
    await callback.answer()


def format_translation_list(results: list[tuple[dict, float]]) -> str:
    lines = [
        f"{quality_marker(score)} {entry['translation']} ({int(score * 100)}%)"
        for entry, score in results
    ]
    return "🔤 Translations:\n\n" + "\n".join(lines)


@router.message(TranslateState.word)
async def handle_word_input(message: Message, state: FSMContext):
    data = await state.get_data()
    from_lang = data.get("from_lang")
    to_lang = data.get("to_lang")
    word = message.text.strip()

    logger.info(f"User input: '{word}' ({from_lang} → {to_lang})")
    try:
        try:
            matches = await translate_text(from_lang, to_lang, word)
            formatted = format_translation_list(matches)
            await message.answer(formatted)
            logger.info(f"Displayed {len(matches)} results for '{word}'")
            await state.set_state(TranslateState.success)
            await handle_success_state(message, state)
        except TranslationError as e:
            logger.warning(f"Translation error: {e}")
            raise e
        except Exception as e:
            logger.exception("Unexpected error during translation")
            raise e
    except Exception as e:
        await message.answer(str(e))
        await state.set_state(TranslateState.error)
        await handle_error_state(message, state)
