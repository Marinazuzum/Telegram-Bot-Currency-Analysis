from telegram import Update 
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

import io
import os #модуль позволяет работать с файловой системой, процессами, окружением и другими аспектами операционной системы.
import psycopg2 # Для работы с базами данных PostgreSQL из Python.
import datetime # Для работы с датами и временем.
import logging # Для логирования событий в программ
import requests # Для выполнения HTTP-запросов
import matplotlib.pyplot as plt # Для визуализации данных


# Настройка логирования. Задаётся формат логов и уровень (INFO)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# Чтение переменных окружения:
TOKEN = os.getenv("BOT_TOKEN") # Токен для работы Telegram-бота
#Python пытается получить значение переменной окружения с именем BOT_TOKEN из текущей среды (например, из операционной системы, 
#Docker-контейнера, или из настроек среды в IDE).
#API токены — это уникальные строки, которые используются для аутентификации и авторизации при взаимодействии с внешними сервисами через их API (Application Programming Interface — интерфейс программирования приложений). 
#Токены API предоставляются сервисами для того, чтобы программы или приложения могли безопасно обращаться к их ресурсам
URL = os.getenv("DATABASE_URL") # URL для подключения к базе данных PostgreSQL
API_KEY = os.getenv("API_KEY") # Ключ API для получения курсов валют
#Переменные окружения (os.getenv): Используются для безопасного хранения конфиденциальной информации (токенов и ключей).
#переменная окружения API_KEY хранит токен API, который используется в коде, но сам токен не хранится прямо в исходном коде.

# Асинхронная функция для получения курсов валют и сохранения их в базу данных
# позволяет программе ожидать завершения асинхронной задачи, прежде чем продолжить выполнение.
#Это важно, чтобы не блокировать выполнение других задач, если код работает в асинхронном режиме (например, в рамках бота, который должен обрабатывать множество запросов одновременно)
async def get_rates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    """
    Функция дает курс валют текущую.
    """# URL API для получения курсов валют
    url = 'https://openexchangerates.org/api/latest.json' #?app_id=6325952bd484428489f6aa5cbd05b08b" (В API-запросах параметры часто передаются в URL как ключ-значение пары. Например, в данном случае ключ app_id содержит значение токена, который используется для аутентификации в сервисе API.)
    # Параметры запроса к API
    params = {
        'app_id':API_KEY, #Это словарь Python, в котором хранится параметр app_id и его значение — уникальный API ключ.
        'base':None, # Базовая валюта (по умолчанию USD, если None).
        'symbols':None, # Список валют, для которых нужны курсы (если None, то все доступные).
    }
    # Выполнение GET-запроса к API.
    response = requests.get(url, params=params)#params- Не нужно вручную собирать URL-строку, параметры автоматически добавляются к запросу.
    # Отправка текста ответа от API в Telegram.
    await update.message.reply_text(response.text) #reply_text() — это метод, который позволяет боту отправить текстовое сообщение в чат в ответ на полученное сообщение. 
    #В данном случае, это текст, который будет отправлен обратно пользователю. не блокируя остальные процессы бота
    #response — это объект, полученный в результате HTTP-запроса с использованием библиотеки requests
    #response.text — это строка, содержащая текстовый ответ от API, который обычно в формате JSON или другом текстовом формате
    # Парсит ответ от сервера в формат JSON, чтобы можно было легко работать с полученными данными. в Python-словарь
    data = response.json() 
    # Извлечение курсов валют, базовой валюты и временной метки из ответа.
    rates = data.get("rates",{})
    base_currency = data.get("base")
    timestamp = data.get("timestamp")
    date= datetime.datetime.fromtimestamp(timestamp).date() # Преобразование временной метки в дату.
    # Подключение к базе данных PostgreSQL.
    conn=psycopg2.connect(URL) #то значение этой переменной ( из .env файла) будет содержать такую строку подключения.
    cursor = conn.cursor()
    #Курсор — это объект, который позволяет работать с результатами SQL-запросов. 
    #Он выполняет запросы, получает результаты и управляет транзакциями.
    # Цикл по всем валютам и их курсам
    for currency, rate in rates.items():
        # Выполнение SQL-запроса для вставки или обновления данных. Передаете фактические значения в виде кортежа или списка:
        cursor.execute("""
                    insert into rates (base_currency, date, currency, rate)
                    values (%s,%s,%s,%s) 
                    on conflict (base_currency, date, currency) do update 
                       set rate = excluded.rate
                    """, (base_currency, date, currency, rate))
     #с использованием механизма ON CONFLICT для обновления данных при наличии дубликатов. Этот фрагмент указывает, что конфликт будет проверяться по тройке столбцов:
     #base_currency, date и currency. Если в таблице уже существует запись с таким же сочетанием значений для этих столбцов, то происходит конфликт.
     #PostgreSQL будет обновлять столбец rate в существующей записи значением excluded.rate, т.е. значением, которое пытались вставить.
     
     #%s — это плейсхолдер для значений, которые будут переданы позже в запрос. Он не является частью SQL-синтаксиса, а используется для безопасной подстановки значений. 
     #Защита от SQL-инъекций
     #Плейсхолдеры заменяются фактическими значениями, переданными в запрос, во время его выполнения.

     # Подтверждение изменений в базе данных.
    conn.commit()
    # Закрытие курсора и соединения с базой данных
    cursor.close()
    conn.close()

     # Отправка сообщения в Telegram о количестве загруженных валют и дате.
    await update.message.reply_text(f"Обменные курсы для {len(rates)} валют загружены в базу данных {date}")
