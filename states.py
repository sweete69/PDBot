from aiogram.fsm.state import State, StatesGroup


class BannerFlow(StatesGroup):
    waiting_input = State()


class DescByTextFlow(StatesGroup):
    waiting_text = State()


class DescByPhotoFlow(StatesGroup):
    waiting_photo = State()


class DescResultFlow(StatesGroup):
    viewing = State()


class BannerResultFlow(StatesGroup):
    viewing = State()