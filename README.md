### Beta version 2.0

- Продумать установку вариант 2: форкать и добавлять
переменные в security в гитхабе

[ [eng](#Telegram-bot-for-employees-birthdays) / 
  [rus](#Телеграм-бот-для-дней-рождения-сотрудников) ]

# Telegram bot for employee birthdays

- The bot notifies employees in the chat about the upcoming birthday of a colleague.
- The bot registers a contribution for congratulations.
- Saves data to the database, allowing you to view directly from private
messages
- Adds a new employee to the database.
- Removes a former employee from the database.
- Deletes old contribution records.

### Installation

- Fork the repository
- Clone it to a remote server where the bot will be running
> git clone <-ssh->
- Add the ".env" file to the /main folder, add the group chat ID and token of 
bot
> BOT_TOKEN = '<bot token received from BotFather>'
> GROUP_CHAT = <Your group chat ID>
- Launch the bot with the command:
> docker-compose up

### Scheme of work

1. Launch the bot, add it to the group and allow messages.
2. Add employee birthdays to the table via private messages to the bot.
When adding the first employee, a database and a table with dates
of birth will be created.
3. Every day at 8:00, the bot checks the table for upcoming birthdays.
4. The day before the expected birthday (or days if two or more 
people's dates coincided) the bot will send a notification to the group chat and add
a separate table to the database to record contributions to the employee from colleagues.
5. Simultaneously with the notification, a team or several teams will be added to the chatbot
to send the contribution.
6. Users send commands to send a contribution.
7. The bot registers incoming commands and enters them into the table.
8. The table can be viewed from personal messages with the bot.

_______________________________________________________________________________
# Телеграм-бот для дней рождения сотрудников

- Бот уведомляет сотрудников в чате о предстоящем дне рождении коллеги.
- Бот регистрирует взнос на поздравление.
- Сохраняет данные в базу данных, позволяя просматривать прямо из личных 
сообщений
- Добавляет нового сотрудника в БД.
- Удаляет бывшего сотрудника из БД.
- Удаляет старые записи о взносах.

### Установка

- Форкните репозиторий
- Клонируйте его на удаленный сервер, на котором будет запущен бот
> git clone <-ssh->
- Добавьте в папку /main файл ".env", внести в него ID группового чата и токен 
бота
> BOT_TOKEN = '<токен бота, получаемый из BotFather>'
> GROUP_CHAT = <ID вашего группового чата>
- Запустите бота командой:
> docker-compose up


### Схема работы

1. Запустить бота, добавить в группу и разрешить сообщения.
2. Добавить дни рождения сотрудников в таблицу через личные сообщения боту.
При добавлении первого сотрудника будет создана база данных и таблица с датами
рождения.
3. Каждый день в 8:00 бот проверяет таблицу на предмет предстоящих дней рождения.
4. За день до предполагаемого дня рождения (или дней, если у двух и более 
людей совпали даты) бот отправит уведомление в групповой чат и добавит в базу
данных отдельную таблицу для фиксирования взносов сотруднику от коллег.
5. Одновременно с уведомлением в чат-боте добавится команда или несколько команд
для отправки взноса.
6. Пользователи отправляют команды для отправки взноса.
7. Бот регистрирует приходящие команды и заносит в таблицу.
8. Таблицу можно посмотреть из личных сообщений с ботом.
