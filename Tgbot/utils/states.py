from aiogram.fsm.state import State, StatesGroup

class CreateBanner(StatesGroup):
    waiting_for_photo = State()
    waiting_for_text = State()

class CreateDescription(StatesGroup):
    waiting_for_photo = State()
    waiting_for_text = State()