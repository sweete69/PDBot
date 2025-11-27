from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InputFile
import os
import asyncio

# --- ИМПОРТ КЛАВИАТУР И СОСТОЯНИЙ (Исправление NameError) ---
from ProdSnap.keyboards.main_menu import get_main_menu_kb
from ProdSnap.keyboards.banner_photo.create_banner import get_create_banner_kb
from ProdSnap.keyboards.banner_photo.create_photo import get_create_photo_kb
from ProdSnap.keyboards.banner_photo.create_by_text import get_create_by_text_kb
from ProdSnap.utils.states import CreateBanner

# --- ИМПОРТ AI-СЕРВИСОВ (Исправление ModuleNotFoundError и ImportError) ---

# 1. ТЕКСТ (GEMINI)
# Используем существующую функцию Gemini для текста (переименована в generate_text_sync)
from ProdSnap.ai.gemini_service import (
    generate_description_from_text as generate_text_sync, 
)

# 2. ИЗОБРАЖЕНИЯ (HUGGING FACE)
# Эти функции должны находиться в ProdSnap.ai.image_generator.py
from ProdSnap.ai.image_generator import (
    generate_image as generate_image_sync,
    generate_image_from_photo as generate_image_from_photo_sync,
)

router = Router()

@router.callback_query(F.data == "create_banner")
async def create_banner_callback(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text="🎨 Создание рекламного баннера\n\nВыберите способ создания:",
        reply_markup=get_create_banner_kb()
    )
    await callback.answer()

@router.callback_query(F.data == "create_photo")
async def upload_photo_banner(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CreateBanner.waiting_for_photo)
    await callback.message.edit_text(
        "📸 Создание баннера по фото\n\nЗагрузите фото товара:",
        reply_markup=get_create_photo_kb(),
    )
    await callback.answer() 

@router.callback_query(F.data == "create_photo_by_text")
async def create_text_banner(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CreateBanner.waiting_for_text)
    await callback.message.edit_text(
        "✍️ Создание баннера по тексту\n\nВведите описание товара для генерации баннера:",
        reply_markup=get_create_by_text_kb(),
    )
    await callback.answer()

@router.message(CreateBanner.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    user_prompt = message.text
    if not user_prompt or len(user_prompt.strip()) == 0:
        await message.answer("❌ Пожалуйста, введите описание товара.")
        return

    processing_msg = await message.answer("⏳ Генерируем баннер... Это может занять 10-30 секунд.")

    try:
        # Асинхронный вызов синхронных функций (Gemini Text)
        banner_text = await asyncio.to_thread(generate_text_sync, user_prompt)
        # Асинхронный вызов синхронных функций (Hugging Face Image)
        banner_image_path = await asyncio.to_thread(generate_image_sync, user_prompt)

        await processing_msg.delete()

        if banner_image_path and os.path.exists(banner_image_path):
            await message.answer(f"📋 **Рекламный текст:**\n\n{banner_text}", parse_mode="Markdown")
            
            with open(banner_image_path, 'rb') as photo:
                await message.answer_photo(
                    photo,
                    caption="🎨 Ваш рекламный баннер готов!"
                )
            
            try:
                os.remove(banner_image_path)
            except:
                pass
        else:
            await message.answer("❌ Не удалось создать изображение, но вот рекламный текст:\n\n" + banner_text)

    except Exception as e:
        await processing_msg.delete()
        await message.answer(f"❌ Произошла ошибка при генерации: {str(e)}")

    finally:
        await state.clear()
        await message.answer("🏠 Главное меню", reply_markup=get_main_menu_kb())

@router.message(CreateBanner.waiting_for_photo)
async def process_photo(message: types.Message, state: FSMContext, bot: Bot):
    if not message.photo:
        await message.answer("❌ Пожалуйста, отправьте фото товара.")
        return

    photo = message.photo[-1]
    file_path = f"temp/{message.from_user.id}_{photo.file_id}.jpg"
    os.makedirs("temp", exist_ok=True)
    
    processing_msg = await message.answer("⏳ Обрабатываем фото и генерируем баннер...")
    
    try:
        await bot.download(photo, destination=file_path)
        
        # Генерируем текст и изображение
        banner_text = await asyncio.to_thread(generate_text_sync, "товар на фото")
        
        banner_image_path = await asyncio.to_thread(
            generate_image_from_photo_sync, file_path, "рекламный баннер"
        )
        
        await processing_msg.delete()

        if banner_image_path and os.path.exists(banner_image_path):
            await message.answer(f"📋 **Рекламный текст:**\n\n{banner_text}", parse_mode="Markdown")
            
            with open(banner_image_path, 'rb') as photo_file:
                await message.answer_photo(
                    photo_file,
                    caption="🎨 Ваш рекламный баннер готов!"
                )
            
            try:
                os.remove(file_path)
                os.remove(banner_image_path)
            except:
                pass
        else:
            await message.answer("❌ Не удалось обработать фото, но вот рекламный текст:\n\n" + banner_text)
            
    except Exception as e:
        await processing_msg.delete()
        await message.answer(f"❌ Произошла ошибка при обработке: {e}")
        print(f"Error: {e}")
        
    finally:
        await state.clear()
        await message.answer("🏠 Главное меню", reply_markup=get_main_menu_kb())