import os
from dotenv import load_dotenv

load_dotenv()

os.makedirs("data", exist_ok=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

API_BASE_URL = "https://bdx-web-host--megedfgh.replit.app"
API_USER = os.getenv("API_USERNAME", "mehedi")
API_PASS = os.getenv("API_PASSWORD", "admin")

DB_PATH = "data/bot.db"