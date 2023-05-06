import datetime as dt
import sqlite3
import threading
from settings import bot, start_message, help_message, cur, con, BASE_DONAT

from notify_logic import Notifier


@bot.message_handler(commands=['start'])
def start(message):
    """Функция старта бота."""
    Notifier.set_bot_commands(self=Notifier, donation_commands=[])
    bot.send_message(
        message.chat.id,
        start_message
    )


@bot.message_handler(commands=['help'])
def help_function(message):
    """Функция вызова инструкций бота."""
    bot.send_message(
        message.chat.id,
        help_message
    )


@bot.message_handler(regexp='^Д|добавить')
def add_employee(message):
    """Функция добавления нового сотрудника в базу данных."""
    data = message.text.split()
    date = data[4].split('.')
    year = int(dt.date.today().strftime('%Y'))
    date = dt.date(year, int(date[1]), int(date[0])).strftime('%d.%m')
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
        result = 'ID | Имя Фамилия | Телеграм | Дата рождения \n\n'
        for employee in table:
            for data in employee:
                result += str(data) + ' '
            result += '\n'
        bot.send_message(message.chat.id, result)
    except sqlite3.OperationalError:
        bot.send_message(message.chat.id, 'Таблица пока пустая, добавь хотя '
                                          'бы одного сотрудника.')


@bot.message_handler(regexp='^/donate', chat_types='group')
def register_donate(message):
    table_name = message.text.split('@')[0][8:]
    table_name = 'fund_' + table_name
    cur.execute(f'''
        INSERT INTO {table_name}(name, surname, username, amount)
        VALUES ('{message.from_user.first_name}',
                '{message.from_user.last_name}',
                '{message.from_user.username}',
                '{BASE_DONAT}');
    ''')
    con.commit()


if __name__ == '__main__':
    n = Notifier()
    notifier = threading.Thread(target=n.notify_scheduler)
    notifier.start()
    bot.polling()
