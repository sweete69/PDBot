from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InputFile
import os
import asyncio

from Tgbot.keyboards.main_menu import get_main_menu_kb
from Tgbot.keyboards.banner_photo.create_banner import get_create_banner_kb
from Tgbot.keyboards.banner_photo.create_photo import get_create_photo_kb
from Tgbot.keyboards.banner_photo.create_by_text import get_create_by_text_kb
from Tgbot.utils.states import CreateBanner

from Tgbot.ai.text_generator import generate_text
from Tgbot.ai.image_generator import generate_image, generate_image_from_photo

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

@router.callback_query(F.data == "create_photo_by_text")
async def create_text_banner(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CreateBanner.waiting_for_text)
    await callback.message.edit_text(
        "✍️ Создание баннера по тексту\n\nВведите описание товара для генерации баннера:",
        reply_markup=get_create_by_text_kb(),
    )

@router.message(CreateBanner.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    user_prompt = message.text
    if not user_prompt or len(user_prompt.strip()) == 0:
        await message.answer("❌ Пожалуйста, введите описание товара.")
        return

    # Отправляем сообщение о начале генерации
    processing_msg = await message.answer("⏳ Генерируем баннер... Это может занять 10-30 секунд.")

    try:
        # Генерируем рекламный текст
        banner_text = generate_text(user_prompt, style="ad")
        
        # Генерируем изображение (синхронная функция в отдельном потоке)
        import asyncio
        loop = asyncio.get_event_loop()
        banner_image_path = await loop.run_in_executor(None, generate_image, user_prompt)

        # Удаляем сообщение о обработке
        await processing_msg.delete()

        if banner_image_path and os.path.exists(banner_image_path):
            # Отправляем текст и изображение
            await message.answer(f"📋 **Рекламный текст:**\n\n{banner_text}")
            
            # Отправляем изображение
            with open(banner_image_path, 'rb') as photo:
                await message.answer_photo(
                    photo,
                    caption="🎨 Ваш рекламный баннер готов!"
                )
            
            # Удаляем временный файл
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
async def process_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("❌ Пожалуйста, отправьте фото товара.")
        return

    photo = message.photo[-1]
    file_path = f"temp/{message.from_user.id}_{photo.file_id}.jpg"
    os.makedirs("temp", exist_ok=True)
    
    processing_msg = await message.answer("⏳ Обрабатываем фото и генерируем баннер...")
    
    try:
        await photo.download(file_path)
        
        # Генерируем текст и изображение
        banner_text = generate_text("товар на фото", style="ad")
        
        import asyncio
        loop = asyncio.get_event_loop()
        banner_image_path = await loop.run_in_executor(
            None, generate_image_from_photo, file_path, "рекламный баннер"
        )
        
        await processing_msg.delete()

        if banner_image_path and os.path.exists(banner_image_path):
            await message.answer(f"📋 **Рекламный текст:**\n\n{banner_text}")
            
            with open(banner_image_path, 'rb') as photo_file:
                await message.answer_photo(
                    photo_file,
                    caption="🎨 Ваш рекламный баннер готов!"
                )
            
            # Удаляем временные файлы
            try:
                os.remove(file_path)
                os.remove(banner_image_path)
            except:
                pass
        else:
            await message.answer("❌ Не удалось обработать фото, но вот рекламный текст:\n\n" + banner_text)
            
    except Exception as e:
        await processing_msg.delete()
        await message.answer("⏳ Обрабатываем фото и генерируем баннер...")
        print(f"Error: {e}")
        
    finally:
        await state.clear()
        await message.answer("🏠 Главное меню", reply_markup=get_main_menu_kb())