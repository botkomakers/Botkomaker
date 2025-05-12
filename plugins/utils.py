import math
import time

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: '', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {Dic_powerN[n]}B"

async def progress_bar(current, total, message, start, type):
    now = time.time()
    diff = now - start
    percentage = current * 100 / total
    speed = current / diff
    time_to_completion = (total - current) / speed
    estimated_total_time = round(time_to_completion)
    progress = f"[{'█' * int(percentage / 10)}{'-' * (10 - int(percentage / 10))}]"
    text = f"{type}\n{progress} {round(percentage, 2)}%\n{humanbytes(current)} of {humanbytes(total)}\nETA: {estimated_total_time}s"
    try:
        await message.edit(text)
    except:
        pass
