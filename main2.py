import telebot

#Это пока неизвестно когда будет интегрировано

CHAT_BY_DATETIME = dict()

@bot.message_handler(func=lambda message: True)
def on_request(message: telebot.types.Message):
    text = 'Получено!'
    need_seconds = 50
    current_time = DT.datetime.now()
    last_datetime = CHAT_BY_DATETIME.get(message.chat.id)

    # Если первое сообщение (время не задано)
    if not last_datetime:
        CHAT_BY_DATETIME[message.chat.id] = current_time
    else:
        # Разница в секундах между текущим временем и временем последнего сообщения
        delta_seconds = (current_time - last_datetime).total_seconds()

        # Осталось ждать секунд перед отправкой
        seconds_left = int(need_seconds - delta_seconds)

        # Если время ожидания не закончилось
        if seconds_left > 0:
            text = f'Подождите {seconds_left} секунд перед выполнение этой команды'
        else:
            CHAT_BY_DATETIME[message.chat.id] = current_time

    bot.reply_to(message, text)



