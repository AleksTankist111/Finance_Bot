import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SQL_DB = os.getenv("SQL_DB")
DEFAULT_CURRENCY = "RSD"