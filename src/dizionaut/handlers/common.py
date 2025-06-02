# dizionaut/handlers/common.py

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..states import TranslateState
from ..utils import format_ml

restart_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Restart", callback_data="restart")],
        [InlineKeyboardButton(text="✏️ Try another word", callback_data="retry_word")],
    ]
)


async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(TranslateState.welcome)
    await message.answer(
        format_ml("""
        👋 Welcome to Dizionaut!
        I can help you translate words.
    
        Tap the button below to begin.
        """
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🌍 Translate", callback_data="translate")]
            ]
        ),
    )
