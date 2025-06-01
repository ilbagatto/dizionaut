from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from dizionaut.handlers.translate import language_keyboard
from ..states import TranslateState

router = Router()

@router.message(Command("start"))
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

@router.callback_query(F.data == "start_translation", TranslateState.welcome)
async def start_from_welcome(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Please select source language:", reply_markup=language_keyboard("from"))
    await state.set_state(TranslateState.from_lang)
    await callback.answer()
