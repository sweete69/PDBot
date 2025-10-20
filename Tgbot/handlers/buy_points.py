from aiogram import Router, types, F
from Tgbot.keyboards.buy_points import get_buy_points

router = Router()

@router.callback_query(F.data=="buy_points")
async def buy_points_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "⭐️ Покупка поинтов\n\n"
        "Здесь будет информация о покупке поинтов...",
        reply_markup=get_buy_points()
    )