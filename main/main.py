import datetime
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


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        'Привет, я телеграм-бот. Помогаю нашим сотрудникам не забывать '
        'про дни рождения друг друга. Меня нужно добавить в чат и рассказать '
        'мне о всех работниках. \n\n'
        'Если нужна будет помощь вызывай команду /help.'
    )


@bot.message_handler(commands=['add'])
def add_info(message):
    bot.send_message(
        message.chat.id,
        'Чтобы добавить нового сотрудника нужно просто написать мне его '
        'данные в правильном порядке и виде. Напиши мне ключевое слово '
        '"Добавить" и далее '
        'данные через один пробел. Если число однозначное не надо добавлять 0 в '
        'начало. Снизу пример: \n\n'
        'Добавить Майкл Скотт @telegram_mike 15 Март'
    )


@bot.message_handler(regexp='^Д|добавить')
def add_employee(message):
    months = {
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

    data = message.text.split()

    if data[5].lower() not in months:
        bot.send_message(message.chat.id, 'Проверь, пожалуйста, месяц и '
                                          'попробуй заново.')
    else:
        cur.executescript(f'''
            CREATE TABLE IF NOT EXISTS birthdays(
                id INTEGER PRIMARY KEY,
                name TEXT,
                surname TEXT,
                tg_name TEXT,
                day INTEGER,
                month INTEGER
            );

            INSERT INTO birthdays(name, surname, tg_name, day, month)
            VALUES ('{data[1]}', '{data[2]}', '{data[3]}',
                    {int(data[4])}, {months[data[5].lower()]});
        ''')
        con.commit()
        bot.send_message(message.chat.id, 'Я добавил в таблицу. Посмотреть ее '
                                          'можно вызовом /table')


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
        employee = cur.execute(f'''
            SELECT name, surname
            FROM birthdays
            WHERE id = {int(data[1])};
        ''')

        for i in employee:
            employee = i
        print(employee)
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
        result = 'ID Имя Фамилия Телеграм Число Месяц \n\n'
        for employee in table:
            for data in employee:
                result += str(data) + ' '
            result += '\n'
        bot.send_message(message.chat.id, result)
    except sqlite3.OperationalError:
        bot.send_message(message.chat.id, 'Таблица пока пустая, добавь хотя '
                                          'бы одного сотрудника.')


# def notify():
#     today = datetime.date.today()
#     day = int(str(today).split('-')[2])
#     month = int(str(today).split('-')[1])
#
#     cur.execute(f'''
#         SELECT name, surname, tg_name
#         FROM birthdays
#         WHERE day = {day + 1} AND month = {month};
#     ''')
#
#     for x in cur:
#         print(x)


def notify2():
    try:
        sec_now = int(time.strftime('%S'))
        cur.execute(f'''
                SELECT sec, surname
                FROM birthdays
                WHERE sec = {sec_now + 10};
            ''')
        for res in cur:
            if res:
                bot.send_message(NOTIFY_TO, f'Через 10 сек ДР у {res[1]}')
    except sqlite3.OperationalError:
        pass


def notifier():
    schedule.every(1).second.do(notify2)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    notifier = threading.Thread(target=notifier)
    notifier.start()
    bot.polling()
