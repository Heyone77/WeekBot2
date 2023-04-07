import re
from time import sleep
from Week_oddity import week_oddity
from Schedule import day_schedule
from chat_state import ChatState
from tgbot import bot, admin_id
from utils import update_command_counter, can_user_use_command

chat_state = ChatState()
chat_state.load_chat_state()


@bot.message_handler(commands=["id"])
def command_handler(message):
    update_command_counter(message.from_user.id, message.from_user.first_name, "week", chat_state)
    id_to_del = bot.send_message(message.chat.id, message.chat.id, disable_notification=True).id
    sleep(5)
    bot.delete_message(message.chat.id, id_to_del)


@bot.message_handler(commands=['list1'])
def command_handler(message):
    if message.from_user.id != admin_id:
        return
    if len(chat_state.command_counter) == 0:
        bot.send_message(message.from_user.id, "Словарь пустой", parse_mode="HTML")
        return
    dict_string = "\n".join(
        [f"{k}: {v['Username:']}, {v['Commands:']}" for k, v in chat_state.command_counter.items()])
    bot.send_message(message.from_user.id, f"{dict_string}", parse_mode="HTML")


@bot.message_handler(commands=['list2'])
def command_handler(message):
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
def command_handler(message):
    if can_user_use_command(message.from_user.id, chat_state):
        chat_state.messages_to_del.append(message.message_id)
        try:
            message_id = bot.send_photo(message.chat.id, day_schedule(), disable_notification=True).id
            update_command_counter(message.from_user.id, message.from_user.first_name, "schedule", chat_state)
        except Exception as e:
            bot.send_message(admin_id, f"Error: {e}")
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
def command_handler(message):
    update_command_counter(message.from_user.id, message.from_user.first_name, "week", chat_state)
    if week_oddity():
        bot.send_message(message.chat.id, "Нечётная неделя",
                         disable_notification=True)
    else:
        bot.send_message(message.chat.id, "Чётная неделя",
                         disable_notification=True)


@bot.message_handler(content_types=["text"])
def command_handler(message):
    regex = r".+(п(о|а)зд)|(держ)|(успе).+"
    matches = re.findall(regex, message.text.lower(), re.MULTILINE)
    if len(matches) > 0:
        update_command_counter(message.from_user.id, message.from_user.first_name, "opozdal", chat_state)
        id_to_del = bot.reply_to(message, "Отлично, держи в курсе 👌👌👌", disable_notification=True).id
        sleep(5)
        bot.delete_message(message.chat.id, id_to_del)
    else:
        return
