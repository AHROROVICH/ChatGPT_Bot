import telebot
from flask import Flask, request
import openai
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Webhook endpoint
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200

# ChatGPT javobi
def get_chatgpt_response(message):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Siz foydalanuvchiga yordam beruvchi aqlli yordamchisiz."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content.strip()

# Foydalanuvchi xabariga javob
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        response = get_chatgpt_response(message.text)
    except Exception as e:
        response = f"Xatolik: {e}"
    bot.send_message(message.chat.id, response)

# Run server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
