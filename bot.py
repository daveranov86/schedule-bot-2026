import os
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

TOKEN = os.getenv("TOKEN")
BASE_URL = os.getenv("BASE_URL")

if not TOKEN:
    raise ValueError("TOKEN не найден в переменных окружения")

if not BASE_URL:
    raise ValueError("BASE_URL не найден в переменных окружения")

BASE_URL = BASE_URL.rstrip("/")
API_URL = f"https://api.telegram.org/bot{TOKEN}"
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

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


def telegram_request(method: str, data: dict):
    url = f"{API_URL}/{method}"
    return requests.post(url, json=data, timeout=30)


def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": KEYBOARD
    }
    telegram_request("sendMessage", payload)


def format_day(day):
    lessons = SCHEDULE.get(day, [])
    if not lessons:
        return f"{DAY_RU[day]}: пар нет 🎉"

    lines = [f"📚 {DAY_RU[day]}"]
    for lesson in lessons:
        lines.append(f"{lesson['time']} — {lesson['subject']} — кабинет {lesson['room']}")
    return "\n".join(lines)


def get_next_lesson():
    now = datetime.now()
    day = DAYS[now.weekday()]
    current = now.strftime("%H:%M")

    for lesson in SCHEDULE.get(day, []):
        start = lesson["time"].split("-")[0]
        if current <= start:
            return lesson
    return None


def handle_text(chat_id, text):
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
        day = DAYS[datetime.now().weekday()]
        send_message(chat_id, format_day(day))
        return

    if text in ["/tomorrow", "Завтра"]:
        day = DAYS[(datetime.now() + timedelta(days=1)).weekday()]
        send_message(chat_id, format_day(day))
        return

    if text in ["/week", "Неделя"]:
        text_out = "\n\n".join(
            format_day(d) for d in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        )
        send_message(chat_id, text_out)
        return

    if text in ["/next", "Следующая пара"]:
        lesson = get_next_lesson()
        if lesson:
            send_message(
                chat_id,
                f"📍 Следующая пара:\n"
                f"{lesson['subject']}\n"
                f"{lesson['time']}\n"
                f"Кабинет: {lesson['room']}"
            )
        else:
            send_message(chat_id, "На сегодня пар больше нет.")
        return

    send_message(chat_id, "Я понимаю команды: /start, /today, /tomorrow, /week, /next")


def set_webhook():
    response = requests.post(
        f"{API_URL}/setWebhook",
        json={"url": WEBHOOK_URL},
        timeout=30
    )
    print("SET WEBHOOK URL:", WEBHOOK_URL)
    print("SET WEBHOOK STATUS:", response.status_code)
    print("SET WEBHOOK RESPONSE:", response.text)


@app.get("/")
def health():
    return "ok", 200


@app.post(WEBHOOK_PATH)
def webhook():
    update = request.get_json(silent=True) or {}
    message = update.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text", "")

    if chat_id:
        handle_text(chat_id, text)

    return jsonify({"ok": True})


if __name__ == "__main__":
    set_webhook()
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
