"""
Handlers for starting or restarting the translation flow.

This module covers the /start command, "retry word" callback,
and full restart callback.
"""

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ..states import TranslateState
from .common import start

router = Router()


@router.message(Command("start"))
async def handle_start_command(message: types.Message, state: FSMContext):
    """
    Handle the /start command by invoking the shared start routine.

    Args:
        message (types.Message): Telegram message object.
        state (FSMContext): FSM context for the current user.
    """
    await start(message, state)


@router.callback_query(F.data == "retry_word")
async def retry_word(callback: CallbackQuery, state: FSMContext):
    """
    Handle the "Try another word" button.

    Transitions the state machine to `word` input.

    Args:
        callback (CallbackQuery): Callback query object from Telegram.
        state (FSMContext): FSM context.
    """
    await callback.answer()
    await state.set_state(TranslateState.word)
    await callback.message.answer("✏️ Please enter another word.")


@router.callback_query(F.data == "restart")
async def restart(callback: CallbackQuery, state: FSMContext):
    """
    Handle the "Restart" button.

    Clears previous state and invokes the shared start routine.

    Args:
        callback (CallbackQuery): Callback query object from Telegram.
        state (FSMContext): FSM context.
    """
    await callback.answer()
    await start(callback.message, state)
