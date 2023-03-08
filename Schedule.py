from datetime import datetime

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
