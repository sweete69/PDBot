import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import get_settings, Settings
from handlers import router
from gemini_service import GeminiService, GeminiConfig

logging.basicConfig(level=logging.INFO)


async def main():
    settings: Settings = get_settings()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp["settings"] = settings
    dp["ai"] = GeminiService(
        GeminiConfig(
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url,
            text_model=settings.gemini_text_model,
            image_model=settings.gemini_image_model,
        )
    )

    dp.include_router(router)
    await dp.start_polling(bot, settings=settings, ai=dp["ai"])


if __name__ == "__main__":
    asyncio.run(main())