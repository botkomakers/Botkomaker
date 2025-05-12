import os
import aiohttp
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.getenv("API_ID", 123456))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")

app = Client("smart_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

SUPPORTED_SITES = [
    "youtube.com", "youtu.be", "facebook.com", "fb.watch", "tiktok.com",
    "vimeo.com", "dailymotion.com", "instagram.com", "twitter.com", "x.com",
    "reddit.com"
]

SUPPORTED_EXTS = [".mp4", ".mkv", ".avi", ".mp3", ".zip", ".pdf", ".rar"]

@app.on_message(filters.private & filters.command("start"))
async def start_handler(client: Client, message: Message):
    await message.reply_text(
        "**Welcome to Smart Downloader Bot!**\n\n"
        "**Supported Platforms:**\n"
        "- YouTube, Facebook, TikTok, Instagram, Twitter, Reddit\n"
        "- Vimeo, Dailymotion, FB Watch\n"
        "- Direct file links: MP4, MKV, MP3, PDF, ZIP, etc.\n\n"
        "**How to use:**\n"
        "Just send a video or file link. No command needed!",
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
            "**Just send any valid video or file link.**\n"
            "I'll automatically detect it and send the download!"
        )

def is_direct_file_link(url: str) -> bool:
    return url.lower().startswith("http") and any(url.lower().endswith(ext) for ext in SUPPORTED_EXTS)

def is_supported_video_link(url: str) -> bool:
    return any(site in url.lower() for site in SUPPORTED_SITES)

@app.on_message(filters.private & filters.text & ~filters.command(["start", "help"]))
async def link_handler(client: Client, message: Message):
    url = message.text.strip()
    os.makedirs("downloads", exist_ok=True)

    if is_supported_video_link(url):
        try:
            processing = await message.reply_text("Downloading video... Please wait.")
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'quiet': True,
                'merge_output_format': 'mp4',
                'nocheckcertificate': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                path = ydl.prepare_filename(info)

            await processing.edit("Uploading video...")
            await message.reply_video(path, caption=info.get("title", "Here is your video"))
            os.remove(path)
        except Exception as e:
            await message.reply_text("❌ Couldn’t download. Link may be unsupported or private.")

    elif is_direct_file_link(url):
        try:
            processing = await message.reply_text("Downloading file... Please wait.")
            filename = url.split("/")[-1]
            filepath = f"downloads/{filename}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await processing.edit(f"Download failed. HTTP status: {resp.status}")
                    with open(filepath, 'wb') as f:
                        while True:
                            chunk = await resp.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)

            await processing.edit("Uploading file...")
            await message.reply_document(document=filepath, caption="Here is your file.")
            os.remove(filepath)

        except Exception as e:
            await message.reply_text(f"❌ File download failed: {e}")

    else:
        # Only send ONE message if link is invalid
        await message.reply_text("🚫 Please send a valid video or file link from a supported platform.")

app.run()