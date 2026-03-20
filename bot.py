from flask import Flask, request
import requests
from datetime import datetime
import os

app = Flask(__name__)

TOKEN = "ТВОЙ_ТОКЕН"
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

ALLOWED_ID = 1020934186  # твой ID

# ===== РАСПИСАНИЕ =====
SCHEDULE = {
    "default": {
        "monday": [],
        "tuesday": [],
        "wednesday": [
            {"time": "14:20-15:50", "subject": "Физическая культура и спорт", "room": ""},
            {"time": "16:20-17:50", "subject": "Физическая культура и спорт", "room": ""},
            {"time": "18:00-19:30", "subject": "Математический анализ", "room": ""}
        ],
        "thursday": [
            {"time": "12:40-14:10", "subject": "Конституционное право", "room": ""},
            {"time": "14:20-15:50", "subject": "Экономика государственного и муниципального сектора", "room": ""},
            {"time": "16:20-17:50", "subject": "Экономика государственного и муниципального сектора", "room": ""},
            {"time": "18:00-19:30", "subject": "Макроэкономика", "room": ""}
        ],
        "friday": [
            {"time": "09:00-10:30", "subject": "Макроэкономика", "room": "А-61"},
            {"time": "10:40-12:10", "subject": "Регламентация служебной деятельности государственных гражданских служащих", "room": "А-256"},
            {"time": "12:40-14:10", "subject": "Русский язык и культура речи", "room": "А-324"}
        ],
        "saturday": [
            {"time": "16:20-17:50", "subject": "Математический анализ", "room": ""},
            {"time": "18:00-19:30", "subject": "Математический анализ", "room": ""}
        ],
        "sunday": []
    }
}

DAY_RU = {
    "monday": "Понедельник",
    "tuesday": "Вторник",
    "wednesday": "Среда",
    "thursday": "Четверг",
    "friday": "Пятница",
    "saturday": "Суббота",
    "sunday": "Воскресенье"
}

# ===== ОТПРАВКА =====
def send_message(chat_id, text):
    requests.post(URL, json={
        "chat_id": chat_id,
        "text": text
    })

# ===== ФОРМАТ ДНЯ =====
def format_day(day):
    lessons = SCHEDULE["default"][day]

    if not lessons:
        return f"📚 {DAY_RU[day]}:\nВыходной"

    text = f"📚 {DAY_RU[day]}:\n"
    for l in lessons:
        text += f"{l['time']} — {l['subject']}\n"

    return text.strip()

# ===== СЛЕДУЮЩАЯ ПАРА =====
def get_next_lesson():
    now = datetime.now()
    day = now.strftime("%A").lower()
    lessons = SCHEDULE["default"][day]

    if not lessons:
        return "Сегодня выходной"

    current = now.hour * 60 + now.minute

    for lesson in lessons:
        start_str, end_str = lesson["time"].split("-")

        sh, sm = map(int, start_str.split(":"))
        eh, em = map(int, end_str.split(":"))

        start = sh * 60 + sm
        end = eh * 60 + em

        if start <= current < end:
            return f"Сейчас идёт:\n{lesson['time']} — {lesson['subject']}\nКабинет: {lesson['room']}"

        if current < start:
            return f"Следующая пара:\n{lesson['time']} — {lesson['subject']}\nКабинет: {lesson['room']}"

    return "На сегодня пар больше нет"

# ===== WEBHOOK =====
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    msg = data.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = (msg.get("text") or "").lower()

    if not chat_id:
        return "ok"

    # 🔒 ПРИВАТНЫЙ ДОСТУП
    if chat_id != ALLOWED_ID:
        return "ok"

    if text == "/start":
        send_message(chat_id, "Бот работает\n\nКоманды:\nсегодня\nзавтра\nнеделя\nследующая пара")

    elif "сегодня" in text:
        day = datetime.now().strftime("%A").lower()
        send_message(chat_id, format_day(day))

    elif "завтра" in text:
        day_index = (datetime.now().weekday() + 1) % 7
        day = list(DAY_RU.keys())[day_index]
        send_message(chat_id, format_day(day))

    elif "неделя" in text:
        text_week = ""
        for d in DAY_RU:
            text_week += format_day(d) + "\n\n"
        send_message(chat_id, text_week.strip())

    elif "следующая пара" in text:
        send_message(chat_id, get_next_lesson())

    return "ok"

# ===== ЗАПУСК (ВАЖНО ДЛЯ RENDER) =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
