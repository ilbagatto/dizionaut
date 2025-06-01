from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from dizionaut.handlers.translate import language_keyboard
from ..states import TranslateState
from .common import start

router = Router()

@router.message(Command("start"))
async def handle_start_command(message: types.Message, state: FSMContext):
    await start(message, state)

@router.callback_query(F.data == "start_translation", TranslateState.welcome)
async def start_from_welcome(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Please select source language:", reply_markup=language_keyboard("from"))
    await state.set_state(TranslateState.from_lang)
    await callback.answer()


@router.callback_query(F.data == "restart")
async def handle_restart(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await start(callback.message, state)