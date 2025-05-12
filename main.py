from flask import Flask, request
from pyrogram import Client, filters
from context import TOKEN, API_ID, API_HASH, WEBHOOK_URL
from plugins import start, downloader

app = Flask(__name__)
bot = Client("videobot", bot_token=TOKEN, api_id=API_ID, api_hash=API_HASH)

@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()
    if update:
        bot.process_update(update)
    return "OK", 200

@app.route("/", methods=["GET"])
def root():
    return "Bot is running!", 200

bot.start()
print("Bot started, setting webhook...")
bot.set_webhook(WEBHOOK_URL)
print("Webhook set!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
