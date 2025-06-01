from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.filters import Command
from loguru import logger

from .errors import handle_error_state

from ..services.api import TranslationError, translate_text

from ..states import TranslateState

router = Router()

# Supported languages with flags
LANGUAGES = [
    ("🇷🇺 Russian", "ru"),
    ("🇬🇧 English", "en"),
    ("🇩🇪 German", "de"),
    ("🇫🇷 French", "fr"),
    ("🇮🇹 Italian", "it"),
    ("🇪🇸 Spanish", "es"),
    ("🇧🇬 Bulgarian", "bg"),
    ("🇷🇸 Serbian", "sr"),
]


def get_lang_name(lang_code):
    lang_name = next((name for name, code in LANGUAGES if code == lang_code), lang_code)
    return lang_name


def language_keyboard(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"{prefix}:{code}")]
            for name, code in LANGUAGES
        ]
    )


@router.message(Command("translate"))
async def start_translation(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Please select source language:", reply_markup=language_keyboard("from")
    )
    await state.set_state(TranslateState.from_lang)


@router.callback_query(F.data.startswith("from:"))
async def handle_from_lang(callback: types.CallbackQuery, state: FSMContext):
    lang_code = callback.data.split(":")[1]
    lang_name = get_lang_name(lang_code)
    await state.update_data(from_lang=lang_code)
    await callback.message.edit_text(
        f"Source language: {lang_name}\nNow select target language:",
        reply_markup=language_keyboard("to"),
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
        f"Source language: {from_lang_name}\nTarget language: {to_lang_name}\nEnter the word or phrase you want to translate:"
    )
    await state.set_state(TranslateState.word)
    await callback.answer()


@router.message(TranslateState.word)
async def handle_word_input(message: Message, state: FSMContext):
    data = await state.get_data()
    from_lang = data.get("from_lang")
    to_lang = data.get("to_lang")
    word = message.text.strip()

    logger.info(f"User input: '{word}' ({from_lang} → {to_lang})")

    try:
        matches = await translate_text(from_lang, to_lang, word)

        formatted = "\n".join(
            f"• {m['translation']} ({int(m['match'] * 100)}%)" for m in matches
        )

        await message.answer(f"🔤 Translations for '{word}':\n{formatted}")
        logger.info(f"Displayed {len(matches)} results for '{word}'")

    except TranslationError as e:
        logger.warning(f"Translation error: {e}")
        await message.answer(str(e))
        await state.set_state(TranslateState.error)
        await handle_error_state(message, state)
    except Exception:
        logger.exception("Unexpected error during translation")
        await state.set_state(TranslateState.error)
        await handle_error_state(message, state)

    
