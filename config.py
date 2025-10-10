import os
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_USERNAMES = os.getenv("ADMIN_USERNAMES", "")
PAYPAL_LINK = os.getenv("PAYPAL_LINK", "")
