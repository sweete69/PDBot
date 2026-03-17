from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

CB_MENU_MAIN = "menu:main"
CB_MENU_BANNER = "menu:banner"
CB_MENU_DESC = "menu:desc"
CB_MENU_BUY = "menu:buy"
CB_MENU_POLICY = "menu:policy"

CB_DESC_BY_PHOTO = "desc:photo"
CB_DESC_BY_TEXT = "desc:text"

CB_DESC_REGEN = "desc:regen"
CB_DESC_BACK = "desc:back"

CB_BANNER_REGEN = "banner:regen"
CB_BANNER_BACK = "banner:back"

CB_BUY_PREFIX = "buy:"


def main_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🎨 Создать баннер", callback_data=CB_MENU_BANNER)
    kb.button(text="📝 Описание товара", callback_data=CB_MENU_DESC)
    kb.button(text="⭐ Купить поинты", callback_data=CB_MENU_BUY)
    kb.button(text="📄 Политика сервиса", callback_data=CB_MENU_POLICY)
    kb.adjust(1)
    return kb.as_markup()


def banner_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 В меню", callback_data=CB_MENU_MAIN)
    kb.adjust(1)
    return kb.as_markup()


def desc_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✏️ По тексту", callback_data=CB_DESC_BY_TEXT)
    kb.button(text="📸 По фото", callback_data=CB_DESC_BY_PHOTO)
    kb.button(text="🏠 В меню", callback_data=CB_MENU_MAIN)
    kb.adjust(1)
    return kb.as_markup()


def buy_points_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="10 поинтов", callback_data=f"{CB_BUY_PREFIX}10")
    kb.button(text="50 поинтов", callback_data=f"{CB_BUY_PREFIX}50")
    kb.button(text="100 поинтов", callback_data=f"{CB_BUY_PREFIX}100")
    kb.button(text="🏠 В меню", callback_data=CB_MENU_MAIN)
    kb.adjust(1)
    return kb.as_markup()


def back_to_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 В меню", callback_data=CB_MENU_MAIN)
    kb.adjust(1)
    return kb.as_markup()


def desc_result_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data=CB_DESC_BACK)
    kb.button(text="🔁 Сгенерировать новое", callback_data=CB_DESC_REGEN)
    kb.adjust(2)
    return kb.as_markup()


def banner_result_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data=CB_BANNER_BACK)
    kb.button(text="🔁 Новый баннер", callback_data=CB_BANNER_REGEN)
    kb.adjust(2)
    return kb.as_markup()


# совместимость, если где-то ещё используется
result_kb = back_to_menu_kb