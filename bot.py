import os
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN не найден")

API_BASE = f"https://api.telegram.org/bot{TOKEN}"

with open("schedule.json", "r", encoding="utf-8") as f:
    SCHEDULE = json.load(f)

DAYS = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday"
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

KEYBOARD = {
    "keyboard": [
        [{"text": "Сегодня"}, {"text": "Завтра"}],
        [{"text": "Неделя"}, {"text": "Следующая пара"}]
    ],
    "resize_keyboard": True
}

app = Flask(__name__)


def tg(method, payload):
    requests.post(f"{API_BASE}/{method}", json=payload, timeout=30)


def send_message(chat_id, text):
    tg("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": KEYBOARD
    })


def format_day(day_key):
    lessons = SCHEDULE.get(day_key, [])
    if not lessons:
        return f"{DAY_RU[day_key]}: пар нет 🎉"

    lines = [f"📚 {DAY_RU[day_key]}"]
    for lesson in lessons:
        lines.append(f"{lesson['time']} — {lesson['subject']} — кабинет {lesson['room']}")
    return "\n".join(lines)


def get_next_lesson():
    now = datetime.now()
    day_key = DAYS[now.weekday()]
    current_time = now.strftime("%H:%M")
    lessons = SCHEDULE.get(day_key, [])

    for lesson in lessons:
        start_time = lesson["time"].split("-")[0]
        if current_time <= start_time:
            return lesson
    return None


def handle_message(chat_id, text):
    text = (text or "").strip()

    if text == "/start":
        send_message(
            chat_id,
            "Привет! Я бот с расписанием.\n\n"
            "Команды:\n"
            "/today — расписание на сегодня\n"
            "/tomorrow — расписание на завтра\n"
            "/week — расписание на неделю\n"
            "/next — следующая пара"
        )
        return

    if text in ["/today", "Сегодня"]:
        day_key = DAYS[datetime.now().weekday()]
        send_message(chat_id, format_day(day_key))
        return

    if text in ["/tomorrow", "Завтра"]:
        tomorrow_date = datetime.now() + timedelta(days=1)
        day_key = DAYS[tomorrow_date.weekday()]
        send_message(chat_id, format_day(day_key))
        return

    if text in ["/week", "Неделя"]:
        parts = []
        for day_key in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]:
            parts.append(format_day(day_key))
        send_message(chat_id, "\n\n".join(parts))
        return

    if text in ["/next", "Следующая пара"]:
        lesson = get_next_lesson()
        if lesson:
            send_message(
                chat_id,
                f"📍 Следующая пара:\n"
                f"{lesson['subject']}\n"
                f"🕒 {lesson['time']}\n"
                f"🏫 Кабинет: {lesson['room']}"
            )
        else:
            send_message(chat_id, "На сегодня пар больше нет.")
        return

    send_message(chat_id, "Я понимаю: /start, /today, /tomorrow, /week, /next")


@app.route("/", methods=["GET"])
def home():
    return "OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    message = data.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text", "")

    if chat_id:
        handle_message(chat_id, text)

    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