#форматированная строка (f-строка), которая позволяет вставлять переменные в строку. 
# Функция len(rates) возвращает количество элементов в словаре rates, который содержит курсы валют.
#{date} — вставляет дату, которая указывает, когда были загружены данные. Это значение получается из datetime.datetime.fromtimestamp(timestamp).date(),
# то есть это дата, полученная из временной метки timestamp

async def get_historical_rates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Функция загружает исторические курсы валют за указанный период и сохраняет их в базу данных.
    """
    # Получаем параметры периода от пользователя
    try:#Блок, в котором выполняется преобразование строк в даты. Блок try-except необходим для того, чтобы программа не упала с ошибкой, если пользователь введет данные в неправильном формате или забудет указать одну из дат.
         #Вместо этого бот отправит сообщение с просьбой ввести даты в правильном формате.

        start_date = context.args[0]  # Ожидается в формате 'YYYY-MM-DD'
        end_date = context.args[1]    # Ожидается в формате 'YYYY-MM-DD'
        #Преобразуем строки в объекты  datetime
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    except (IndexError, ValueError): #блок, который перехватывает ошибки
        await update.message.reply_text("Укажите даты в формате: /get_historical_rates YYYY-MM-DD YYYY-MM-DD")
        return #Возвращается return, чтобы функция завершилась и не продолжала выполнение, если данные не были получены

    # Проверяем корректность диапазона дат
    if start_date > end_date:
        await update.message.reply_text("Дата начала должна быть раньше даты окончания.")
        return

    conn = psycopg2.connect(URL)
    cursor = conn.cursor()

    total_days = (end_date - start_date).days + 1
    current_date = start_date
    #Отправляем начальное сообщение с заглушкой
    progress_message = await update.message.reply_text("⏳ Загрузка данных...")
    # Список эмодзи для анимации
    fancy_frames = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
    completed_icon = "🟩"  # Заполненная часть прогресса
    remaining_icon = "⬜️"  # Остаток
    
    processed_days = 0
    while current_date <= end_date:
        #Формируем строку даты в формате YYYY-MM-DD
        date_str = current_date.strftime("%Y-%m-%d")

        #Формируем URL для API
        url = f'https://openexchangerates.org/api/historical/{current_date}.json'
        params = {
            'app_id': API_KEY,
            'base': None,
            'symbols': None,
        }
        #Выполняем запрос
        response = requests.get(url, params=params)
        if response.status_code != 200:
            await update.message.reply_text(f"Ошибка при запросе данных за {current_date}: {response.status_code}")
            current_date += datetime.timedelta(days=1)
            continue
        #Обрабатываем данные
        data = response.json()
        rates = data.get("rates", {})
        base_currency = data.get("base")
        timestamp = data.get("timestamp")
        date = datetime.datetime.fromtimestamp(timestamp).date()

        # Сохраняем данные в базу
        for currency, rate in rates.items():
            cursor.execute("""
                INSERT INTO rates (base_currency, date, currency, rate)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (base_currency, date, currency) DO UPDATE
                   SET rate = EXCLUDED.rate
            """, (base_currency, date, currency, rate))

        conn.commit()
        #await update.message.reply_text(f"Курсы валют за {current_date} успешно сохранены.")
        
        # Обновляем прогресс
        processed_days += 1
        progress = int((processed_days / total_days) * 100)
        #Формируем прогресс-бар
        progress_bar = f"[{completed_icon * (progress // 10)}{remaining_icon * (10 - progress // 10)}] {progress}%"

        # Меняющийся кадр анимации
        frame = fancy_frames[processed_days % len(fancy_frames)]

        # Обновляем сообщение
        await progress_message.edit_text(
            f"⏳ Загрузка данных...\n{progress_bar}\n{frame} Обрабатываем {date_str}\n"
            f"📅 Осталось дней: {total_days - processed_days}"
        )
       ##progress_bar = f"[{'#' * (progress // 10)}{'.' * (10 - progress // 10)}] {progress}%"
        ##await progress_message.edit_text(f"⏳ Загрузка данных...\n{progress_bar}")
        current_date += datetime.timedelta(days=1)

    cursor.close()
    conn.close()
    #await update.message.reply_text(f"Обменные курсы за период {start_date} — {end_date} успешно загружены.")
    ##await progress_message.edit_text(f"✅ Обменные курсы за период {start_date} — {end_date} успешно загружены.")
    #Финальное сообщение с фейерверками 🎆
    fireworks = "🎆✨🎇"
    await progress_message.edit_text(
        f"✅ {fireworks} Все данные за период {start_date} — {end_date} успешно загружены! {fireworks}\n"
        f"Спасибо, что воспользовались ботом!"
    )

async def plot(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
    #Объект Update содержит информацию о входящем сообщении, например, текст, пользователя и другие данные. Это объект, 
    # который приходит в вашу функцию, когда пользователь отправляет команду.
    #объект context, который предоставляет доступ к дополнительной информации о контексте команды, например, аргументам команды, состоянию и т. д. 
    # В данном случае, context.args[0] — это первый аргумент команды, который будет валютой, запрашиваемой пользователем
    """
    Функция рисует график курса валют за указанный период.
    """
    currency = context.args[0] #пользователь отправил команду с валютой, например: /plot USD
    await update.message.reply_text(f"Данные по {currency}")
    #метод отправляет текстовое сообщение обратно пользователю в чат. Сообщение будет содержать информацию о валюте, 
    #переданной в команду (например, "Данные по USD").
    try: #Начинает блок обработки исключений для отлова ошибок при работе с базой данных.
     #Почему: Работа с БД мб подвержена множ ошибок (например, проблемы с подкл)
        conn =psycopg2.connect(URL)
        #Устанавливает соединение с БД исп URL.Соединение необх для выполнения SQL-запросов
        cursor =conn.cursor()
        #Создает объект cursor, который используется для выполнения SQL-запросов. 
        # f-строки для вставки переменной currency в запрос
        cursor.execute(f"""select date, rate from rates where currency = '{currency}' 
                        and date >= '2024-12-01'
                        order by date;""")
        #""" использование для переноса строки до и после
        result = cursor.fetchall() #Извлекает все строки, возвращенные запросом, и сохраняет их в переменную result
        #Он возвращает список кортежей, где каждый кортеж представляет собой одну строку из результатов запроса.
        # await update.message.reply_text (f"Данные по {result}")
        conn.commit() 
        #Фиксируем изменение в транзакции
        cursor.close()
        conn.close()
        #Закрывает курсор и соединение с базой данных. Открытые соединения потребляют ресурсы.
    except Exception as e:
        print(f'Ошибка:{e}')
        await update.message.reply_text(f'Ошибка:{e}')

    date = [datetime.datetime.strftime(d[0], '%Y-%m-%d') for d in result]
    #получили список дат по валюте
    rates = [d[1] for d in result]
    #получили список значений обменного курса по валюте

    await update.message.reply_text(f"Данные по {date}")
    await update.message.reply_text(f"Данные по {rates}")

    plt.figure(figsize= (14,8))
    #Создаем стандартный график размером 14 на 8
    #dates  значение по осии x, rates значение по оси  y
    plt.plot(date,rates,marker = 'o', label= f"Обменный курс USD к {currency}")
    plt.xlabel ('Дата')
    plt.ylabel ('Обменный курс')
    plt.legend #Добавляем легенду
    plt.grid #Добавляем сетку
    plt.xticks(rotation=40) #изменяем угол наклона надписей на оси X
    buf =io.BytesIO()
    #Создает объект, который используем как буфер обм для хранения изобр
    plt.savefig(buf, format ='png')
    #сохраняем график в формате пнг в буфер
    buf.seek(0)
    #Перемещаем график в начало буфера обмена чтобы данные  можно было считать
    plt.close()
    #Закрывакм график, чтобы освободить ресурсы (память)
    await update.message.reply_photo(photo=buf, caption =f"График обменного курса USD к {currency}")

