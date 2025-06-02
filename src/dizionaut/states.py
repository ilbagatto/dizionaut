"""
Defines the finite state machine (FSM) states used in the translation workflow.
"""

from aiogram.fsm.state import State, StatesGroup


class TranslateState(StatesGroup):
    """
    State group representing the stages of user interaction with the bot
    during the translation process.
    """
    welcome = State()     # Initial greeting or start state
    from_lang = State()   # Language to translate from
    to_lang = State()     # Language to translate to
    word = State()        # The word or phrase to be translated
    error = State()       # Error state (e.g., invalid input)
    success = State()     # Final state after successful translation
