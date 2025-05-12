from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    await message.reply(
        "**Welcome to Video Downloader Bot!**\n\n"
        "Just send any video link from YouTube, Facebook, or any platform, "
        "and I'll download it for you."
    )
