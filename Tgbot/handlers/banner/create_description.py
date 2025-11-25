from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
import os

from Tgbot.keyboards.main_menu import get_main_menu_kb
from Tgbot.keyboards.description_text.create_description import get_create_description_kb
from Tgbot.keyboards.description_text.description_by_photo import get_description_by_photo_kb
from Tgbot.keyboards.description_text.description_by_text import get_description_by_text_kb
from Tgbot.utils.states import CreateDescription

from Tgbot.ai.text_generator import generate_text

router = Router()

@router.callback_query(F.data == "create_description")
async def create_description_banner(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📝 Создание описания товара\n\nВыберите способ создания:",
        reply_markup=get_create_description_kb()
    )

@router.callback_query(F.data == "create_description_by_photo")
async def create_description_by_photo(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CreateDescription.waiting_for_photo)
    await callback.message.edit_text(
        "📸 Создание описания по фото товара\n\n"
        "Загрузите фото товара:",
        reply_markup=get_description_by_photo_kb(),
    )

@router.callback_query(F.data == "create_description_text")
async def create_text_banner(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CreateDescription.waiting_for_text)
    await callback.message.edit_text(
        "✍️ Создание описания по тексту\n\n"
        "Введите название или описание товара:",
        reply_markup=get_description_by_text_kb(),
    )

# Обработка фото для описания
@router.message(CreateDescription.waiting_for_photo)
async def process_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("❌ Пожалуйста, отправьте фото товара.")
        return

    await message.answer("⏳ Анализируем фото и генерируем описание...")
    
    # Генерируем описание на основе фото
    description = generate_text("товар на фото", style="description")
    
    await message.answer(
        f"📋 Описание товара:\n\n{description}\n\n"
        f"💡 Вы можете отредактировать описание под свои нужды."
    )
    
    await state.clear()
    await message.answer("🏠 Главное меню", reply_markup=get_main_menu_kb())

# Обработка текста для описания
@router.message(CreateDescription.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    user_prompt = message.text
    await message.answer("⏳ Генерируем описание товара...")
    
    description = generate_text(user_prompt, style="description")
    
    await message.answer(
        f"📋 Описание товара:\n\n{description}\n\n"
        f"💡 Вы можете отредактировать описание под свои нужды."
    )
    
    await state.clear()
    await message.answer("🏠 Главное меню", reply_markup=get_main_menu_kb())