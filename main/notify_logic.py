import datetime as dt
import sqlite3
import time

import schedule
from settings import BASE_DONAT, GROUP_CHAT, bot, con, cur
from telebot import types


class Notifier:
    """Класс Notifier используется для работы с ругелярными действиями бота.
    Устанавливает команды, создает/удаляет таблицы, управляет уведомлениями."""

    general_commands_list = [
        types.BotCommand('/help', 'Помощь'),
        types.BotCommand('/table', 'Посмотреть таблицу')
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
        table_name = 'fund_' + username[1:] + '_' + creation_date
        cur.execute(f'''
            CREATE TABLE IF NOT EXISTS '{table_name}'(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                amount INTEGER NOT NULL
            );
        ''')
        con.commit()

    @staticmethod
    def delete_money_table():
        """Функция для удаления старых таблиц.

        - Из всех таблиц выберет связанные со сборами.
        - Проверит дату создания и удалит, если она старше 180 дней
        """
        cur.execute('''
            SELECT tbl_name
            FROM sqlite_master
            WHERE tbl_name LIKE 'fund%';
        ''')
        funds = cur.fetchall()
        for fund in funds:
            table_date = fund[0].split('_')[-1].split('.')
            table_date = dt.date(
                year=int(table_date[2]),
                month=int(table_date[1]),
                day=int(table_date[0])
            )
            if table_date < dt.date.today() - dt.timedelta(days=180):
                cur.execute(f'''
                    DROP TABLE '{fund[0]}';
                ''')
                con.commit()

    def notify(self):
        """Функция уведомления в группе о дне рождения коллеги.

        - Проверяет есть ли завтра дни рождения.
        - При выполнении условия для каждого создает бот-команду для доната,
        таблицу для регистрации сборов.
        - Отправляет уведомление в чат.
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
                    print(employee)
                    donate_commands.append(types.BotCommand(
                        f'/donate_{employee[2][1:]}',
                        f'Отправить {BASE_DONAT} {employee[2]}'
                    ))
                    self.create_money_table(employee[2])
                    bot.send_message(
                        GROUP_CHAT,
                        f'Всем привет! Завтра день рождения празднует '
                        f'{employee[0]} {employee[1]}. Кто хочет поздравить?'
                    )
                self.set_bot_commands(donate_commands)

        except sqlite3.OperationalError:
            pass

    def notify_scheduler(self):
        """Функция настройки расписания проверки предстоящих дней рождения"""
        schedule.every(500).seconds.do(self.notify)
        # schedule.every(10).seconds.do(self.delete_money_table)
        schedule.every().sunday.at('21:00').do(self.delete_money_table)
        while True:
            schedule.run_pending()
            time.sleep(1)
