from pathlib import Path

import pytz

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"
TIMEZONE = pytz.timezone("Europe/Moscow")
APP_NAME = "audio-summarization"
