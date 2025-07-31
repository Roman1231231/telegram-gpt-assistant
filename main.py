from flask import Flask, request
import openai
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

STYLES = {
    "💼 Вежливо и делово": "Ответь в деловом, вежливом и уважительном тоне.",
    "⚡️ Кратко и по делу": "Ответь максимально кратко, без лишнего.",
    "😂 С юмором": "Ответь легко, с юмором и неформально, но уместно.",
    "🤔 Уточни вопрос": "Ответь вопросом, чтобы уточнить, что человек имел в виду."
}

def chatgpt_reply(message, style_prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": style_prompt},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content.strip()

def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": reply_markup,
        "parse_mode": "HTML"
    }
    requests.post(f"{TELEGRAM_URL}/sendMessage", json=data)

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text:
            keyboard = {
                "inline_keyboard": [[
                    {"text": key, "callback_data": f"{key}|{text}"}
                ] for key in STYLES.keys()]
            }
            send_message(chat_id, "Выберите стиль ответа:", reply_markup=keyboard)

    elif "callback_query" in data:
        cq = data["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        data_parts = cq["data"].split("|", 1)
        style, original_text = data_parts
        reply = chatgpt_reply(original_text, STYLES[style])
        send_message(chat_id, f"<b>{style}</b>\n{reply}")

    return {"ok": True}

if __name__ == "__main__":
    app.run(debug=True)
