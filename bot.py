import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import datetime

# Вставь сюда свой токен
TOKEN = "8053791999:AAEsIlnQxkhdrsorNPa3AuTNwteNdFzO-CE"

# Telegram ID владельца бота (появится в логах после первого сообщения)
OWNER_ID = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Команды ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global OWNER_ID
    OWNER_ID = update.effective_user.id
    await update.message.reply_text("Привет! Я твой трекер. Жду твои отчёты каждый вечер.")
    logger.info(f"Owner ID: {OWNER_ID}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Просто пиши свой отчёт в свободной форме. Я всё приму и сохраню. Утром напомню.")

# === Обработка сообщений ===
async def handle_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    logger.info(f"Отчёт от {user.username or user.id} в {now}: {text}")
    await update.message.reply_text("✅ Отчёт принят!")

# === Утреннее напоминание ===
async def morning_reminder(app):
    if OWNER_ID:
        await app.bot.send_message(chat_id=OWNER_ID, text="Доброе утро ☕ Напиши план на день и не забудь действовать! Ты знаешь, зачем ты встал.")
    else:
        logger.warning("Owner ID не установлен. Утреннее напоминание не отправлено.")

# === Запуск ===
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_report))

    # Планировщик на 08:00 по Киеву
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")
    scheduler.add_job(morning_reminder, CronTrigger(hour=8, minute=0), args=[app])
    scheduler.start()

    print("Бот запущен...")
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
