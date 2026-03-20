import os
import requests
from flask import Flask, request
from datetime import datetime

TOKEN = os.environ.get("TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })

# ===== РАСПИСАНИЕ =====

schedule = {
    "even": {  # четная
        "monday": """Понедельник:
09:00–10:30 История России
10:40–12:10 Основы гос.
12:40–14:10 Админ право
14:20–15:50 Экономика""",

        "tuesday": """Вторник:
09:00–10:30 Регламентация
10:40–12:10 История
12:40–14:10 Политология
14:20–15:50 Конституционное право""",

        "wednesday": """Среда:
14:20–15:50 Физра
16:20–17:50 Физра
18:00–19:30 Матан""",

        "thursday": """Четверг:
12:40–14:10 Конституционное право
14:20–15:50 Экономика
16:20–17:50 Экономика
18:00–19:30 Макроэкономика""",

        "friday": """Пятница:
09:00–10:30 Макро
10:40–12:10 Регламентация
12:40–14:10 Русский""",

        "saturday": """Суббота:
16:20–17:50 Матан
18:00–19:30 Матан""",

        "sunday": "Выходной"
    },

    "odd": {  # нечетная
        "monday": """Понедельник:
09:00–10:30 История
10:40–12:10 Основы гос.
12:40–14:10 Админ право
14:20–15:50 Админ право (лекция)""",

        "tuesday": """Вторник:
09:00–10:30 Регламентация
10:40–12:10 История
12:40–14:10 Основы гос.
14:20–15:50 Конституционное право""",

        "wednesday": """Среда:
16:20–17:50 Английский
18:00–19:30 Английский""",

        "thursday": """Четверг:
18:00–19:30 Макроэкономика""",

        "friday": """Пятница:
09:00–10:30 Макро
10:40–12:10 Регламентация
12:40–14:10 Политология""",

        "saturday": """Суббота:
10:40–12:10 Русский
12:40–14:10 Обучение служением""",

        "sunday": "Выходной"
    }
}

days_map = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday"
}

def get_week_type():
    week_number = datetime.now().isocalendar()[1]
    return "even" if week_number % 2 == 0 else "odd"

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").lower()

        week_type = get_week_type()
        today = datetime.now().weekday()
        day_name = days_map[today]

        if text in ["/start"]:
            send_message(chat_id, "Бот работает ✅")

        elif "сегодня" in text or "/today" in text:
            send_message(chat_id, schedule[week_type][day_name])

        elif "завтра" in text or "/tomorrow" in text:
            tomorrow = (today + 1) % 7
            send_message(chat_id, schedule[week_type][days_map[tomorrow]])

        elif "неделя" in text or "/week" in text:
            result = ""
            for day in days_map.values():
                result += schedule[week_type][day] + "\n\n"
            send_message(chat_id, result)

        else:
            send_message(chat_id, "Используй: сегодня / завтра / неделя")

    return "ok"
    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=port)
   
