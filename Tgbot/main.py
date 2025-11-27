import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from ProdSnap.config import BOT_TOKEN

# Импорт роутеров из основной папки handlers
from ProdSnap.handlers import start
from ProdSnap.handlers import main_menu
from ProdSnap.handlers import policy
from ProdSnap.handlers import buy_points
# >>> ИМПОРТ РОУТЕРОВ ИЗ ПОДПАПКИ banner <<<
from ProdSnap.handlers.banner import create_description # Проверьте это
from ProdSnap.handlers.banner import create_banner      # Проверьте это

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(main_menu.router)
    dp.include_router(policy.router)
    dp.include_router(buy_points.router)
    # >>> РЕГИСТРАЦИЯ РОУТЕРОВ <<<
    dp.include_router(create_description.router)
    dp.include_router(create_banner.router)

    await bot.delete_webhook(drop_pending_updates=True)
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())