from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from loguru import logger

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
async def handle_word_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    from_lang = data.get("from_lang")
    to_lang = data.get("to_lang")
    from_lang_name = get_lang_name(from_lang)
    to_lang_name = get_lang_name(to_lang)

    word = message.text.strip()

    logger.info(f"Translating '{word}' from {from_lang} to {to_lang}")

    # Placeholder: here will be Glosbe API call
    try:
        translations = ["Example1", "Example2"]  # Replace with actual result
        if translations:
            result = "\n".join(f"- {t}" for t in translations)
            await message.answer(
                f'Translation of "{word}" from {from_lang_name} to {to_lang_name}:\n{result}'
            )
        else:
            await message.answer("No translation found.")
    except Exception as e:
        logger.exception("Error during translation")
        await message.answer(
            "⚠️ An error occurred while translating. Please try again later."
        )

    await state.clear()
