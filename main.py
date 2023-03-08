# Импортирование модулей
import time
import telebot
from Schedule import day_schedule
from Week_oddity import week_oddity
import os
from dotenv import load_dotenv, find_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

class ChatState:
    def __init__(self):
        self.last_user = 0
        self.last_message_id = 0

# Загрузка переменных среды
load_dotenv(find_dotenv())
token = os.environ.get("TOKEN")
chat_id = os.environ.get("CHAT_ID")

# Инициализация объектов бота и планировщика задач
bot = telebot.TeleBot(token)
scheduler = BackgroundScheduler()
chat_state = ChatState()

# Словарь для хранения значений


# Функция для изменения названия чата
def change_chat_title():
    title = "(НН) БЕЗ БАБ ББ-40919" if week_oddity() else "(ЧН) БЕЗ БАБ ББ-40919"
    bot.set_chat_title(CHAT_ID, title)


# Отправка ID чата
@bot.message_handler(commands=["id"])
def handle_id(message):
    bot.send_message(message.chat.id, message.chat.id)


# Ручной вызов функции смены названия чата
@bot.message_handler(commands=["title"])
def change_title_command(message):
    change_chat_title()


@bot.message_handler(commands=["schedule"])
def send_schedule_command(message):
    try:
        chat_state.last_message_id = bot.send_photo(message.chat.id, day_schedule(), disable_notification=True).id
    except:
        chat_state.last_message_id = bot.send_message(message.chat.id, "На удивление пустой день", disable_notification=True).id
    time.sleep(25)
    try:
        bot.delete_message(message.chat.id, chat_state.last_message_id)
        bot.delete_message(message.chat.id, chat_state.last_message_id - 1)
    except:
        print(f"Не могу удалить соообщение {chat_state.last_message_id}")
        bot.delete_message(message.chat.id, chat_state.last_message_id - 2)

@bot.message_handler(commands=["week"])
def handle_text(message):
        if message.from_user.id != chat_state.last_user:
            if week_oddity():
                bot.send_message(message.chat.id, "Нечётная неделя", disable_notification=True)
                chat_state.last_user = message.from_user.id
            else:
                bot.send_message(message.chat.id, "Чётная неделя", disable_notification=True)
                chat_state.last_user = message.from_user.id
        else:
            bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEHyPdj76H0IMu5B8JC0J3fydn_EXnFeAAC5xYAAkm1YEjpExkRZP9e7i4E", disable_notification=True)



scheduler.add_job(func=change_chat_title, trigger='cron', day_of_week='mon', hour=12,  timezone='Asia/Yekaterinburg')
scheduler.start()

bot.polling(none_stop=True, interval=0)

