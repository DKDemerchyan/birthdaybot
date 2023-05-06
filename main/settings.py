import os
import sqlite3

from dotenv import load_dotenv
import telebot

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_CHAT = os.getenv('GROUP_CHAT')
BASE_DONAT = 500

con = sqlite3.connect('../database.db', check_same_thread=False)
cur = con.cursor()
bot = telebot.TeleBot(BOT_TOKEN)


start_message = (
    'Привет, я телеграм-бот. Помогаю нашим сотрудникам не забывать '
    'про дни рождения друг друга, а также собирать на подарки. '
    'Меня нужно добавить в чат и рассказать '
    'мне о всех работниках. Подробнее обо мне можно почитать'
    'тут https://github.com/DKDemerchyan/birthdaybot \n\n'
    'Если нужна инструкция или помощь вызывай команду /help'
)

help_message = (
    'Чтобы добавить нового сотрудника нужно просто написать мне его '
    'данные в правильном порядке и виде. Напиши мне ключевое слово '
    '"Добавить" и далее данные через один пробел. \n'
    '>>> Добавить Майкл Скотт @telegram_mike 15.03'
    '\n ____________________________ \n\n'
    'Чтобы удалить сотрудника из списка необходимо написать ключевое '
    'слово "Удалить" и далее ID сотрудника. \n\n'
    '>>> Удалить 6 \n\n'
    'ID можно узнать по команде /table'
)
