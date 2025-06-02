"""
Handler for the success state in the translation flow.

Provides the user with options to restart or translate another word.
"""

from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .common import start, restart_keyboard
from ..states import TranslateState

router = Router()


@router.message(TranslateState.success)
async def handle_success_state(message: Message, state: FSMContext):
    """
    Handle messages received when the bot is in the success state.

    Presents the user with restart and retry options.

    Args:
        message (Message): Incoming user message.
        state (FSMContext): Current FSM context.
    """
    await message.answer(
        "What would you like to do next?",
        reply_markup=restart_keyboard
    )
