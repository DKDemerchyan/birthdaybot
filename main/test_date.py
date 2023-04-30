import datetime

YEAR = int(datetime.date.today().strftime('%Y'))

today = datetime.date.today()

birth_day = datetime.date(YEAR, 5, 2)

x = today + datetime.timedelta(days=2)

print(today)