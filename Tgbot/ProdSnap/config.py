import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

if not BOT_TOKEN:
    exit("Error: BOT_TOKEN is missing in .env")
if not GEMINI_API_KEY:
    exit("Error: GEMINI_API_KEY is missing in .env")