from datetime import datetime, timedelta
from pyrogram import Client, filters, types
from pytimeparse import parse
from pytz import timezone
import asyncio

# Daftar pengingat yang tersimpan
reminders = []

@Client.on_message(filters.command("remind", config.prefix) & filters.me)
async def remind(c: Client, m: types.Message):
    # Memeriksa panjang perintah
    if len(m.command) < 3:
        await m.reply("Penggunaan: `/remind <waktu> <pesan>`\n\nContoh:\n`/remind 1h30m Beli susu`\n`/remind 1d Cek email`")
        return

    time_from_now = m.command[1]
    text_to_remind = " ".join(m.command[2:])
    
    now = datetime.now(timezone("Asia/Jakarta"))
    delay = parse(time_from_now)

    if delay is None:
        await m.reply("Format waktu tidak valid. Contoh: `1h30m`, `2d`, `15m`.")
        return

    t = now + timedelta(seconds=delay)
    reminders.append((t, text_to_remind))
    
    # Kirim pesan terjadwal
    await m.reply(f"Pengingat disimpan, akan dikirim pada {t.strftime('%d/%m/%Y')} pukul {t.strftime('%H:%M:%S')}.")
    
    # Menjadwalkan pengingat
    await asyncio.sleep(delay)  # Tunggu selama 'delay'
    await c.send_message(m.chat.id, text_to_remind)

@Client.on_message(filters.command("listremind", config.prefix) & filters.me)
async def list_reminders(c: Client, m: types.Message):
    if len(reminders) == 0:
        await m.reply("Tidak ada pengingat yang tersimpan.")
    else:
        response = "Daftar Pengingat:\n\n"
        for i, reminder in enumerate(reminders, start=1):
            t, text = reminder
            response += f"{i}. {text} - {t.strftime('%d/%m/%Y %H:%M:%S')}\n"
        await m.reply(response)
