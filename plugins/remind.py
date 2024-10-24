import config
from datetime import datetime, timedelta
from pyrogram import Client, filters, types
from pytimeparse import parse
from pytz import timezone
from plugins.help.basic import edit_or_reply
import asyncio

# Daftar pengingat yang tersimpan
reminders = []
scheduled_messages = []  # Menyimpan pesan yang dijadwalkan

@Client.on_message(filters.command("remind", config.prefix) & filters.me)
async def remind(c: Client, m: types.Message):
    # Memeriksa panjang perintah
    if len(m.command) < 4:
        await edit_or_reply(m, "**Penggunaan:** `.remind <waktu> <pesan> <jumlah>`\n\n**Contoh:**\n`.remind 1m Beli susu 10`")
        return

    time_from_now = m.command[1]
    text_to_remind = " ".join(m.command[2:-1])  # Mengambil semua kata kecuali yang terakhir
    repeat_count = int(m.command[-1])  # Mengambil jumlah pengulangan

    now = datetime.now(timezone("Asia/Jakarta"))
    delay = parse(time_from_now)

    if delay is None:
        await edit_or_reply(m, "Format waktu tidak valid. **Contoh:** `1m`, `2h`, `15s`.")
        return

    # Menyimpan pengingat
    reminders.append((now + timedelta(seconds=delay), text_to_remind))

    await edit_or_reply(m, f"Pengingat disimpan, akan mengirim '{text_to_remind}' sebanyak {repeat_count} kali dengan interval {time_from_now}.")
    
    # Mengirim pengingat sesuai jumlah yang diminta
    for i in range(repeat_count):
        await asyncio.sleep(delay)  # Tunggu selama 'delay'
        await c.send_message(m.chat.id, text_to_remind)

@Client.on_message(filters.command("rlist", config.prefix) & filters.me)
async def list_reminders(c: Client, m: types.Message):
    if len(reminders) == 0:
        await edit_or_reply(m, "Tidak ada pengingat yang tersimpan.")
    else:
        response = "**Daftar Pengingat:**\n\n"
        for i, (t, text) in enumerate(reminders, start=1):
            response += f"{i}. `{text}` - Dijadwalkan pada {t.strftime('%d/%m/%Y %H:%M:%S')}\n"
        await edit_or_reply(m, response)




@Client.on_message(filters.command("send", config.prefix) & filters.me)
async def schedule_message(c: Client, m: types.Message):
    # Memeriksa panjang perintah
    if len(m.command) < 3:
        await edit_or_reply(m, f"**Penggunaan:** `{config.prefix}send <waktu> <pesan>`\n\n**Contoh:**\n`{config.prefix}send 01:00 Ini pesan`")
        return

    scheduled_time = m.command[1]
    text_to_send = " ".join(m.command[2:])
    
    # Mengonversi waktu ke dalam format datetime
    now = datetime.now(timezone("Asia/Jakarta"))
    if ":" in scheduled_time:
        hour, minute = map(int, scheduled_time.split(":"))
        scheduled_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Jika waktu sudah lewat hari ini, jadwalkan untuk hari berikutnya
        if scheduled_datetime < now:
            scheduled_datetime += timedelta(days=1)
        
        # Menyimpan pesan terjadwal
        scheduled_messages.append((scheduled_datetime, text_to_send))
        await edit_or_reply(m, f"Pesan akan dikirim setiap hari pada {scheduled_datetime.strftime('%H:%M')} WIB.")
        
        # Menjadwalkan pengiriman pesan
        while True:
            now = datetime.now(timezone("Asia/Jakarta"))
            if now >= scheduled_datetime:
                await c.send_message(m.chat.id, text_to_send)
                scheduled_datetime += timedelta(days=1)  # Jadwalkan untuk hari berikutnya
            await asyncio.sleep(60)  # Tunggu 1 menit sebelum memeriksa lagi
    else:
        await m.reply("Format waktu tidak valid. Harap gunakan format `HH:MM`.")




@Client.on_message(filters.command("slist", config.prefix) & filters.me)
async def list_scheduled_messages(c: Client, m: types.Message):
    if len(scheduled_messages) == 0:
        await edit_or_reply(m, "Tidak ada pesan yang dijadwalkan.")
    else:
        response = "**Daftar Pesan Terjadwal:**\n\n"
        for i, (scheduled_time, text) in enumerate(scheduled_messages, start=1):
            response += f"{i}. `{text}` - Dijadwalkan pada {scheduled_time.strftime('%H:%M')} WIB setiap hari.\n"
        await edit_or_reply(m, response)



@Client.on_message(filters.command("sdel", config.prefix) & filters.me)
async def delete_scheduled_message(c: Client, m: types.Message):
    if len(m.command) < 2:
        await edit_or_reply(m, "**Penggunaan:** `.sdel <nomor>`\n\n**Contoh:** `.sdel 1` untuk menghapus pesan pertama.")
        return

    try:
        index = int(m.command[1]) - 1
        if 0 <= index < len(scheduled_messages):
            removed_message = scheduled_messages.pop(index)
            await edit_or_reply(m, f"Pesan '{removed_message[1]}' telah dihapus dari daftar pesan terjadwal.")
        else:
            await edit_or_reply(m, "Nomor tidak valid. Silakan pilih nomor yang ada di daftar.")
    except ValueError:
        await edit_or_reply(m, "Harap masukkan nomor yang valid.")
