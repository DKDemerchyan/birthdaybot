import datetime as dt
import os
import sqlite3
import threading
import time

import schedule
from dotenv import load_dotenv
from telebot import TeleBot, types

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_CHAT = os.getenv('GROUP_CHAT')

con = sqlite3.connect('../database.db', check_same_thread=False)
cur = con.cursor()

bot = TeleBot(BOT_TOKEN)

# CONSTANTS:
YEAR = int(dt.date.today().strftime('%Y'))
BASE_DONAT = 500


@bot.message_handler(commands=['start'])
def start(message):
    """Функция стартующая при первом запуске бота."""
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
    """Функция вызова инструкций бота."""
    bot.send_message(
        message.chat.id,
        'Чтобы добавить нового сотрудника нужно просто написать мне его '
        'данные в правильном порядке и виде. Напиши мне ключевое слово '
        '"Добавить" и далее данные через один пробел. \n'
        '>>> Добавить Майкл Скотт @telegram_mike 15.03'
        '\n ____________________________ \n'
        'Чтобы удалить сотрудника из списка необходимо написать ключевое '
        'слово "Удалить" и далее ID сотрудника. \n\n'
        '>>> Удалить 6 \n\n'
        'ID можно узнать по команде /table'
        '\n ____________________________ \n'
    )


@bot.message_handler(regexp='^Д|добавить')
def add_employee(message):
    """Функция добавления нового сотрудника в базу данных."""
    data = message.text.split()
    date = data[4].split('.')
    date = dt.date(YEAR, int(date[1]), int(date[0])).strftime('%d.%m')
    print('Это add_employee', date)
    try:
        cur.executescript(f'''
            CREATE TABLE IF NOT EXISTS birthdays(
                id INTEGER PRIMARY KEY,
                name TEXT,
                surname TEXT,
                username TEXT,
                birth_date TEXT
            );

            INSERT INTO birthdays(name, surname, username, birth_date)
            VALUES ('{data[1]}', '{data[2]}', '{data[3][1:]}', '{date}');
        ''')
        con.commit()
        bot.send_message(message.chat.id, 'Добавил в таблицу. Посмотреть ее '
                                          'можно вызовом /table')
    except sqlite3.OperationalError:
        bot.send_message(message.chat.id, 'Что-то не так с введенными данными')


@bot.message_handler(regexp='^У|удалить')
def delete_employee(message):
    """Функция удаления сотрудника из базы данных."""
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
    """Функция вывода всех сотрудников из базы данных."""
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


@bot.message_handler(regexp='^/donate')
def register_donate(message):
    print(message)
    table_name = message.text.split('@')[0][8:]
    print(table_name)
    cur.execute(f'''
        INSERT INTO fund_{table_name}(name, surname, username, amount)
        VALUES ('{message.from_user.first_name}',
                '{message.from_user.last_name}',
                '{message.from_user.username}',
                '{BASE_DONAT}');
    ''')


def set_bot_commands(donation_commands):    # ВЫВЕСТИ GENERAL_COMMANDS LIST В КОНСТАНТУ
    general_commands_list = [
        types.BotCommand('/start', 'Запустить бота'),
        types.BotCommand('/help', 'Помощь'),
        types.BotCommand('/table', 'Таблица сотрудников')
    ]
    donation_commands.extend(general_commands_list)
    bot.set_my_commands(donation_commands)


def create_money_table(username):
    creation_date = dt.date.today().strftime('%d.%m')
    print('creation_date', creation_date)
    cur.executescript(f'''
        CREATE TABLE IF NOT EXISTS fund_{username}(
                id INTEGER PRIMARY KEY,
                name TEXT,
                surname TEXT,
                username TEXT,
                amount TEXT,
                table_date TEXT
            );

        INSERT INTO fund_{username}(username, table_date)
        VALUES ('donate_{username}', '{creation_date}');
    ''')
    con.commit()


def notify():
    """Функция уведомления в группе о дне рождения коллеги."""
    after_tomorrow = (dt.date.today() + dt.timedelta(days=2)).strftime('%d.%m')
    try:
        cur.execute(f'''
            SELECT name, surname, username
            FROM birthdays
            WHERE birth_date = '{after_tomorrow}';
        ''')
        employees = cur.fetchall()
        if employees:
            donate_commands = []
            for employee in employees:
                donate_commands.append(
                    types.BotCommand(f'/donate_{employee[2]}',
                                     f'Донат для {employee[2]}')
                )
                create_money_table(employee[2])
                bot.send_message(GROUP_CHAT, f'Всем привет послезавтра свой день'
                                             f' рождения празднует {employee[0]} '
                                             f'{employee[1]} {employee[2]}')
            set_bot_commands(donate_commands)
    except sqlite3.OperationalError:
        pass


def notifier():
    """Функция настройки расписания проверки предстоящих дней рождения"""
    #  schedule.every().day.at('10:30').do(notify)
    schedule.every(5).seconds.do(notify)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    notifier = threading.Thread(target=notifier)
    notifier.start()
    bot.polling()
