import os
import requests
from flask import Flask, request
from datetime import datetime

TOKEN = os.environ.get("TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# ===== ОТПРАВКА СООБЩЕНИЯ =====
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })

# ===== ДНИ НЕДЕЛИ =====
days_map = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday"
}

# ===== ОПРЕДЕЛЕНИЕ ЧЕТНОЙ/НЕЧЕТНОЙ =====
def get_week_type():
    week_number = datetime.now().isocalendar()[1]
    return "even" if week_number % 2 == 0 else "odd"

# ===== РАСПИСАНИЕ =====
schedule = {
    "even": {
        "monday": "📚 Понедельник:\nВыходной",
        "tuesday": "📚 Вторник:\nВыходной",
        "wednesday": "📚 Среда:\nВыходной",
        "thursday": "📚 Четверг:\nВыходной",
        "friday": """📚 Пятница:
09:00–10:30 — Макроэкономика
10:40–12:10 — Регламентация служебной деятельности
12:40–14:10 — Русский язык и культура речи""",
        "saturday": "📚 Суббота:\nВыходной",
        "sunday": "Выходной"
    },
    "odd": {
        "monday": "📚 Понедельник:\nВыходной",
        "tuesday": "📚 Вторник:\nВыходной",
        "wednesday": "📚 Среда:\nВыходной",
        "thursday": "📚 Четверг:\nВыходной",
        "friday": """📚 Пятница:
09:00–10:30 — Макроэкономика
10:40–12:10 — Регламентация служебной деятельности
12:40–14:10 — Русский язык и культура речи""",
        "saturday": "📚 Суббота:\nВыходной",
        "sunday": "Выходной"
    }
}

# ===== СЛЕДУЮЩАЯ ПАРА =====
def get_next_lesson():
    now = datetime.now()
    week_type = get_week_type()
    day_name = days_map[now.weekday()]
    current_time = now.strftime("%H:%M")

    lessons_raw = schedule[week_type][day_name]

    if "Выходной" in lessons_raw:
        return "Сегодня выходной"

    lines = lessons_raw.split("\n")[1:]
    lessons = []

    for line in lines:
        if "—" in line:
            time_part = line.split("—")[0].strip()
            start_time = time_part.split("–")[0]
            lessons.append((start_time, line))

    for start_time, lesson in lessons:
        if current_time <= start_time:
            return f"Следующая пара:\n{lesson}"

    return "На сегодня пар больше нет"

# ===== WEBHOOK =====
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    message = data.get("message") or {}
    chat_id = message.get("chat", {}).get("id")
    text = (message.get("text") or "").lower()

    if not chat_id:
        return "ok"

    week_type = get_week_type()
    today = datetime.now().weekday()
    day_name = days_map[today]

    if text == "/start":
        send_message(chat_id, "Бот работает ✅\nИспользуй: сегодня, завтра, неделя, следующая пара")

    elif "сегодня" in text:
        send_message(chat_id, schedule[week_type][day_name])

    elif "завтра" in text:
        tomorrow = (today + 1) % 7
        send_message(chat_id, schedule[week_type][days_map[tomorrow]])

    elif "неделя" in text:
        result = ""
        for day in days_map.values():
            result += schedule[week_type][day] + "\n\n"
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
