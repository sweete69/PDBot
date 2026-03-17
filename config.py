import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    gemini_api_key: str
    gemini_base_url: str
    gemini_text_model: str
    gemini_image_model: str
    max_output_chars: int


def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com").strip()
    gemini_text_model = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash").strip()
    gemini_image_model = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image-preview").strip()
    max_output_chars = int(os.getenv("MAX_OUTPUT_CHARS", "3500"))

    if not bot_token:
        raise RuntimeError("Не найден BOT_TOKEN в .env")
    if not gemini_api_key:
        raise RuntimeError("Не найден GEMINI_API_KEY в .env")

    return Settings(
        bot_token=bot_token,
        gemini_api_key=gemini_api_key,
        gemini_base_url=gemini_base_url,
        gemini_text_model=gemini_text_model,
        gemini_image_model=gemini_image_model,
        max_output_chars=max_output_chars,
    )