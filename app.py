import re
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from yt_dlp import YoutubeDL
from config import temp
from plugins.utils import progress_bar, humanbytes

# Supported platform regex patterns
LINK_PATTERNS = {
    "youtube": r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/\S+",
    "facebook": r"(https?://)?(www\.)?facebook\.com/\S+",
    "tiktok": r"(https?://)?(www\.)?tiktok\.com/\S+",
    "instagram": r"(https?://)?(www\.)?instagram\.com/\S+",
    "twitter": r"(https?://)?(www\.)?(x\.com|twitter\.com)/\S+"
}

# Output template
YDL_OPTS = {
    "format": "bestvideo+bestaudio/best",
    "outtmpl": "downloads/%(title).70s.%(ext)s",
    "writethumbnail": True,
    "merge_output_format": "mp4",
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "geo_bypass": True,
}

def extract_link(text):
    for platform, pattern in LINK_PATTERNS.items():
        match = re.search(pattern, text)
        if match:
            return match.group(0), platform
    return None, None

@Client.on_message(filters.text & filters.private & ~filters.command)
async def auto_download_handler(client: Client, message: Message):
    if temp.IS_PAUSED:
        return

    link, platform = extract_link(message.text)
    if not link:
        return

    processing = await message.reply_text(f"**Detected {platform.capitalize()} link!**\nProcessing download...")

    try:
        await download_and_send(client, message, link, platform, processing)
    except Exception as e:
        await processing.edit(f"**Error:** `{str(e)}`")

async def download_and_send(client, message, link, platform, processing):
    opts = YDL_OPTS.copy()

    def progress_hook(d):
        if d['status'] == 'downloading':
            downloaded = humanbytes(d.get('downloaded_bytes', 0))
            total = humanbytes(d.get('total_bytes', d.get('total_bytes_estimate', 0)))
            speed = humanbytes(d.get('speed', 0))
            eta = d.get('eta', 0)
            text = f"**Downloading:** {downloaded} / {total} ({speed}/s) - ETA {eta}s"
            asyncio.create_task(processing.edit(text))

    opts['progress_hooks'] = [progress_hook]

    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(link, download=True)
        file_path = ydl.prepare_filename(info)
        if not os.path.exists(file_path):
            raise Exception("Download failed.")

    await processing.edit("**Uploading...**")
    caption = f"**{info.get('title', 'Video')}**\nPlatform: `{platform}`"
    duration = int(info.get("duration", 0))

    await message.reply_video(
        video=file_path,
        caption=caption,
        duration=duration,
        supports_streaming=True,
        progress=progress_bar,
        progress_args=("Uploading...", processing)
    )
    await processing.delete()
    os.remove(file_path)

# Initialize the Client
app = Client("video_downloader_bot", bot_token="YOUR_BOT_TOKEN")

# Run the bot
if __name__ == "__main__":
    app.run()