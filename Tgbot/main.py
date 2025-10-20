import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.start import router as start_router
from handlers.main_menu import router as main_menu_router
from Tgbot.handlers.banner.create_banner import router as create_banner_router
from Tgbot.handlers.banner.create_description import router as create_description_router
from handlers.policy import router as policy_router
from handlers.buy_points import router as buy_points_router

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token="8229333698:AAGcU3pYqoI-PNLTn4ZdUHLqu4kl4yJQ5fQ")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрируем роутеры
    dp.include_router(start_router)
    dp.include_router(main_menu_router)
    dp.include_router(create_banner_router)
    dp.include_router(create_description_router)
    dp.include_router(policy_router)
    dp.include_router(buy_points_router)


    await dp.start_polling(bot)

if __name__ == "__main__":
    print("✅ Бот включен и готов к работе!")
    asyncio.run(main())