def init_db(): # Фунция, которая не принимает аргументов. Она выполняет операции по подключению к базе данных и созданию таблиц.
    """
    Функция для инициализации базы данных PostgreSQL, включая создание нескольких таблиц
    """
    try: #блок происходит подключение к базе данных PostgreSQL с помощью библиотеки psycopg2
        conn=psycopg2.connect(URL)
        cursor = conn.cursor()
        
        #Создания таблицы messages, если она не существует.  
        # Предназначена для хранения простых сообщений от пользователей. Таблица имеет три столбца: 
        # id: автоинкрементный идентификатор (первичный ключ),
        # text: текст сообщения,
        # username: имя пользователя, отправившего сообщение.
        #прямой запрос cursor.execute.Запрос пишется непосредственно в методе cursor.execute 
        cursor.execute("CREATE TABLE IF NOT EXISTS messages (id SERIAL PRIMARY KEY, text TEXT, username TEXT);") 
        
        # Создание таблицы  message_updates, если она еще не существует
        #предназначена для хранения более подробной информации о сообщениях
        #Запрос записывается в отдельной переменной create_table_query с последующим cursor.execute:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS message_updates (
            id SERIAL PRIMARY KEY,
            message_text TEXT,
            user_id BIGINT,
            user_name TEXT,
            is_bot BOOLEAN,
            message_id INT,
            date TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        #где user_id: идентификатор пользователя (BIGINT),
        #is_bot: булевое значение, указывающее, является ли отправитель ботом,

        conn.commit()
        cursor.close()
        conn.close()
        print ('Таблицы message создана')
    except Exception as e:
        print(f'Ошибка:{e}') 

    try:
        conn=psycopg2.connect(URL)
        cursor = conn.cursor()

        # Создание таблицы rates если она не существует
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS rates 
                       (base_currency TEXT,
                        date DATE,
                        currency TEXT,
                        rate REAL,
                        PRIMARY KEY (base_currency, date, currency));""")

        conn.commit()
        cursor.close()
        conn.close()
        print ('Таблицы rates создана')
    except Exception as e:
        print(f'Ошибка:{e}') 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    """
    Функция для начальной настройки взаимодействия с пользователем, отправляя приветственное сообщение
    """
    await update.message.reply_text("Привет, я бот с буткемпа")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Функция эхо-ответ пользователю, сохранение данных в базу
    """
    user_messages = update.message.text 
    user_username = update.message.from_user.username

    await update.message.reply_text(update)
    await update.message.reply_text(user_messages)
    await update.message.reply_text(user_username)
    
    # Сохранение в базу данных
    try:
        conn=psycopg2.connect(URL)
        cursor=conn.cursor()
        cursor.execute("INSERT INTO messages (text, username) VALUES (%s, %s);", (user_messages, user_username))

        # Преобразование UNIX времени в формат TIMESTAMP
        # date = datetime.datetime.fromtimestamp(update.message["date"])

        # Вставка данных в таблицу
        insert_query = """
        INSERT INTO message_updates (message_text, user_id, user_name, is_bot, message_id, date)
        VALUES (%s, %s, %s, %s, %s, %s);
        """

        cursor.execute(insert_query, 
        (
            user_messages,
            update.message.from_user.id,
            update.message.from_user.username,
            update.message.from_user.is_bot,
            update.message.message_id,
            update.message.date
        ))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f'Ошибка:{e}')

