from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from Tgbot.keyboards.main_menu import get_main_menu_kb
from Tgbot.utils.states import CreateBanner
from Tgbot.keyboards.banner_photo.create_banner import get_create_banner_kb
from Tgbot.keyboards.banner_photo.create_photo import get_create_photo_kb
from Tgbot.keyboards.banner_photo.create_by_text import get_create_by_text_kb

router = Router()

@router.callback_query(F.data == "create_banner")
async def create_banner_callback(callback: types.CallbackQuery):
    # Редактируем существующее сообщение вместо удаления
    await callback.message.edit_text(
        text="🔍 Создание баннера\n\nВыберите способ создания:",
        reply_markup=get_create_banner_kb()
    )
    await callback.answer()

@router.callback_query(F.data=="create_photo")
async def upload_photo_banner(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CreateBanner.waiting_for_photo)
    await callback.message.edit_text(
        "📸 Загрузка фото товара\n\n"
        "Пожалуйста, загрузите фото товара:",
        reply_markup=get_create_photo_kb(),
    )

@router.callback_query(F.data=="create_photo_by_text")
async def create_text_banner(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CreateBanner.waiting_for_text)
    await callback.message.edit_text(
        "✍️ Создание баннера по тексту\n\n"
        "Введите текст для создания баннера:",
        reply_markup=get_create_by_text_kb(),
    )

# Обработчики для состояний (заглушки для коллег)
@router.message(CreateBanner.waiting_for_photo)
async def process_photo(message: types.Message, state: FSMContext):
    # Здесь коллеги добавят логику обработки фото
    await message.answer("Фото получено! Создание баннеров в разработке...")
    await state.clear()
    await message.answer("🏠 Главное меню",
                        reply_markup=get_main_menu_kb())

@router.message(CreateBanner.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    # Здесь коллеги добавят логику обработки текста
    await message.answer("Текст получен! Создание баннеров в разработке...")
    await state.clear()
    await message.answer("🏠 Главное меню",
                        reply_markup=get_main_menu_kb())