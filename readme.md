# TG-Bot для использования в студенческих чатах в телеграмме


# For Contributors

1. Для разработки бота нужно настроить виртуальное окружение
2. Настроить `.env` файл
```dotenv
TOKEN={Токен из Папочки ботов}
CHAT_ID={ID чата, к которому подключается бот}
ADMIN_ID={ID личного чата, желательно человека, который запускает бота.}
```
3. Запустить Dockerfile (или написать свой docker-compose.yml)


Желательно указать свой id в ADMIN_ID иначе вы не сможете вызвать часть комманд из за проверки прав


