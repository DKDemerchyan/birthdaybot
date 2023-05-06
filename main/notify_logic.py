import datetime as dt
import sqlite3
import time

import schedule
from telebot import types
from settings import bot, GROUP_CHAT, cur, con


class Notifier:
    """Класс Notifier используется для работы с ругелярными действиями бота.
    Устанавливает команды, создает/удаляет таблицы, управляет уведомлениями."""

    general_commands_list = [
        types.BotCommand('/start', 'Запустить бота'),
        types.BotCommand('/help', 'Помощь'),
        types.BotCommand('/table', 'Таблица сотрудников')
    ]

    def set_bot_commands(self, donation_commands):
        """Функция при вызове устанавливает боту команды.

        - Принимает команды донатов, создающиеся в notify()
        - К стандартным командам добавляет команды для донатов
        """
        donation_commands.extend(self.general_commands_list)
        bot.set_my_commands(donation_commands)

    @staticmethod
    def create_money_table(username):
        """Функция создания таблицы в БД, для фиксирования донатов.

        - Создает новую таблицу при вызове
        - Фиксирует дату создания в первую строку таблицы
        """
        creation_date = dt.date.today().strftime('%d.%m.%Y')
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

    @staticmethod
    def delete_money_table():
        """Функция для удаления старых таблиц.

        - Из всех таблиц выберет связанные со сборами.
        - Проверит дату создания и удалит, если она старше 180 дней
        """
        cur.execute(f'''
            SELECT tbl_name
            FROM sqlite_master
            WHERE tbl_name LIKE 'fund%';
        ''')
        funds = cur.fetchall()
        for fund in funds:
            cur.execute(f'''
                SELECT table_date
                FROM {fund[0]}
                WHERE id = 1;
            ''')
            table_date = cur.fetchone()[0].split('.')
            table_date = dt.date(int(table_date[2]), int(table_date[1]),
                                 int(table_date[0]))
            if table_date < dt.date.today() - dt.timedelta(days=180):
                print('Дропаю', fund[0])
                cur.execute(f'''
                    DROP TABLE {fund[0]};
                ''')
                con.commit()

    def notify(self):
        """Функция уведомления в группе о дне рождения коллеги.

        - Проверяет есть ли завтра дни рождения
        - При выполнении условия для каждого создает бот-команду для доната,
        таблицу для регистрации сборов
        - Отправляет уведомление в чат
        """
        tomorrow = (dt.date.today() + dt.timedelta(days=1)).strftime('%d.%m')
        try:
            cur.execute(f'''
                SELECT name, surname, username
                FROM birthdays
                WHERE birth_date = '{tomorrow}';
            ''')
            employees = cur.fetchall()
            if employees:
                donate_commands = []
                for employee in employees:
                    donate_commands.append(
                        types.BotCommand(f'/donate_{employee[2]}',
                                         f'Донат для {employee[2]}')
                    )
                    self.create_money_table(employee[2])
                    bot.send_message(GROUP_CHAT, f'Всем привет! Завтра день'
                                                 f' рождения празднует '
                                                 f'{employee[0]} {employee[1]}. '
                                                 f'Кто хочет поздравить?')
                self.set_bot_commands(donate_commands)
        except sqlite3.OperationalError:
            pass

    def notify_scheduler(self):
        """Функция настройки расписания проверки предстоящих дней рождения"""
        schedule.every(60).seconds.do(self.notify)
        schedule.every().day.at('14:00').do(self.delete_money_table)
        while True:
            schedule.run_pending()
            time.sleep(1)
