# Импортирование модулей
import atexit
import handlers

from apscheduler.schedulers.background import BackgroundScheduler
from tgbot import bot
from utils import change_chat_title

scheduler = BackgroundScheduler()

scheduler.add_job(func=change_chat_title, trigger='cron', day_of_week='mon', hour=7)

scheduler.start()
atexit.register(handlers.chat_state.save_chat_state)

bot.polling(none_stop=True, interval=0)
