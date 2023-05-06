### Alpha version 8.0

[ [eng](#Telegram-bot-for-employees-birthdays) / 
  [rus](#Телеграм-бот-для-дней-рождения-сотрудников) ]

# Telegram-bot for employees' birthdays

- Bot notifies employees in the chat about the upcoming birthday of a colleague
- Bot registers the contribution for congratulations
- Saves data to the database
- Clears the chat history
- Adds a new employee to the database
- Removes a former employee from the database


_______________________________________________________________________________
# Телеграм-бот для дней рождения сотрудников

- Бот уведомляет сотрудников в чате о предстоящем дне рождении коллеги
- Бот регистрирует сумму взноса на поздравление
- Сохраняет данные в базу данных
- Очищает историю чата
- Добавляет нового сотрудника в БД
- Удаляет бывшего сотрудника из БД

### Установка

- Добавить в своем боте команды /help, /add, /table (Сделаю автоматическое добавление этих команд при запуске)
- Добавить в корневую папку файл .env, внести в него


### Схема работы

1. Запустить бота
2. Добавить бота в группу и разрешить сообщения
3. Добавить дни рождения сотрудников в таблицу через личные сообщения боту.
При добавлении первого сотрудника будет создана база данных и таблица с датами
рождения
4. Каждый день в 8:00 бот проверяет таблицу на предмет предстоящих дней рождения
5. За два дня до предполагаемого дня рождения (или дней, если у двух и более 
людей совпали даты) бот отправит уведомление в групповой чат и добавит в базу
данных отдельную таблицу для фиксирования взносов сотруднику от коллег
6. Одновременно с уведомлением в чат-боте добавится команда или несколько команд
для отправки взноса
7. Пользователи выбирают команду для отправки взноса
8. Бот регистрирует приходящие команды и заносит в таблицу
9. 