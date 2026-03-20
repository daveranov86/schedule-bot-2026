from flask import Flask, request
import requests
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Если TOKEN уже есть в Render -> оставь как есть
TOKEN = os.environ.get("TOKEN", "8760259729:AAGD0y2l7IM0UxjyptOPB6NLZPeVga-lEVc")
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

ALLOWED_ID = 1020934186  # твой Telegram ID

DAY_RU = {
    "monday": "Понедельник",
    "tuesday": "Вторник",
    "wednesday": "Среда",
    "thursday": "Четверг",
    "friday": "Пятница",
    "saturday": "Суббота",
    "sunday": "Воскресенье"
}

DAY_KEYS = list(DAY_RU.keys())

SCHEDULE = {
    "even": {
        "monday": [
            {"time": "09:00-10:30", "subject": "История России", "room": "А-462"},
            {"time": "10:40-12:10", "subject": "Основы российской государственности", "room": "А-401"},
            {"time": "12:40-14:10", "subject": "Административное право", "room": "А-346"},
            {"time": "14:20-15:50", "subject": "Экономика государственного и муниципального сектора", "room": "А-463"},
        ],
        "tuesday": [
            {"time": "09:00-10:30", "subject": "Регламентация служебной деятельности государственных гражданских служащих", "room": "Б-310"},
            {"time": "10:40-12:10", "subject": "История России", "room": "А-63"},
            {"time": "12:40-14:10", "subject": "Политология", "room": "А-63"},
            {"time": "14:20-15:50", "subject": "Конституционное право", "room": "А-523"},
        ],
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
        "sunday": []
    },

    "odd": {
        "monday": [
            {"time": "09:00-10:30", "subject": "История России", "room": "А-462"},
            {"time": "10:40-12:10", "subject": "Основы российской государственности", "room": "А-401"},
            {"time": "12:40-14:10", "subject": "Административное право", "room": "А-346"},
            {"time": "14:20-15:50", "subject": "Административное право", "room": "А-463"},
        ],
        "tuesday": [
            {"time": "09:00-10:30", "subject": "Регламентация служебной деятельности государственных гражданских служащих", "room": "Б-310"},
            {"time": "10:40-12:10", "subject": "История России", "room": "А-63"},
            {"time": "12:40-14:10", "subject": "Основы российской государственности", "room": "А-63"},
            {"time": "14:20-15:50", "subject": "Конституционное право", "room": "А-523"},
        ],
        "wednesday": [
            {"time": "16:20-17:50", "subject": "Иностранный язык", "room": "И-318"},
            {"time": "18:00-19:30", "subject": "Иностранный язык", "room": "И-318"},
        ],
        "thursday": [
            {"time": "18:00-19:30", "subject": "Макроэкономика", "room": "А-256"},
        ],
        "friday": [
            {"time": "09:00-10:30", "subject": "Макроэкономика", "room": "А-61"},
            {"time": "10:40-12:10", "subject": "Регламентация служебной деятельности государственных гражданских служащих", "room": "А-256"},
            {"time": "12:40-14:10", "subject": "Политология", "room": "А-324"},
        ],
        "saturday": [
            {"time": "10:40-12:10", "subject": "Русский язык и культура речи", "room": "А-63"},
            {"time": "12:40-14:10", "subject": "Обучение служением", "room": "А-345"},
        ],
        "sunday": []
    }
}


def msk_now():
    return datetime.utcnow() + timedelta(hours=3)


def send_message(chat_id, text):
    requests.post(
        URL,
        json={
            "chat_id": chat_id,
            "text": text
        },
        timeout=20
    )


def get_week_type(target_date=None):
    if target_date is None:
        target_date = msk_now()

    monday = target_date - timedelta(days=target_date.weekday())
    return "even" if monday.day % 2 == 0 else "odd"


def format_day(day, target_date=None):
    week_type = get_week_type(target_date)
    lessons = SCHEDULE[week_type][day]

    if not lessons:
        return f"📚 {DAY_RU[day]}:\nВыходной"

    text = f"📚 {DAY_RU[day]}:\n"
    for lesson in lessons:
        text += f"{lesson['time']} — {lesson['subject']}\n"
    return text.strip()


def get_next_lesson():
    now = msk_now()
    day = DAY_KEYS[now.weekday()]
    week_type = get_week_type(now)
    lessons = SCHEDULE[week_type][day]

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
            return (
                f"Сейчас идёт:\n"
                f"{lesson['time']} — {lesson['subject']}\n"
                f"Кабинет: {lesson['room']}"
            )

        if current < start:
            return (
                f"Следующая пара:\n"
                f"{lesson['time']} — {lesson['subject']}\n"
                f"Кабинет: {lesson['room']}"
            )

    return "На сегодня пар больше нет"


@app.route("/", methods=["GET"])
def home():
    return "Бот работает", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    msg = data.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = (msg.get("text") or "").strip().lower()

    if not chat_id:
        return "ok", 200

    if chat_id != ALLOWED_ID:
        return "ok", 200

    if text == "/start":
        send_message(
            chat_id,
            "Бот работает ✅\n\nКоманды:\nСегодня\nЗавтра\nНеделя\nСледующая пара"
        )

    elif text == "сегодня":
        today = msk_now()
        day = DAY_KEYS[today.weekday()]
        send_message(chat_id, format_day(day, today))

    elif text == "завтра":
        tomorrow = msk_now() + timedelta(days=1)
        day = DAY_KEYS[tomorrow.weekday()]
        send_message(chat_id, format_day(day, tomorrow))

    elif text == "неделя":
        now = msk_now()
        week_type = get_week_type(now)
        title = "📅 Чётная неделя" if week_type == "even" else "📅 Нечётная неделя"

        text_week = title + "\n\n"
        for d in DAY_KEYS:
            text_week += format_day(d, now) + "\n\n"

        send_message(chat_id, text_week.strip())

    elif text == "следующая пара":
        send_message(chat_id, get_next_lesson())

    else:
        send_message(chat_id, "Используй: Сегодня, Завтра, Неделя, Следующая пара")

    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
