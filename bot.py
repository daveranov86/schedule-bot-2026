import os
from datetime import datetime, timedelta

import requests
from flask import Flask, request, jsonify

TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN не найден в переменных окружения")

API_URL = f"https://api.telegram.org/bot{TOKEN}"
app = Flask(__name__)

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

KEYBOARD = {
    "keyboard": [
        [{"text": "Сегодня"}, {"text": "Завтра"}],
        [{"text": "Неделя"}, {"text": "Следующая пара"}],
    ],
    "resize_keyboard": True,
}

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
        "sunday": [],
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
        "sunday": [],
    },
}


def tg_post(method: str, payload: dict) -> None:
    requests.post(f"{API_URL}/{method}", json=payload, timeout=30)


def send_message(chat_id: int, text: str) -> None:
    tg_post(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": KEYBOARD,
        },
    )


def get_week_type(target_date=None) -> str:
    if target_date is None:
        target_date = datetime.now()
    monday = target_date - timedelta(days=target_date.weekday())
    return "even" if monday.day % 2 == 0 else "odd"


def format_day(day_key: str, target_date=None) -> str:
    week_type = get_week_type(target_date)
    lessons = SCHEDULE[week_type][day_key]

    if not lessons:
        return f"📚 {DAY_RU[day_key]}:\nВыходной"

    lines = [f"📚 {DAY_RU[day_key]}:"]
    for lesson in lessons:
        lines.append(f"{lesson['time']} — {lesson['subject']}")
    return "\n".join(lines)


def get_next_lesson() -> str:
    now = datetime.now()
    week_type = get_week_type(now)
    day_key = DAYS_MAP[now.weekday()]
    lessons = SCHEDULE[week_type][day_key]

    if not lessons:
        return "Сегодня выходной"

    current_minutes = now.hour * 60 + now.minute

    for lesson in lessons:
        start_str, end_str = lesson["time"].split("-")

        sh, sm = map(int, start_str.split(":"))
        eh, em = map(int, end_str.split(":"))

        start_minutes = sh * 60 + sm
        end_minutes = eh * 60 + em

        if start_minutes <= current_minutes < end_minutes:
            return (
                "Сейчас идёт:\n"
                f"{lesson['time']} — {lesson['subject']}\n"
                f"Кабинет: {lesson['room']}"
            )

        if current_minutes < start_minutes:
            return (
                "Следующая пара:\n"
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
    message = data.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip().lower()

    if not chat_id:
        return jsonify({"ok": True}), 200

    if text == "/start":
        send_message(
            chat_id,
            "Привет! Я бот с расписанием МИРЭА.\n\n"
            "Команды:\n"
            "сегодня\n"
            "завтра\n"
            "неделя\n"
            "следующая пара",
        )

    elif text in ["сегодня", "/today"]:
        today = datetime.now()
        send_message(chat_id, format_day(DAYS_MAP[today.weekday()], today))

    elif text in ["завтра", "/tomorrow"]:
        tomorrow = datetime.now() + timedelta(days=1)
        send_message(chat_id, format_day(DAYS_MAP[tomorrow.weekday()], tomorrow))

    elif text in ["неделя", "/week"]:
        week_type = get_week_type()
        title = "Чётная неделя" if week_type == "even" else "Нечётная неделя"
        result = [f"📅 {title}"]
        for day_key in DAYS_MAP.values():
            result.append(format_day(day_key))
        send_message(chat_id, "\n\n".join(result))

    elif text in ["следующая пара", "/next"]:
        send_message(chat_id, get_next_lesson())

    else:
        send_message(chat_id, "Используй: сегодня, завтра, неделя, следующая пара")

    return jsonify({"ok": True}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
