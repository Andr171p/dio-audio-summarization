from pathlib import Path

import pytz
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"
TIMEZONE = pytz.timezone("Europe/Moscow")

load_dotenv(ENV_PATH)
