# Функция для изменения названия чата
from datetime import datetime, timedelta

from telebot.util import user_link

from Week_oddity import week_oddity
from tgbot import chat_id, bot


def change_chat_title():
    chat_title = bot.get_chat(chat_id).title
    if chat_title.startswith("(НН)") or chat_title.startswith("(ЧН)"):
        new_title = chat_title[5:]
        title = f"(НН) {new_title}" if week_oddity() else f"(ЧН) {new_title}"
    else:
        title = f"(НН) {chat_title}" if week_oddity() else f"(ЧН) {chat_title}"
    bot.set_chat_title(chat_id, title)


def update_command_counter(user, command, instance):
    if user.id not in instance.command_counter:
        instance.command_counter[user.id] = {'Username:': user_link(user), 'Commands:': {}}
    if command not in instance.command_counter[user.id]['Commands:']:
        instance.command_counter[user.id]['Commands:'][command] = 0
    instance.command_counter[user.id]['Commands:'][command] += 1


def can_user_use_command(user_id, instance):
    now = datetime.now()
    if user_id in instance.last_command_time:
        time_since_last_command = now - instance.last_command_time[user_id]
        if time_since_last_command < timedelta(minutes=5):
            return False
    instance.last_command_time[user_id] = now
    return True
