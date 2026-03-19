from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import json
import os

TOKEN = os.getenv("TOKEN")

with open("schedule.json", "r", encoding="utf-8") as f:
    SCHEDULE = json.load(f)

DAYS = {0:"monday",1:"tuesday",2:"wednesday",3:"thursday",4:"friday",5:"saturday",6:"sunday"}

DAY_RU = {
    "monday":"Понедельник","tuesday":"Вторник","wednesday":"Среда",
    "thursday":"Четверг","friday":"Пятница","saturday":"Суббота","sunday":"Воскресенье"
}

keyboard = ReplyKeyboardMarkup(
    [["Сегодня","Завтра"],["Неделя","Следующая пара"]],
    resize_keyboard=True
)

def format_day(day):
    lessons = SCHEDULE.get(day, [])
    if not lessons:
        return f"{DAY_RU[day]}: пар нет"

    text = f"📚 {DAY_RU[day]}\n"
    for l in lessons:
        text += f"{l['time']} — {l['subject']} — {l['room']}\n"
    return text

def get_next():
    now = datetime.now()
    day = DAYS[now.weekday()]
    current = now.strftime("%H:%M")

    for l in SCHEDULE.get(day, []):
        start = l["time"].split("-")[0]
        if current <= start:
            return l
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает 👍", reply_markup=keyboard)

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = DAYS[datetime.now().weekday()]
    await update.message.reply_text(format_day(day), reply_markup=keyboard)

async def tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = DAYS[(datetime.now()+timedelta(days=1)).weekday()]
    await update.message.reply_text(format_day(day), reply_markup=keyboard)

async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ""
    for d in ["monday","tuesday","wednesday","thursday","friday","saturday"]:
        text += format_day(d)+"\n\n"
    await update.message.reply_text(text, reply_markup=keyboard)

async def next_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    l = get_next()
    if l:
        await update.message.reply_text(
            f"📍 Следующая пара:\n{l['subject']}\n{l['time']}\nКабинет: {l['room']}",
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text("Пар больше нет", reply_markup=keyboard)

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = update.message.text
    if t == "Сегодня":
        await today(update, context)
    elif t == "Завтра":
        await tomorrow(update, context)
    elif t == "Неделя":
        await week(update, context)
    elif t == "Следующая пара":
        await next_lesson(update, context)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("today", today))
app.add_handler(CommandHandler("tomorrow", tomorrow))
app.add_handler(CommandHandler("week", week))
app.add_handler(CommandHandler("next", next_lesson))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buttons))

app.run_polling()
