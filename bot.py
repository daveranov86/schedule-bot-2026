import os
from datetime import datetime, timedelta

import requests
from flask import Flask, request, jsonify

TOKEN = os.environ.get("TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# ===== ДНИ =====
DAYS_MAP = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}

DAY_RU = {
    "monday": "Понедельник",
    "tuesday": "Вторник",
    "wednesday": "Среда",
    "thursday": "Четверг",
    "friday": "Пятница",
    "saturday": "Суббота",
    "sunday": "Воскресенье",
}

# ===== КНОПКИ =====
KEYBOARD = {
    "keyboard": [
        [{"text": "Сегодня"}, {"text": "Завтра"}],
        [{"text": "Неделя"}, {"text": "Следующая пара"}],
    ],
    "resize_keyboard": True,
}

# ===== ОТПРАВКА =====
def send_message(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "reply_markup": KEYBOARD
    })

# ===== ЧЕТНОСТЬ =====
def get_week_type(date=None):
    if date is None:
        date = datetime.now()
    monday = date - timedelta(days=date.weekday())
    return "even" if monday.day % 2 == 0 else "odd"

# ===== РАСПИСАНИЕ =====
SCHEDULE = {
    "even": {
        "monday": [],
        "tuesday": [],
        "wednesday": [
            {"time": "14:20-15:50", "subject": "Физическая культура и спорт", "room": "ФОК-4"},
            {"time": "16:20-17:50", "subject": "Физическая культура и спорт", "room": "ФОК-4"},
            {"time": "18:00-19:30", "subject": "Математический анализ", "room": "257"},
        ],
        "thursday": [
            {"time": "12:40-14:10", "subject": "Конституционное право", "room": "А-310"},
            {"time": "14:20-15:50", "subject": "Экономика государственного и муниципального сектора", "room": "А-462"},
            {"time": "16:20-17:50", "subject": "Экономика государственного и муниципального сектора", "room": "А-462"},
            {"time": "18:00-19:30", "subject": "Макроэкономика", "room": "А-256"},
        ],
        "friday": [
            {"time": "09:00-10:30", "subject": "Макроэкономика", "room": "А-61"},
            {"time": "10:40-12:10", "subject": "Регламентация служебной деятельности государственных гражданских служащих", "room": "А-256"},
            {"time": "12:40-14:10", "subject": "Русский язык и культура речи", "room": "А-324"},
        ],
        "saturday": [
            {"time": "16:20-17:50", "subject": "Математический анализ", "room": "А-462"},
            {"time": "18:00-19:30", "subject": "Математический анализ", "room": "А-462"},
        ],
        "sunday": [],
    },
    "odd": {
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": [
            {"time": "09:00-10:30", "subject": "Макроэкономика", "room": "А-61"},
            {"time": "10:40-12:10", "subject": "Регламентация служебной деятельности государственных гражданских служащих", "room": "А-256"},
            {"time": "12:40-14:10", "subject": "Русский язык и культура речи", "room": "А-324"},
        ],
        "saturday": [],
        "sunday": [],
    }
}

# ===== ФОРМАТ ДНЯ =====
def format_day(day, date=None):
    lessons = SCHEDULE[get_week_type(date)][day]

    if not lessons:
        return f"📚 {DAY_RU[day]}:\nВыходной"

    text = f"📚 {DAY_RU[day]}:\n"
    for l in lessons:
        text += f"{l['time']} — {l['subject']}\n"
    return text.strip()

# ===== СЛЕДУЮЩАЯ ПАРА (ИСПРАВЛЕНО) =====
def get_next_lesson():
    now = datetime.now()
    lessons = SCHEDULE[get_week_type(now)][DAYS_MAP[now.weekday()]]

    if not lessons:
        return "Сегодня выходной"

    current = now.hour * 60 + now.minute

    for l in lessons:
        h, m = map(int, l["time"].split("-")[0].split(":"))
        lesson_time = h * 60 + m

        if lesson_time >= current:
            return f"Следующая пара:\n{l['time']} — {l['subject']}\nКабинет: {l['room']}"

    return "На сегодня пар больше нет"

# ===== WEBHOOK =====
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json() or {}
    msg = data.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = (msg.get("text") or "").lower()

    if not chat_id:
        return "ok"

    if text == "/start":
        send_message(chat_id, "Бот работает\nИспользуй: сегодня, завтра, неделя, следующая пара")

    elif "сегодня" in text:
        send_message(chat_id, format_day(DAYS_MAP[datetime.now().weekday()]))

    elif "завтра" in text:
        d = datetime.now() + timedelta(days=1)
        send_message(chat_id, format_day(DAYS_MAP[d.weekday()], d))

    elif "неделя" in text:
        result = ""
        for d in DAYS_MAP.values():
            result += format_day(d) + "\n\n"
        send_message(chat_id, result)

    elif "следующая" in text:
        send_message(chat_id, get_next_lesson())

    else:
        send_message(chat_id, "Используй: сегодня, завтра, неделя, следующая пара")

    return "ok"

# ===== ЗАПУСК =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