async def return_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_username = update.message.from_user.username

    try:
        conn=psycopg2.connect(URL)
        cursor=conn.cursor()
        cursor.execute(f"SELECT text from messages where username = '{user_username}';")
        #Выбираем всю информацию из таблицы messages
        result = cursor.fetchall()
        await update.message.reply_text(result)

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f'Ошибка:{e}')
        await update.message.reply_text(f'Ошибка:{e}')

async def delete_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_username = update.message.from_user.username

    try:
        conn=psycopg2.connect(URL)
        cursor=conn.cursor()
        cursor.execute(f"DELETE from messages where username = '{user_username}';")
        await update.message.reply_text("Deleted")

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f'Ошибка:{e}')
        await update.message.reply_text(f'Ошибка:{e}')

async def update_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_username = update.message.from_user.username

    try:
        conn=psycopg2.connect(URL)
        cursor=conn.cursor()
        cursor.execute(f"UPDATE messages SET text = text || ')' where username = '{user_username}';")
        await update.message.reply_text("Updated")

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f'Ошибка:{e}')
        await update.message.reply_text(f'Ошибка:{e}')
 
def main():

    init_db()

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("return_all_messages", return_all_messages))
    application.add_handler(CommandHandler("delete_all_messages", delete_all_messages))
    application.add_handler(CommandHandler("update_all_messages", update_all_messages))
    application.add_handler(CommandHandler("get_historical_rates", get_historical_rates))
    application.add_handler(CommandHandler("get_rates", get_rates))
    application.add_handler(CommandHandler("plot", plot))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()