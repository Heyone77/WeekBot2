from datetime import datetime
import requests
from json import loads


def get_photo(path: str):
    with open(path, "rb") as img:
        return img.read()


def day_schedule():
    weekday = datetime.today().isoweekday()
    if weekday == 1 or weekday == 7:
        return "Самоподготовка"
    else:
        path = f"./schedule_images/{weekday}.png"
        return get_photo(path)


def get_motivational_quote():
    response = requests.get('https://api.goprogram.ai/inspiration')
    return loads(response.text)
