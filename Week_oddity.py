import datetime as dt

def week_oddity():
    week_number = dt.datetime.today().isocalendar()[1]
    if week_number % 2 == 0:
        return False
    else:
        return True
