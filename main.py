# Импортирование модулей
import json
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
import pickle


class ChatState:
    def __init__(self):
        self.command_counter = {}
        self.messages_to_del = []


# Загрузка переменных среды
load_dotenv(find_dotenv())
token = os.environ.get("TOKEN")
chat_id = os.environ.get("CHAT_ID")
admin_id = int(os.environ.get("ADMIN_ID"))

# Инициализация объектов бота и планировщика задач
bot = telebot.TeleBot(token)
scheduler = BackgroundScheduler()
chat_state = ChatState()

if os.path.exists("command_count.pickle") and os.stat("command_count.pickle").st_size > 0:
    with open("command_count.pickle", "rb") as f:
        chat_state.command_counter = pickle.load(f)
else:
    chat_state.command_counter = {}


# Функция для изменения названия чата
def change_chat_title():
    chat_title = bot.get_chat(chat_id).title
    if chat_title.startswith("(НН)") or chat_title.startswith("(ЧН)"):
        new_title = chat_title[5:]
        title = f"(НН) {new_title}" if week_oddity() else f"(ЧН) {new_title}"
    else:
        title = f"(НН) {chat_title}" if week_oddity() else f"(ЧН) {chat_title}"
    bot.set_chat_title(chat_id, title)



def update_command_counter(user_id, username, command, instance):
    if user_id not in instance.command_counter:
        user_link = f"<a href='tg://user?id={user_id}'>{username}</a>"
        instance.command_counter[user_id] = {'Username:': user_link, 'Commands:': {}}
    if command not in instance.command_counter[user_id]['Commands:']:
        instance.command_counter[user_id]['Commands:'][command] = 0
    instance.command_counter[user_id]['Commands:'][command] += 1


def can_user_use_command(user_id):
    now = datetime.datetime.now()
    if user_id in last_command_time:
        time_since_last_command = now - last_command_time[user_id]
        if time_since_last_command < datetime.timedelta(minutes=5):
            return False
    last_command_time[user_id] = now
    return True


# Отправка ID чата
@bot.message_handler(commands=["id"])
def handle_id(message):
    print("id")
    update_command_counter(message.from_user.id, message.from_user.first_name, "week", chat_state)
    id_to_del = bot.send_message(message.chat.id, message.chat.id, disable_notification=True).id
    sleep(5)
    bot.delete_message(message.chat.id, id_to_del)


last_command_time = {}


def save_data():
    with open('command_count.pickle', 'wb') as file:
        pickle.dump(chat_state.command_counter, file)


@bot.message_handler(commands=['list1'])
def mycommand_handler(message):
    if message.from_user.id != admin_id:
        return
    if len(chat_state.command_counter) == 0:
        bot.send_message(message.from_user.id, "Словарь пустой", parse_mode="HTML")
        return
    dict_string = "\n".join(
        [f"{k}: {v['Username:']}, {v['Commands:']}" for k, v in chat_state.command_counter.items()])
    bot.send_message(message.from_user.id, f"{dict_string}", parse_mode="HTML")


@bot.message_handler(commands=['list2'])
def mycommand_handler(message):
    if message.from_user.id == admin_id:
        dict_to_mess = chat_state.command_counter
        if len(dict_to_mess) > 0:
            result_str = ""
            for key in dict_to_mess:
                result_str += f"{key}:\n{dict_to_mess[key]}\n"
            bot.send_message(message.from_user.id, result_str, parse_mode="HTML")
        else:
            bot.send_message(message.from_user.id, "Словарь пустой")
    else:
        return


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
    regex = r".+(п(о|а)зд)|(держ)|(успе).+"
    matches = re.findall(regex, message.text.lower(), re.MULTILINE)
    if len(matches) > 0:
        update_command_counter(message.from_user.id, message.from_user.first_name, "opozdal", chat_state)
        id_to_del = bot.reply_to(message, "Отлично, держи в курсе =)", disable_notification=True).id
        sleep(5)
        bot.delete_message(message.chat.id, id_to_del)
    else:
        return


scheduler.add_job(func=change_chat_title, trigger='cron',
                  day_of_week='mon', hour=7)

scheduler.start()
atexit.register(save_data)

bot.polling(none_stop=True, interval=0)
