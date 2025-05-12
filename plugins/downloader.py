import yt_dlp
import os
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.private & filters.text & ~filters.command("start"))
async def handle_link(client, message: Message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        return

    msg = await message.reply("Downloading video...")

    try:
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        
        await message.reply_video(file_path, caption="Here is your video!")
        os.remove(file_path)
        await msg.delete()
    except Exception as e:
        await msg.edit(f"Failed to download: {e}")
