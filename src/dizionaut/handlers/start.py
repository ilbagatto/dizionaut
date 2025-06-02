from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ..states import TranslateState
from .common import start

router = Router()


@router.message(Command("start"))
async def handle_start_command(message: types.Message, state: FSMContext):
    await start(message, state)



@router.callback_query(F.data == "retry_word")
async def retry_word(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(TranslateState.word)
    await callback.message.answer("✏️ Please enter another word.")


@router.callback_query(F.data == "restart")
async def restart(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await start(callback.message, state)
