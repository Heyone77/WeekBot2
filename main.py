# Импортирование модулей
import re
from time import sleep
import telebot
from Week_oddity import week_oddity
import os
from Schedule import day_schedule
from dotenv import load_dotenv, find_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import atexit
import json
import pickle


class ChatState:
    def __init__(self, askers=None):
        if askers is None:
            askers = {}
        self.askers = askers
        self.command_counter = {}
        self.messages_to_del = []

    def get_info(self):
        print(f"{self.command_counter}")


# Загрузка переменных среды
load_dotenv(find_dotenv())
token = os.environ.get("TOKEN")
chat_id = os.environ.get("CHAT_ID")
admin_id = os.environ.get("ADMIN_ID")


# Инициализация объектов бота и планировщика задач
bot = telebot.TeleBot(token)
scheduler = BackgroundScheduler()
chat_state = ChatState()



if os.path.exists("users.json") and os.path.getsize("users.json") > 0:
    with open("users.json", "r") as f:
        chat_state.askers = {int(k): v for k, v in json.load(f).items()}
else:
    chat_state.askers = {}

if os.path.exists("command_count.pickle") and os.stat("command_count.pickle").st_size > 0:
    with open("command_count.pickle", "rb") as f:
        chat_state.command_counter = pickle.load(f)
else:
    chat_state.command_counter = {}

with open("users.json", "r") as f:
    chat_state.askers = {int(k): v for k, v in json.load(f).items()}


# Функция для изменения названия чата
def change_chat_title():
    chat_title = bot.get_chat(chat_id).title
    if chat_title.startswith("(НН)") or chat_title.startswith("(ЧН)"):
        new_title = chat_title[5:]
        title = f"(НН) {new_title}" if week_oddity() else f"(ЧН) {new_title}"
    else:
        title = f"(НН) {chat_title}" if week_oddity() else f"(ЧН) {chat_title}"
    bot.set_chat_title(chat_id, title)


# def update_command_counter(user_id, command, instance):
#     if user_id not in instance.command_counter:
#         instance.command_counter[user_id] = {}
#     if command not in instance.command_counter[user_id]:
#         instance.command_counter[user_id][command] = 0
#     instance.command_counter[user_id][command] += 1

def update_command_counter(user_id, username, command, instance):
    if user_id not in instance.command_counter:
        instance.command_counter[user_id] = {'username': username, 'commands': {}}
    if command not in instance.command_counter[user_id]['commands']:
        instance.command_counter[user_id]['commands'][command] = 0
    instance.command_counter[user_id]['commands'][command] += 1


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


last_command_time = {}


def save_data():
    with open("users.json", "w") as file:
        # записываем словарь в файл в формате JSON
        json.dump(chat_state.askers, file)
    with open('command_count.pickle', 'wb') as file:
        pickle.dump(chat_state.command_counter, file)


@bot.message_handler(commands=['list'])
def mycommand_handler(message):
    dict_to_mess = json.dumps(chat_state.command_counter)
    bot.send_message(message.from_user.id,
                     f"{dict_to_mess}, <a href='tg://user?id={message.from_user.id}'>{chat_state.command_counter[message.from_user.id]['username']}</a>",
                     parse_mode="HTML")


@bot.message_handler(commands=['schedule'])
def mycommand_handler(message):
    if can_user_use_command(message.from_user.id):
        chat_state.messages_to_del.append(message.message_id)
        try:
            message_id = bot.send_photo(
                message.chat.id, day_schedule(), disable_notification=True).id
            update_command_counter(message.from_user.id, message.from_user.first_name, "schedule", chat_state)
        except Exception as e:
            bot.send_message(admin_id, f"Ошибка: {e}")
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
    update_command_counter(message.from_user.id, message.from_user.first_name, "week", chat_state)
    if week_oddity():
        bot.send_message(message.chat.id, "Нечётная неделя",
                         disable_notification=True)
    else:
        bot.send_message(message.chat.id, "Чётная неделя",
                         disable_notification=True)


@bot.message_handler(commands=["test"])
def handle_text(message):
    update_command_counter(message.from_user.id, message.from_user.first_name, "test", chat_state)
    bot.send_message(message.chat.id, "test")


@bot.message_handler(content_types=["text"])
def handle_id(message):
    regex = r"оп(о|а)зд.+"
    matches = re.findall(regex, message.text.lower(), re.MULTILINE)
    if len(matches) > 0:
        update_command_counter(message.from_user.id, message.from_user.first_name, "опоздашка", chat_state)
        id_to_del = bot.reply_to(message, "Отлично, держи в курсе =)", disable_notification=True).id
        sleep(5)
        bot.delete_message(message.chat.id, id_to_del)
    else:
        return


scheduler.add_job(func=change_chat_title, trigger='cron',
                  day_of_week='mon', hour=7)

# scheduler.add_job(func=chat_state.get_info, trigger='interval', seconds=10)

scheduler.start()
atexit.register(save_data)

bot.polling(none_stop=True, interval=0)
