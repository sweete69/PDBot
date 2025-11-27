from aiogram import Router, types, F
from ProdSnap.keyboards.main_menu import get_main_menu_kb

router = Router()

@router.callback_query(F.data=="main_menu")
async def main_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🏠 Главное меню",
        reply_markup=get_main_menu_kb(),
    )