from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_buy_points():
    """
    Возвращает клавиатуру для меню покупки поинтов.
    """
    # Здесь должны быть кнопки для покупки (например, 100, 500, 1000 поинтов)
    # Сейчас добавим только кнопку "Назад"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="100 🌟 (100 руб.)", callback_data="buy_100_points")],
            [InlineKeyboardButton(text="500 🌟 (450 руб.)", callback_data="buy_500_points")],
            [InlineKeyboardButton(text="🏠 В меню 🏠", callback_data="main_menu")],
        ],
        resize_keyboard=True
    )