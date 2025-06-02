"""
Translation workflow handlers for managing language selection, word input,
and displaying translation results.

This module controls the main user flow: selecting source/target language,
entering a word, and viewing results from the translation API.
"""

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

from dizionaut.utils import LANGUAGES
from dizionaut.utils import get_lang_name

from ..services.scoring import quality_marker
from .success import handle_success_state
from ..utils import format_translation_result
from .errors import handle_error_state
from ..services.api import TranslationError, translate_text
from ..states import TranslateState

router = Router()


def language_keyboard(prefix: str, excluded_code: str = None) -> InlineKeyboardMarkup:
    """
    Generate an inline keyboard for selecting a language.

    Args:
        prefix (str): Callback data prefix (e.g., "from", "to").
        excluded_code (str, optional): Language code to exclude.

    Returns:
        InlineKeyboardMarkup: Keyboard with language options.
    """

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
    """
    Start the translation process by asking the user for source language.

    Args:
        callback (CallbackQuery): User-initiated callback.
        state (FSMContext): FSM state context.
    """
    await state.clear()
    await callback.message.edit_text(
        "Please select source language:", reply_markup=language_keyboard("from")
    )
    await state.set_state(TranslateState.from_lang)
    await callback.answer()


@router.callback_query(F.data.startswith("from:"))
async def handle_from_lang(callback: CallbackQuery, state: FSMContext):
    """
    Handle selection of source language.

    Args:
        callback (CallbackQuery): Callback with source language.
        state (FSMContext): FSM context.
    """
    from_lang = callback.data.split(":")[1]
    await state.update_data(from_lang=from_lang)
    await callback.message.edit_text(
        "Now select target language:",
        reply_markup=language_keyboard("to", excluded_code=from_lang),
    )
    await state.set_state(TranslateState.to_lang)
    await callback.answer()


@router.callback_query(F.data.startswith("to:"))
async def handle_to_lang(callback: CallbackQuery, state: FSMContext):
    """
    Handle selection of target language and prompt for the word.

    Args:
        callback (CallbackQuery): Callback with target language.
        state (FSMContext): FSM context.
    """
    to_lang = callback.data.split(":")[1]
    await state.update_data(to_lang=to_lang)
    await callback.message.edit_text("✏️ Please enter a word to translate:")
    await state.set_state(TranslateState.word)
    await callback.answer()


@router.message(TranslateState.word)
async def handle_word(message: Message, state: FSMContext):
    """
    Receive the word from the user and trigger translation.

    Args:
        message (Message): User input message.
        state (FSMContext): FSM context.
    """
    await state.update_data(word=message.text)
    await handle_text_input(message, state)


async def handle_text_input(message: Message, state: FSMContext):
    """
    Fetch translations and show the results to the user.

    Handles success and error states.

    Args:
        message (Message): Message with the word.
        state (FSMContext): FSM context.
    """
    data = await state.get_data()
    from_lang = data.get("from_lang")
    to_lang = data.get("to_lang")
    phrase = data.get("word")

    try:
        translations = await translate_text(from_lang, to_lang, phrase)
        if not translations:
            raise TranslationError("No translations found.")

        result = format_translation_result(
            translations,
            from_lang,
            to_lang,
            lang_name_fn=get_lang_name,
            quality_marker_fn=quality_marker,
        )

        await state.set_state(TranslateState.success)
        await message.answer(result)
        await handle_success_state(message, state)

    except TranslationError as e:
        logger.warning(f"Translation error: {e}")
        await state.set_state(TranslateState.error)
        await message.answer("⚠️ Something went wrong while translating.")
        await handle_error_state(message, state)
