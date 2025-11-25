from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_create_description_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📸 Создать описание по фото 📸", callback_data="create_description_by_photo")],
            [InlineKeyboardButton(text="✏️ Ваш текст ✏️", callback_data="create_description_text")],
            [InlineKeyboardButton(text="🏠 В меню 🏠", callback_data="main_menu")],        ],
        resize_keyboard=True
    )