
from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from  .common import start, restart_keyboard
from ..states import TranslateState

router = Router()

@router.message(TranslateState.success)
async def handle_success_state(message: Message, state: FSMContext):

    await message.answer(
        "❓ What would you like to do?",
        reply_markup=restart_keyboard
    )

