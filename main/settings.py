import os
import sqlite3

import telebot
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_CHAT = os.getenv('GROUP_CHAT')
BASE_DONAT = 500

con = sqlite3.connect('database.db', check_same_thread=False)
cur = con.cursor()
bot = telebot.TeleBot(BOT_TOKEN)


# MESSAGES:
start_message = (
    'Привет, я телеграм-бот. Помогаю нашим сотрудникам не забывать '
    'про дни рождения друг друга, а также собирать на подарки. '
    'Меня нужно добавить в чат и рассказать '
    'мне о всех работниках. Подробнее обо мне можно почитать'
    'тут https://github.com/DKDemerchyan/birthdaybot \n\n'
    'Если нужна инструкция или помощь вызывай команду /help'
)

help_message = (
    'Инструкция бота:\n'
    '________________\n'
    'Чтобы добавить нового сотрудника в таблицу напишите его '
    'данные в правильном порядке: ключевое слово "Добавить", '
    'далее данные через один пробел. \n'
    '>>> Добавить Майкл Скотт @telegram_username 15.03\n'
    '________________\n'
    'Чтобы удалить сотрудника из списка необходимо написать ключевое '
    'слово "Удалить" и далее ID сотрудника.\n'
    '>>> Удалить 6 \n'
    '________________\n'
    'Увидеть взносы на сотрудника: ДР <ID сотрудника>\n'
    '>>> ДР 7\n'
    '________________\n'
    'ID можно узнать по команде /table\n'
)
