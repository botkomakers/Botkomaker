import os
import aiohttp
import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.getenv("API_ID", 123456))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")

app = Client("smart_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

SUPPORTED_VIDEO_SITES = [
    "youtube.com", "youtu.be",
    "facebook.com", "fb.watch",
    "tiktok.com",
    "vimeo.com",
    "dailymotion.com",
    "instagram.com", "instagr.am",
    "twitter.com", "x.com", "mobile.twitter.com",
    "reddit.com", "bilibili.com",
    "rumble.com", "linkedin.com", "pinterest.com"
]

# Start command
@app.on_message(filters.private & filters.command("start"))
async def start_handler(client: Client, message: Message):
    await message.reply_text(
        "**Welcome to Smart Downloader Bot!**\n\n"
        "**What I can do:**\n"
        "- Auto-download from YouTube, Facebook, TikTok, Instagram, Twitter, Reddit…\n"
        "- Handle direct file links (MP4, MKV, ZIP, PDF, etc.)\n"
        "- Just send any link – no commands needed!\n",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Help", callback_data="help")],
            [InlineKeyboardButton("Join Channel", url="https://t.me/YourChannel")]
        ])
    )

@app.on_callback_query()
async def callback_handler(client, callback_query):
    if callback_query.data == "help":
        await callback_query.message.edit_text(
            "**Help:**\n"
            "• Send me any video or file URL (YouTube, Instagram, Twitter, direct .mp4/.zip etc.)\n"
            "• I’ll download and send it back to you!"
        )

def is_direct_file_link(text):
    return text.lower().startswith("http") and any(
        text.lower().endswith(ext) for ext in [
            ".mp4", ".mkv", ".avi", ".mov",
            ".mp3", ".wav",
            ".zip", ".rar",
            ".pdf", ".docx", ".xlsx", ".pptx"
        ]
    )

def is_video_link(text):
    t = text.lower()
    return t.startswith("http") and any(site in t for site in SUPPORTED_VIDEO_SITES)

@app.on_message(filters.private & filters.text & ~filters.command(["start", "help"]))
async def auto_handler(client: Client, message: Message):
    url = message.text.strip()
    os.makedirs("downloads", exist_ok=True)

    # video-site branch
    if is_video_link(url):
        msg = await message.reply_text("⬇️ Downloading video…")
        try:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'quiet': True,
                'merge_output_format': 'mp4',
                'noplaylist': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            await msg.edit("⬆️ Uploading video…")
            await message.reply_video(video=file_path, caption=info.get("title", "Here’s your video"))
            os.remove(file_path)

        except Exception as e:
            await msg.edit(f"❌ Video download failed:\n`{e}`")

    # direct-file branch
    elif is_direct_file_link(url):
        msg = await message.reply_text("⬇️ Downloading file…")
        filename = url.split("/")[-1].split("?")[0]
        filepath = f"downloads/{filename}"

        try:
            timeout = aiohttp.ClientTimeout(total=300)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await msg.edit(f"❌ Download failed. HTTP {resp.status}")
                    with open(filepath, 'wb') as f:
                        while True:
                            chunk = await resp.content.read(1024 * 64)
                            if not chunk:
                                break
                            f.write(chunk)

            await msg.edit("⬆️ Uploading file…")
            lower = filename.lower()
            if lower.endswith((".mp4", ".mkv", ".avi", ".mov")):
                await message.reply_video(video=filepath, caption="Here’s your video")
            elif lower.endswith((".mp3", ".wav")):
                await message.reply_audio(audio=filepath, caption="Here’s your audio")
            else:
                await message.reply_document(document=filepath, caption="Here’s your file")
            os.remove(filepath)

        except asyncio.TimeoutError:
            await msg.edit("❌ Download timed out.")
        except Exception as e:
            await msg.edit(f"❌ File download failed:\n`{e}`")

    else:
        await message.reply_text("🚫 Please send a valid video or file link from a supported platform.")

app.run()