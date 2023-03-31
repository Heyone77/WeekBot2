# Импортирование модулей
import re
from time import sleep
import telebot
from Schedule import day_schedule, get_motivational_quote
from Week_oddity import week_oddity
import os
from dotenv import load_dotenv, find_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import atexit
import json
from translate import Translator


class ChatState:
    def __init__(self, askers=None):
        if askers is None:
            askers = {}
        self.askers = askers
        self.command_counter = {}
        self.messages_to_del = []

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
translator = Translator(to_lang='ru')

if os.path.exists("users.json") and os.path.getsize("users.json") > 0:
    with open("users.json", "r") as f:
        chat_state.askers = {int(k): v for k, v in json.load(f).items()}
else:
    chat_state.askers = {}


# with open("users.json", "r") as f:
#     chat_state.askers = {int(k): v for k, v in json.load(f).items()}


# Функция для изменения названия чата
def change_chat_title():
    chat_title = bot.get_chat(chat_id).title
    if chat_title.startswith("(НН)") or chat_title.startswith("(ЧН)"):
        new_title = chat_title[5:]
        title = f"(НН) {new_title}" if week_oddity() else f"(ЧН) {new_title}"
    else:
        title = f"(НН) {chat_title}" if week_oddity() else f"(ЧН) {chat_title}"
    bot.set_chat_title(chat_id, title)


def update_command_counter(user_id, command, instance):
    if user_id not in instance.command_counter:
        instance.command_counter[user_id] = {}
    if command not in instance.command_counter[user_id]:
        instance.command_counter[user_id][command] = 0
    instance.command_counter[user_id][command] += 1


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
    id_to_del = bot.send_message(message.chat.id, message.chat.id, disable_notification=True).id
    sleep(5)
    bot.delete_message(message.chat.id, id_to_del)


# Ручной вызов функции смены названия чата
@bot.message_handler(commands=["title"])
def change_title_command(message):
    update_command_counter(message.from_user.id, "title", chat_state)
    change_chat_title()


last_command_time = {}


def save_data():
    with open("users.json", "w") as f:
        # записываем словарь в файл в формате JSON
        json.dump(chat_state.askers, f)
    with open('command_count.json', 'w') as f:
        json.dump(chat_state.command_counter, f)


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


def motivate_students():
    quote = get_motivational_quote()
    translated = translator.translate(quote['quote'])


    # bot.send_message(chat_id, quote['quote'])




@bot.message_handler(commands=["week"])
def handle_text(message):
    update_command_counter(message.from_user.id, "week", chat_state)
    if week_oddity():
        bot.send_message(message.chat.id, "Нечётная неделя",
                         disable_notification=True)
    else:
        bot.send_message(message.chat.id, "Чётная неделя",
                         disable_notification=True)


@bot.message_handler(commands=["test"])
def handle_text(message):
    update_command_counter(message.from_user.id, "test", chat_state)


@bot.message_handler(content_types=["text"])
def handle_id(message):
    regex = r"оп(о|а)зд.+"
    matches = re.findall(regex, message.text.lower(), re.MULTILINE)
    if len(matches) > 0:
        id_to_del = bot.reply_to(message, "Отлично, держи в курсе =)", disable_notification=True).id
        sleep(5)
        bot.delete_message(message.chat.id, id_to_del)
    else:
        return


scheduler.add_job(func=change_chat_title, trigger='cron',
                  day_of_week='mon', hour=8, timezone="UTC")

scheduler.add_job(func=chat_state.get_askers, trigger='interval', seconds=10)

# scheduler.add_job(func=motivate_students, trigger='interval', seconds=2)

scheduler.start()
atexit.register(save_data)

bot.polling(none_stop=True, interval=0)
