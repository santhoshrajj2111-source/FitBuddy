import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


APP_NAME = "FitBuddy"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'fitbuddy.db'}"
)

GOOGLE_API_KEY = os.getenv(
    "GOOGLE_API_KEY",
    ""
).strip()

DEMO_MODE = os.getenv(
    "DEMO_MODE",
    "false"
).lower() in {
    "1",
    "true",
    "yes",
    "on"
}

ADMIN_KEY = os.getenv(
    "ADMIN_KEY",
    "change-me"
)

# Current Gemini models.
WORKOUT_MODEL = os.getenv(
    "GEMINI_WORKOUT_MODEL",
    "gemini-3.8-flash"
)

TIP_MODEL = os.getenv(
    "GEMINI_TIP_MODEL",
    "gemini-3.5-flash-lite"
)