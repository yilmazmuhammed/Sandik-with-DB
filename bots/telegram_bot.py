import os

import telegram
from telegram.ext import Updater, CommandHandler

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
admin_chat_id = 453371981


class SandikTelegramBot(telegram.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_message_to_list(self, chat_ids: list, text, parse_mode='Markdown'):
        for chat_id in set(chat_ids):
            self.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)


telegram_bot = SandikTelegramBot(TELEGRAM_TOKEN)


def start_handler(update, context):
    chat_id = update.message['chat']['id']
    update.message.reply_text("Telegram chat id: %s" % chat_id)


if __name__ == '__main__':
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.start_polling()
    updater.idle()
