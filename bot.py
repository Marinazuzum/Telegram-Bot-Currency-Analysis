from telegram import Update 
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

import os 
import psycopg2
import datetime

TOKEN = os.getenv("BOT_TOKEN")
URL = os.getenv("DATABASE_URL")

def init_db():
    try:
        conn=psycopg2.connect(URL)
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS messages (id SERIAL PRIMARY KEY, text TEXT);")

        # Создание таблицы
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

        conn.commit()
        cursor.close()
        conn.close()
        print ('Таблицы message создана')
    except Exeption as e:
        print(f'Ошибка:{e}') 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    await update.message.reply_text("Привет, я бот с буткемпа")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_messages = update.message.text 
    await update.message.reply_text(update)
    await update.message.reply_text(user_messages)

    try:
        conn=psycopg2.connect(URL)
        cursor=conn.cursor()
        cursor.execute("INSERT INTO messages (text) VALUES (%s);", (user_messages,))

        # Преобразование UNIX времени в формат TIMESTAMP
        # date = datetime.datetime.fromtimestamp(update.message["date"])

        # Вставка данных в таблицу
        insert_query = """
        INSERT INTO message_updates (message_text, user_id, user_name, is_bot, message_id, date)
        VALUES (%s, %s, %s, %s, %s, %s);
        """

        cursor.execute(insert_query, 
        (
            update.message.text,
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

def main():

    init_db()

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()