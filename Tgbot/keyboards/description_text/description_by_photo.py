from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_description_by_photo_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В меню 🏠", callback_data="main_menu")],
        ],
        resize_keyboard=True
    )