# Импортирование модулей
from time import sleep
import telebot
from Schedule import day_schedule
from Week_oddity import week_oddity
import os
from dotenv import load_dotenv, find_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import atexit
import json


class ChatState:
    def __init__(self, askers=None):
        if askers is None:
            askers = {}
        self.askers = askers
        self.messages_to_del = []

    def msg_to_del(self):
        print(datetime.datetime.now().time(), self.messages_to_del)

    def get_askers(self):
        print(self.askers)



# Загрузка переменных среды
load_dotenv(find_dotenv())
token = os.environ.get("TOKEN")
chat_id = os.environ.get("CHAT_ID")

# Инициализация объектов бота и планировщика задач
bot = telebot.TeleBot(token)
scheduler = BackgroundScheduler()
chat_state = ChatState()

with open("users.json", "r") as f:
    chat_state.askers = {int(k): v for k, v in json.load(f).items()}



# Функция для изменения названия чата
def change_chat_title():
    title = "(НН) БЕЗ БАБ ББ-40919" if week_oddity() else "(ЧН) БЕЗ БАБ ББ-40919"
    bot.set_chat_title(chat_id, title)


def can_user_use_command(user_id):
    now = datetime.datetime.now()
    if user_id in last_command_time:
        time_since_last_command = now - last_command_time[user_id]
        if time_since_last_command < datetime.timedelta(minutes=5):
            return False
    last_command_time[user_id] = now
    return True

def add_user_to_askers(user_id):
    if user_id in chat_state.askers:
        chat_state.askers[user_id] += 1
    else:
        chat_state.askers[user_id] = 0



# Отправка ID чата
@bot.message_handler(commands=["id"])
def handle_id(message):
    add_user_to_askers(message.from_user.id)
    bot.send_message(message.chat.id, message.chat.id)

# Ручной вызов функции смены названия чата
@bot.message_handler(commands=["title"])
def change_title_command(message):
    change_chat_title()


last_command_time = {}


def save_data():
    with open("users.json", "w") as f:
        # записываем словарь в файл в формате JSON
        json.dump(chat_state.askers, f)


@bot.message_handler(commands=['schedule'])
def mycommand_handler(message):
    if can_user_use_command(message.from_user.id):
        chat_state.messages_to_del.append(message.message_id)
        try:
            message_id = bot.send_photo(
                message.chat.id, day_schedule(), disable_notification=True).id
        except:
            return
        chat_state.messages_to_del.append(message_id)
        sleep(25)
        for msg in chat_state.messages_to_del.copy():
            bot.delete_message(message.chat.id, msg)
            chat_state.messages_to_del.remove(msg)
    else:
        bot.delete_message(message.chat.id, message.message_id)
        return


@bot.message_handler(commands=["week"])
def handle_text(message):
    if week_oddity():
        bot.send_message(message.chat.id, "Нечётная неделя",
                         disable_notification=True)
    else:
        bot.send_message(message.chat.id, "Чётная неделя",
                         disable_notification=True)
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEHyPdj76H0IMu5B8JC0J3fydn_EXnFeAAC5xYAAkm1YEjpExkRZP9e7i4E",
                         disable_notification=True)


scheduler.add_job(func=change_chat_title, trigger='cron',
                  day_of_week='tue', hour=14, minute=10, timezone="Asia/Yekaterinburg")

scheduler.add_job(func=chat_state.get_askers, trigger='interval', seconds=10)

scheduler.start()
atexit.register(save_data)

bot.polling(none_stop=True, interval=0)
