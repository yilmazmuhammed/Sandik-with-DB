import os

import telegram

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
admin_chat_id = 453371981

sandik_bot = telegram.Bot(TELEGRAM_TOKEN)
