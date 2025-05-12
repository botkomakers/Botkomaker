import os
import aiohttp
import yt_dlp
from flask import Flask
from threading import Thread
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.getenv("API_ID", 123456))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")

# Start Flask server
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is running!"

def run():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

Thread(target=run).start()

# Pyrogram bot
app = Client("auto_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def is_direct_file_link(text):
    return text.lower().startswith("http") and any(text.lower().endswith(ext) for ext in [".mp4", ".mkv", ".avi", ".mp3", ".zip", ".pdf", ".rar"])

def is_video_link(text):
    supported_sites = ["youtube.com", "youtu.be", "facebook.com", "fb.watch", "tiktok.com", "vimeo.com", "dailymotion.com", "twitter.com", "reddit.com"]
    return any(site in text.lower() for site in supported_sites)

@app.on_message(filters.private & filters.command("start"))
async def start_handler(client, message):
    await message.reply_text(
        "**Welcome to Smart Downloader Bot!**\n\n"
        "**Send me any video or file URL. I'll download and send it to you.**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Help", callback_data="help")],
            [InlineKeyboardButton("Join Channel", url="https://t.me/YourChannel")]
        ])
    )

@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    if data == "help":
        await callback_query.message.edit_text(
            "**How to use:**\n"
            "- Send any video link (YouTube, Facebook, etc)\n"
            "- Or direct file link (.mp4, .zip, .pdf, etc)\n"
            "- I'll download and send it."
        )

@app.on_message(filters.private & filters.text & ~filters.command(["start", "help"]))
async def link_handler(client: Client, message: Message):
    url = message.text.strip()
    os.makedirs("downloads", exist_ok=True)

    if is_video_link(url):
        msg = await message.reply("Downloading video...")
        try:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'quiet': True,
                'merge_output_format': 'mp4',
                'cookiefile': 'cookies.txt' if os.path.exists("cookies.txt") else None,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            await msg.edit("Uploading video...")
            await message.reply_video(video=file_path, caption=info.get("title", "Video"))
            os.remove(file_path)

        except Exception as e:
            await msg.edit(f"Failed: {e}")

    elif is_direct_file_link(url):
        msg = await message.reply("Downloading file...")
        filename = url.split("/")[-1]
        filepath = f"downloads/{filename}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await msg.edit(f"Download failed. HTTP {resp.status}")
                    with open(filepath, 'wb') as f:
                        while True:
                            chunk = await resp.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)

            await msg.edit("Uploading file...")
            await message.reply_document(document=filepath, caption="Here is your file.")
            os.remove(filepath)

        except Exception as e:
            await msg.edit(f"File download failed: {e}")
    else:
        await message.reply("Please send a valid video or file link.")

app.run()