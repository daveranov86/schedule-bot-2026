import os
import requests
from flask import Flask, request

TOKEN = os.environ.get("TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# отправка сообщения
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })

# webhook
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Бот работает ✅")

    return "ok"

# главная страница (чтобы Render не падал)
@app.route("/")
def home():
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
