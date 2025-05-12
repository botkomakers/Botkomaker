import os
from flask import Flask
from threading import Thread
from bot.main import run_bot  # Pyrogram bot

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    Thread(target=run_bot).start()  # Run Pyrogram bot in thread
    run()