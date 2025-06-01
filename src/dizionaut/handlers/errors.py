
from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from  .common import start
from ..states import TranslateState

router = Router()

@router.message(TranslateState.error)
async def handle_error_state(message: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔁 Restart", callback_data="restart")],
            [InlineKeyboardButton(text="✏️ Try another word", callback_data="retry_word")],
        ]
    )

    await message.answer(
        "❗ What would you like to do?",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "retry_word")
async def retry_word(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(TranslateState.word)
    await callback.message.answer("✏️ Please enter another word.")

@router.callback_query(F.data == "restart")
async def restart(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await start(callback.message, state)
