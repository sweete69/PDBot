from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_kb():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
                [InlineKeyboardButton(text="🌇 Создать баннер 🌇", callback_data="create_banner")],
                [InlineKeyboardButton(text="📝 Создать описание 📝", callback_data="create_description")],
                [InlineKeyboardButton(text="📄 Политика пользования 📄", callback_data="policy")],
                [InlineKeyboardButton(text="⭐️ Купить поинты ⭐️", callback_data="buy_points")],
        ]
    )
    return keyboard