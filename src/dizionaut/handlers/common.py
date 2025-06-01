# dizionaut/handlers/common.py

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..states import TranslateState

async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(TranslateState.welcome)
    await message.answer(
        "👋 Welcome to Dizionaut!\n"
        "I can help you translate words and expressions.\n"
        "Tap the button below to begin.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🌍 Translate", callback_data="start_translation")]
            ]
        )
    )
