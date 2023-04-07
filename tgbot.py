import os

import telebot
from dotenv import load_dotenv, find_dotenv

# Загрузка переменных среды
load_dotenv(find_dotenv())
token = os.environ.get("TOKEN")
chat_id = os.environ.get("CHAT_ID")
admin_id = int(os.environ.get("ADMIN_ID"))

# Инициализация объекта бота
bot = telebot.TeleBot(token)
