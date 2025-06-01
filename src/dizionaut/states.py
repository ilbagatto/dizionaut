from aiogram.fsm.state import State, StatesGroup


class TranslateState(StatesGroup):
    welcome = State()
    from_lang = State()
    to_lang = State()
    word = State()