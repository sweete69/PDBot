from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_kb() -> InlineKeyboardMarkup:
    """
    Главное меню бота.
    Содержит основные сценарии, которые обрабатывают соответствующие роутеры.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎨 Создать баннер",
                    callback_data="create_banner",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 Описание товара",
                    callback_data="create_description",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⭐️ Купить поинты",
                    callback_data="buy_points",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 Политика сервиса",
                    callback_data="policy",
                )
            ],
        ],
        resize_keyboard=True,
    )
