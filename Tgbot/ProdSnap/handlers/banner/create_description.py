import os
import asyncio
from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from ProdSnap.keyboards.main_menu import get_main_menu_kb
from ProdSnap.keyboards.description_text.create_description import get_create_description_kb
from ProdSnap.keyboards.description_text.description_by_photo import get_description_by_photo_kb
from ProdSnap.keyboards.description_text.description_by_text import get_description_by_text_kb
from ProdSnap.utils.states import CreateDescription

from ProdSnap.ai.gemini_service import (
    generate_description_from_text as generate_text_sync,
    generate_description_from_image as generate_image_desc_sync
)

router = Router()

@router.callback_query(F.data == "create_description")
async def create_description_banner(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📝 Создание описания товара\n\nВыберите способ создания:",
        reply_markup=get_create_description_kb()
    )
    await callback.answer()

@router.callback_query(F.data == "create_description_by_photo")
async def create_description_by_photo(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CreateDescription.waiting_for_photo)
    await callback.message.edit_text(
        "📸 Создание описания по фото товара\n\n"
        "Загрузите фото товара. Вы также можете добавить подпись к фото с пожеланиями (например: 'сделай описание для мам' или 'акцент на скидке').",
        reply_markup=get_description_by_photo_kb(),
    )
    await callback.answer()

@router.callback_query(F.data == "create_description_text")
async def create_text_banner(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CreateDescription.waiting_for_text)
    await callback.message.edit_text(
        "✍️ Создание описания по тексту\n\n"
        "Введите название товара и любые пожелания (например: 'Красные кеды Nike, стиль дерзкий, для молодежи'):",
        reply_markup=get_description_by_text_kb(),
    )
    await callback.answer()

# Обработка фото для описания
@router.message(CreateDescription.waiting_for_photo)
async def process_photo(message: types.Message, state: FSMContext, bot: Bot):
    if not message.photo:
        await message.answer("❌ Пожалуйста, отправьте именно фото (сжатое), а не файл.")
        return

    status_msg = await message.answer("⏳ Анализирую фото и подбираю лучший стиль описания...")

    os.makedirs("temp", exist_ok=True)
    photo = message.photo[-1]
    file_id = photo.file_id
    file_path = f"temp/{message.from_user.id}_{file_id}.jpg"

    try:
        await bot.download(photo, destination=file_path)
        
        # Получаем caption (текст под фото)
        caption_text = message.caption if message.caption else ""

        description = await asyncio.to_thread(generate_image_desc_sync, file_path, caption_text)

        await status_msg.delete()
        # УБРАН parse_mode="Markdown", чтобы избежать ошибок и лишних символов
        await message.answer(f"📋 **Описание товара:**\n\n{description}")

    except Exception as e:
        await status_msg.edit_text(f"❌ Произошла ошибка: {e}")

    finally:
        await state.clear()
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        await message.answer("🏠 Главное меню", reply_markup=get_main_menu_kb())

# Обработка текста для описания
@router.message(CreateDescription.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    user_prompt = message.text
    status_msg = await message.answer("⏳ Придумываю уникальное описание...")

    try:
        description = await asyncio.to_thread(generate_text_sync, user_prompt)

        await status_msg.delete()
        # УБРАН parse_mode="Markdown"
        await message.answer(
            f"📋 Описание товара:\n\n{description}\n\n"
            f"💡 Вы можете отредактировать описание под свои нужды."
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ Произошла ошибка: {e}")

    finally:
        await state.clear()
        await message.answer("🏠 Главное меню", reply_markup=get_main_menu_kb())