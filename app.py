import os
from flask import Flask
from threading import Thread
from bot.main import run_bot  # Make sure your bot logic is in bot/main.py

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is online!"

def flask_thread():
    port = int(os.environ.get('PORT', 5000))  # Render provides this PORT
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=flask_thread).start()
    run_bot()  # Starts the Pyrogram bot