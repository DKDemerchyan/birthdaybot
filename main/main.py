import datetime as dt
import os
import sqlite3
import threading
import time

import schedule
from dotenv import load_dotenv
from telebot import TeleBot

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
NOTIFY_TO = os.getenv('NOTIFY_TO')


con = sqlite3.connect('../database.db', check_same_thread=False)
cur = con.cursor()


bot = TeleBot(BOT_TOKEN)

# CONSTANTS:
YEAR = int(dt.date.today().strftime('%Y'))
MONTHS = {
        'январь': 1,
        'февраль': 2,
        'март': 3,
        'апрель': 4,
        'май': 5,
        'июнь': 6,
        'июль': 7,
        'август': 8,
        'сентябрь': 9,
        'октябрь': 10,
        'ноябрь': 11,
        'декабрь': 12,
    }


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        'Привет, я телеграм-бот. Помогаю нашим сотрудникам не забывать '
        'про дни рождения друг друга, а также собирать на подарки. '
        'Меня нужно добавить в чат и рассказать '
        'мне о всех работниках. Подробнее обо мне можно почитать'
        'тут https://github.com/DKDemerchyan/birthdaybot \n\n'
        'Если нужна инструкция или помощь вызывай команду /help'
    )


@bot.message_handler(commands=['help'])
def help_func(message):
    ...


@bot.message_handler(commands=['add'])
def add_info(message):
    bot.send_message(
        message.chat.id,
        'Чтобы добавить нового сотрудника нужно просто написать мне его '
        'данные в правильном порядке и виде. Напиши мне ключевое слово '
        '"Добавить" и далее данные через один пробел. Снизу пример: \n\n'
        'Добавить Майкл Скотт @telegram_mike 15.03'
    )


@bot.message_handler(regexp='^Д|добавить')
def add_employee(message):
    data = message.text.split()
    date = data[4].split('.')
    date = dt.date(YEAR, int(date[1]), int(date[0])).strftime('%d.%m')
    try:
        cur.executescript(f'''
            CREATE TABLE IF NOT EXISTS birthdays(
                id INTEGER PRIMARY KEY,
                name TEXT,
                surname TEXT,
                tg_name TEXT,
                date TEXT
            );
    
            INSERT INTO birthdays(name, surname, tg_name, date)
            VALUES ('{data[1]}', '{data[2]}', '{data[3]}', '{date}');
        ''')
        con.commit()
        bot.send_message(message.chat.id, 'Добавил в таблицу. Посмотреть ее '
                                          'можно вызовом /table')
    except sqlite3.OperationalError:
        bot.send_message(message.chat.id, 'Что-то не так с введенными данными')


@bot.message_handler(commands=['delete'])
def delete_info(message):
    bot.send_message(
        message.chat.id,
        'Чтобы удалить сотрудника из списка необходимо написать ключевое '
        'слово "Удалить" и далее ID сотрудника. \n\n'
        'Удалить 6'
    )


@bot.message_handler(regexp='^У|удалить')
def delete_employee(message):
    try:
        data = message.text.split()
        cur.execute(f'''
            SELECT name, surname
            FROM birthdays
            WHERE id = {int(data[1])};
        ''')

        employee = cur.fetchone()
        cur.execute(f'''
            DELETE FROM birthdays
            WHERE id = {int(data[1])};
        ''')
        con.commit()
        bot.send_message(message.chat.id,
                         f'Удалил сотрудника {" ".join(employee)}')
    except sqlite3.OperationalError:
        bot.send_message(message.chat.id, 'Я не нашел такого сотрудника '
                                          'в таблице')


@bot.message_handler(commands=['table'])
def send_table(message):
    try:
        table = cur.execute(f'''
            SELECT *
            FROM birthdays
            ORDER BY surname;
        ''')
        result = 'ID Имя Фамилия Телеграм Дата рождения \n\n'
        for employee in table:
            for data in employee:
                result += str(data) + ' '
            result += '\n'
        bot.send_message(message.chat.id, result)
    except sqlite3.OperationalError:
        bot.send_message(message.chat.id, 'Таблица пока пустая, добавь хотя '
                                          'бы одного сотрудника.')


def notify():
    after_tomorrow = (dt.date.today() + dt.timedelta(days=2)).strftime('%d.%m')

    cur.execute(f'''
        SELECT name, surname, tg_name
        FROM birthdays
        WHERE date = {after_tomorrow};
    ''')
    employee = cur.fetchone()
    if employee:
        bot.send_message(NOTIFY_TO, f'Всем привет послезавтра свой день'
                                    f' рождения празднует {employee[0]} '
                                    f'{employee[1]} {employee[2]}')


def notifier():
    schedule.every(5).second.do(notify)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    notifier = threading.Thread(target=notifier)
    notifier.start()
    bot.polling()
