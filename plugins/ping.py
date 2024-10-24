import config
import time
from datetime import datetime
from pyrogram import Client, filters, types
from plugins.help.basic import edit_or_reply

StartTime = time.time()

def get_readable_time(seconds: float) -> str:
    """Mengonversi detik ke format waktu yang lebih mudah dibaca."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)

    time_str = []
    if days > 0:
        time_str.append(f"{days}d")
    if hours > 0:
        time_str.append(f"{hours}h")
    if minutes > 0:
        time_str.append(f"{minutes}m")
    if seconds > 0:
        time_str.append(f"{seconds}s")

    return " ".join(time_str) if time_str else "0s"

@Client.on_message(filters.command("ping", config.prefix) & filters.me)
async def kping(client: Client, message: types.Message):
    uptime = await get_readable_time((time.time() - StartTime))
    start = datetime.now()
    xx = await edit_or_reply(message, 
        f"█▀█ █▀█ █▄░█ █▀▀ █ \n"
        f"█▀▀ █▄█ █░▀█ █▄█ ▄"
    )
    end = datetime.now()
    duration = (end - start).microseconds / 1000  # Menghitung durasi dalam milidetik
    await xx.edit(
        f"➠ **Ping !! -** `{duration:.2f} ms`\n"  # Format durasi dengan 2 desimal
        f"➠ **Uptime -** `{uptime}`\n"
        f"➠ **User -** {client.me.mention}"
    )

    

@Client.on_message(filters.command("xping", config.prefix) & filters.me)
async def ping(c: Client, m: types.Message):
    start = m.date
    msg = await m.reply("ping...")
    end = datetime.now()
    return await msg.edit(
        f"<b>Pong!</b>\n<code>{round((end - start).microseconds / 1000)}ms</code>")
