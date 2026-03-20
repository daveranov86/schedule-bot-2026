import os
import requests
from flask import Flask, request
from datetime import datetime

TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN not found")

API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "Бот работает", 200


def send_message(chat_id, text):
    requests.post(
        f"{API_URL}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=30,
    )


schedule = {
    "even": {
        "monday": "📚 Понедельник\n09:00–10:30 — История России\n10:40–12:10 — Основы российской государственности\n12:40–14:10 — Административное право\n14:20–15:50 — Экономика государственного и муниципального сектора",
        "tuesday": "📚 Вторник\n09:00–10:30 — Регламентация служебной деятельности\n10:40–12:10 — История России\n12:40–14:10 — Политология\n14:20–15:50 — Конституционное право",
        "wednesday": "📚 Среда\n14:20–15:50 — Физическая культура\n16:20–17:50 — Физическая культура\n18:00–19:30 — Математический анализ",
        "thursday": "📚 Четверг\n12:40–14:10 — Конституционное право\n14:20–15:50 — Экономика государственного и муниципального сектора\n16:20–17:50 — Экономика государственного и муниципального сектора\n18:00–19:30 — Макроэкономика",
        "friday": "📚 Пятница\n09:00–10:30 — Макроэкономика\n10:40–12:10 — Регламентация служебной деятельности\n12:40–14:10 — Русский язык и культура речи",
        "saturday": "📚 Суббота\n16:20–17:50 — Математический анализ\n18:00–19:30 — Математический анализ",
        "sunday": "Выходной",
    },
    "odd": {
        "monday": "📚 Понедельник\n09:00–10:30 — История России\n10:40–12:10 — Основы российской государственности\n12:40–14:10 — Административное право\n14:20–15:50 — Административное право",
        "tuesday": "📚 Вторник\n09:00–10:30 — Регламентация служебной деятельности\n10:40–12:10 — История России\n12:40–14:10 — Основы российской государственности\n14:20–15:50 — Конституционное право",
        "wednesday": "📚 Среда\n16:20–17:50 — Иностранный язык\n18:00–19:30 — Иностранный язык",
        "thursday": "📚 Четверг\n18:00–19:30 — Макроэкономика",
        "friday": "📚 Пятница\n09:00–10:30 — Макроэкономика\n10:40–12:10 — Регламентация служебной деятельности\n12:40–14:10 — Политология",
        "saturday": "📚 Суббота\n10:40–12:10 — Русский язык и культура речи\n12:40–14:10 — Обучение служением",
        "sunday": "Выходной",
    },
}

days_map = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}


def get_week_type():
    # Четность по номеру недели
    week_number = datetime.now().isocalendar()[1]
    return "even" if week_number % 2 == 0 else "odd"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    message = data.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").lower().strip()

    if not chat_id:
        return "ok", 200

    week_type = get_week_type()
    today = datetime.now().weekday()
    day_name = days_map[today]

    if text == "/start":
        send_message(
            chat_id,
            "Бот работает ✅\n\nКоманды:\nсегодня\нзавтра\nнеделя\n/today\n/tomorrow\n/week",
        )
    elif text in ["сегодня", "/today"]:
        send_message(chat_id, schedule[week_type][day_name])
    elif text in ["завтра", "/tomorrow"]:
        tomorrow = (today + 1) % 7
        send_message(chat_id, schedule[week_type][days_map[tomorrow]])
    elif text in ["неделя", "/week"]:
        result = "\n\n".join(schedule[week_type][d] for d in days_map.values())
        send_message(chat_id, result)
    else:
        send_message(chat_id, "Используй: сегодня, завтра, неделя")

    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
