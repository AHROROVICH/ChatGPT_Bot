import os
import telebot
import openai
from flask import Flask, request

# .env dan o'zgaruvchilarni olish
TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Tekshiruv
if not TOKEN or not OPENAI_API_KEY:
    raise ValueError("BOT_TOKEN yoki OPENAI_API_KEY topilmadi. .env faylni tekshiring.")

# Telegram va OpenAI sozlamalari
bot = telebot.TeleBot(TOKEN)
openai.api_key = OPENAI_API_KEY

# Flask app
app = Flask(__name__)

# Webhook endpoint
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# ChatGPT javobini olish
def get_chatgpt_response(message_text):
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Siz foydalanuvchiga yordam beruvchi aqlli yordamchisiz."},
                {"role": "user", "content": message_text}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Xatolik yuz berdi: {e}"

# Har qanday xabarni qabul qilish va javob berish
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    reply = get_chatgpt_response(message.text)
    bot.send_message(message.chat.id, reply)

# Flask serverni ishga tushirish
if __name__ == "__main__":
    # Webhook URL sozlansin (Railway'da ishga tushganda)
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Masalan: https://chatgpt-bot.up.railway.app
    if not WEBHOOK_URL:
        raise ValueError("WEBHOOK_URL topilmadi. Railway URL manzilingizni .env faylga qo‘shing.")

    # Webhookni o‘rnatish
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

    # Flask serverni boshlash
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
