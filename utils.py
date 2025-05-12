# Progress bar for upload/download
def progress_bar(current, total, message, progress_args):
    progress = current / total * 100
    text = f"{progress:.2f}% downloaded"
    asyncio.create_task(message.edit(text))

# Convert bytes to human-readable format
def humanbytes(byte_size):
    if byte_size < 1024:
        return f"{byte_size} B"
    elif byte_size < 1048576:
        return f"{byte_size / 1024:.2f} KB"
    elif byte_size < 1073741824:
        return f"{byte_size / 1048576:.2f} MB"
    else:
        return f"{byte_size / 1073741824:.2f} GB"