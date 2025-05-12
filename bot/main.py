import os
import aiohttp
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.getenv("API_ID", 123456))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
COOKIES_FILE = "cookies.txt"

app = Client("downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def is_direct_file_link(text):
    return text.lower().startswith("http") and any(
        text.lower().endswith(ext) for ext in [".mp4", ".mkv", ".avi", ".mp3", ".zip", ".pdf", ".rar"]
    )

def is_video_link(text):
    supported_sites = ["youtube.com", "youtu.be", "facebook.com", "fb.watch", "tiktok.com", "vimeo.com", "dailymotion.com"]
    return any(site in text.lower() for site in supported_sites)

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Help", callback_data="help")],
        [InlineKeyboardButton("Settings", callback_data="settings")],
        [InlineKeyboardButton("Join Channel", url="https://t.me/yourchannel")]
    ])
    await message.reply(
        "Welcome to the bot! Just send a link from YouTube, Facebook, etc. or a direct file link.",
        reply_markup=buttons
    )

@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    if data == "help":
        await callback_query.message.edit("Send a video or file link to start downloading.")
    elif data == "settings":
        await callback_query.message.edit("No settings yet!")

@app.on_message(filters.private & filters.text & ~filters.command(["start", "help"]))
async def handle_links(client, message: Message):
    url = message.text.strip()
    os.makedirs("downloads", exist_ok=True)

    if is_video_link(url):
        msg = await message.reply_text("Downloading video...")
        try:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'merge_output_format': 'mp4',
                'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info_dict)
            await msg.edit("Uploading video...")
            await message.reply_video(video=video_path, caption=info_dict.get("title", "Downloaded"))
            os.remove(video_path)
        except Exception as e:
            await msg.edit(f"Download failed: {e}")

    elif is_direct_file_link(url):
        msg = await message.reply_text("Downloading file...")
        filename = url.split("/")[-1]
        filepath = f"downloads/{filename}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await msg.edit(f"Failed to download. HTTP: {resp.status}")
                    with open(filepath, 'wb') as f:
                        while True:
                            chunk = await resp.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
            await msg.edit("Uploading file...")
            await message.reply_document(document=filepath)
            os.remove(filepath)
        except Exception as e:
            await msg.edit(f"Download failed: {e}")
    else:
        await message.reply_text("Send a valid link.")

app.run()
