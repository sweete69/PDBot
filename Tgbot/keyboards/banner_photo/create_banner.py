from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_create_banner_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📸 Загрузить фото товара 📸", callback_data="create_photo")],
            [InlineKeyboardButton(text="✏️ Создать баннер по тексту ✏️", callback_data="create_photo_by_text")],
            [InlineKeyboardButton(text="🏠 В меню 🏠", callback_data="main_menu")],
        ],
        resize_keyboard=True
    )