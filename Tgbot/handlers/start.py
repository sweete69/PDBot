from aiogram import Router, types
from aiogram.filters import Command
from Tgbot.keyboards.main_menu import get_main_menu_kb

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я помогу тебе создать крутые карточки товаров.\n\n"
        "Выбери действие в главном меню:",
        reply_markup=get_main_menu_kb()
    )