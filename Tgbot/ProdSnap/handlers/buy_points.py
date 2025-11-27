from aiogram import Router, types, F
# >>> ПРАВИЛЬНЫЙ ИМПОРТ ИЗ КЛАВИАТУРЫ <<<
from ProdSnap.keyboards.buy_points import get_buy_points 

router = Router()

@router.callback_query(F.data=="buy_points")
async def buy_points_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "⭐️ Покупка поинтов\n\n"
        "Выберите желаемое количество поинтов:",
        # Используем импортированную функцию клавиатуры
        reply_markup=get_buy_points() 
    )
    # Обязательно завершаем запрос, чтобы кнопка перестала "грузиться"
    await callback.answer()
    
# Пример обработчика для реальной покупки (добавьте по мере необходимости)
@router.callback_query(F.data.startswith("buy_"))
async def process_buy_points(callback: types.CallbackQuery):
    # Здесь будет логика обработки платежа
    points = callback.data.split('_')[1] # Например, 100
    await callback.answer(f"Запрос на покупку {points} поинтов отправлен!", show_alert=True)
    # Далее можно перенаправить пользователя на оплату