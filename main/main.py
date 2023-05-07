import datetime as dt
import sqlite3
import threading

from notify_logic import Notifier
from settings import bot, con, cur, help_message, start_message


@bot.message_handler(commands=['start'], chat_types='private')
def start(message):
    """Функция старта бота."""
    Notifier.set_bot_commands(self=Notifier, donation_commands=[])
    bot.send_message(message.chat.id, start_message)


@bot.message_handler(commands=['help'], chat_types='private')
def help_function(message):
    """Функция вызова инструкций бота."""
    bot.send_message(message.chat.id, help_message)


@bot.message_handler(regexp='^Добавить|добавить', chat_types='private')
def add_employee(message):
    """Функция добавления нового сотрудника в базу данных."""
    try:
        data = message.text.split()
        date = data[4].split('.')
        date = dt.date(
            year=int(dt.date.today().strftime('%Y')),
            month=int(date[1]),
            day=int(date[0])
        ).strftime('%d.%m')

        cur.executescript(f'''
            CREATE TABLE IF NOT EXISTS birthdays(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                username TEXT NOT NULL,
                birth_date TEXT NOT NULL
            );

            INSERT INTO birthdays(name, surname, username, birth_date)
            VALUES ('{data[1]}', '{data[2]}', '{data[3]}', '{date}');
        ''')
        con.commit()
        bot.reply_to(message, 'Добавил в таблицу.')
    except (sqlite3.OperationalError, IndexError):
        bot.reply_to(message, 'Неверно введены данные!')


@bot.message_handler(regexp='^Удалить|удалить', chat_types='private')
def delete_employee(message):
    """Функция удаления сотрудника из базы данных.

    - Принимает ID из таблицы birthdays
    """
    try:
        id_employee = int(message.text.split()[1])
        employee = cur.execute(f'''
            SELECT name, surname
            FROM birthdays
            WHERE id = {id_employee};
        ''').fetchone()

        cur.execute(f'''
            DELETE FROM birthdays
            WHERE id = {id_employee};
        ''')
        con.commit()
        bot.send_message(
            message.chat.id,
            f'Удалил сотрудника {employee[0]} {employee[1]}'
        )
    except (TypeError, IndexError):
        bot.reply_to(message, 'Такого ID не существует!')


@bot.message_handler(commands=['table'])
def send_table(message):
    """Функция вывода всех сотрудников из базы данных."""
    try:
        table = cur.execute('''
            SELECT *
            FROM birthdays
            ORDER BY surname;
        ''')
        result = 'ID | Имя Фамилия | Телеграм | Дата рождения \n\n'
        for employee in table:
            for data in employee:
                result += str(data) + ' '
            result += '\n'
        bot.send_message(message.chat.id, result)
    except sqlite3.OperationalError:
        bot.reply_to(message, 'Таблица пока пустая.')


# @bot.message_handler(regexp='ДР|др [0-9]', chat_types='private')
# def show_donates(message):
#     """Функция показа донатов сотруднику по его ID."""
#     id_employee = int(message.text.split()[1])
#     cur.execute(f'''
#         SELECT username
#         FROM birthdays
#         WHERE id = {id_employee};
#     ''')
#     try:
#         username = cur.fetchone()[0]
#         print(username)
#     except TypeError:
#         bot.reply_to(message, 'Такого ID не существует!')


# @bot.message_handler(regexp='^/donate', chat_types='group')
# def register_donate(message):
#     table_name = message.text.split('@')[0][8:]
#     table_name = 'fund_' + table_name
#     cur.execute(f'''
#         INSERT INTO {table_name}(name, surname, username, amount)
#         VALUES ('{message.from_user.first_name}',
#                 '{message.from_user.last_name}',
#                 '{message.from_user.username}',
#                 '{BASE_DONAT}');
#     ''')
#     con.commit()


if __name__ == '__main__':
    n = Notifier()
    notifier = threading.Thread(target=n.notify_scheduler)
    notifier.start()
    bot.polling()
