import config
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
    if len(m.command) < 4:
        await m.reply("Penggunaan: `/remind <waktu> <pesan> <jumlah>`\n\nContoh:\n`/remind 1m Beli susu 10`")
        return

    time_from_now = m.command[1]
    text_to_remind = " ".join(m.command[2:-1])  # Mengambil semua kata kecuali yang terakhir
    repeat_count = int(m.command[-1])  # Mengambil jumlah pengulangan

    now = datetime.now(timezone("Asia/Jakarta"))
    delay = parse(time_from_now)

    if delay is None:
        await m.reply("Format waktu tidak valid. Contoh: `1m`, `2h`, `15s`.")
        return

    # Mengirim pengingat sesuai jumlah yang diminta
    for i in range(repeat_count):
        t = now + timedelta(seconds=delay * (i + 1))  # Menghitung waktu untuk setiap pengingat
        reminders.append((t, text_to_remind))
        
        # Kirim pesan terjadwal
        await asyncio.sleep(delay)  # Tunggu selama 'delay'
        await c.send_message(m.chat.id, text_to_remind)

    await m.reply(f"Pengingat disimpan, akan mengirim '{text_to_remind}' sebanyak {repeat_count} kali dengan interval {time_from_now}.")

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


@Client.on_message(filters.command("kirim", config.prefix) & filters.me)
async def schedule_message(c: Client, m: types.Message):
    # Memeriksa panjang perintah
    if len(m.command) < 3:
        await m.reply("Penggunaan: `/kirim <waktu> <pesan>`\n\nContoh:\n`/kirim 01:00 Ini pesan`")
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
        await m.reply(f"Pesan akan dikirim setiap hari pada {scheduled_datetime.strftime('%H:%M')} WIB.")
        
        # Menjadwalkan pengiriman pesan
        while True:
            now = datetime.now(timezone("Asia/Jakarta"))
            if now >= scheduled_datetime:
                await c.send_message(m.chat.id, text_to_send)
                scheduled_datetime += timedelta(days=1)  # Jadwalkan untuk hari berikutnya
            await asyncio.sleep(60)  # Tunggu 1 menit sebelum memeriksa lagi
    else:
        await m.reply("Format waktu tidak valid. Harap gunakan format `HH:MM`.")
