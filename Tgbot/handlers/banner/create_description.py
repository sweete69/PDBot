from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from Tgbot.keyboards.main_menu import get_main_menu_kb
from Tgbot.keyboards.description_text.create_description import get_create_description_kb
from Tgbot.keyboards.description_text.description_by_photo import get_description_by_photo_kb
from Tgbot.keyboards.description_text.description_by_text import get_description_by_text_kb
from Tgbot.utils.states import CreateDescription

router = Router()

@router.callback_query(F.data=="create_description")
async def create_description_banner(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📝 Создание описания товара\n\nВыберите способ создания:",
        reply_markup=get_create_description_kb()
    )

@router.callback_query(F.data=="create_description_by_photo")
async def create_description_by_photo(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CreateDescription.waiting_for_photo)
    await callback.message.edit_text(
        "📸 Создание описания по фото товара\n\n"
        "Пожалуйста, загрузите фото товара:",
        reply_markup=get_description_by_photo_kb(),
    )

@router.callback_query(F.data=="create_description_text")
async def create_text_banner(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CreateDescription.waiting_for_text)
    await callback.message.edit_text(
        "✍️ Создание описания по вашему тексту\n\n"
        "Введите текст:",
        reply_markup=get_description_by_text_kb(),
    )

# Обработчики для состояний (заглушки для коллег)
@router.message(CreateDescription.waiting_for_photo)
async def process_photo(message: types.Message, state: FSMContext):
    # Здесь коллеги добавят логику обработки фото
    await message.answer("Фото получено! Создание баннеров в разработке...")
    await state.clear()
    await message.answer("Возвращаем в главное меню:",
                        reply_markup=get_main_menu_kb())

@router.message(CreateDescription.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    # Здесь коллеги добавят логику обработки текста
    await message.answer("Текст получен! Создание баннеров в разработке...")
    await state.clear()
    await message.answer("Баннер создан! Возвращаем в главное меню:",
                        reply_markup=get_main_menu_kb())
