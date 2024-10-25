import requests
from datetime import datetime
from pyrogram import Client, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

API_URL = "https://api.myquran.com/v2/sholat/jadwal/1301/{}"
LOCATION = "Asia/Jakarta"

# Kamus untuk melacak pengingat untuk setiap grup
group_reminders = {}
jadwal_sholat = {}

# Inisialisasi scheduler
scheduler = AsyncIOScheduler()

def fetch_jadwal_sholat(chat_id):
    tanggal = datetime.now().strftime("%Y/%m/%d")
    response = requests.get(API_URL.format(tanggal))
    if response.status_code == 200:
        sholat = response.json()
        return {
            'subuh': sholat['data']['jadwal']['subuh'],
            'dzuhur': sholat['data']['jadwal']['dzuhur'],
            'ashar': sholat['data']['jadwal']['ashar'],
            'maghrib': sholat['data']['jadwal']['maghrib'],
            'isya': sholat['data']['jadwal']['isya']
        }
    else:
        print("Error mengambil jadwal")
        return None

async def send_reminder(chat_id, sholat):
    waktu_sekarang = datetime.now().strftime("%H:%M")
    await app.send_message(chat_id, f"🕌 Pukul <code>{waktu_sekarang}</code> WIB, waktunya {sholat} untuk DKI JAKARTA dan sekitarnya.", parse_mode='html')

def check_sholat():
    current_time = datetime.now().strftime("%H:%M")
    for chat_id, reminders_enabled in group_reminders.items():
        if reminders_enabled and chat_id in jadwal_sholat:  # Cek jika pengingat dihidupkan dan jadwal tersedia
            for sholat, waktu in jadwal_sholat[chat_id].items():
                if waktu == current_time:
                    asyncio.run(send_reminder(chat_id, sholat))
                    break  # Hentikan loop setelah mengirim pengingat

@scheduler.scheduled_job('cron', hour=1, minute=0)
def scheduled_fetch_jadwal():
    # Ambil jadwal sholat setiap jam 1 pagi untuk setiap grup
    for chat_id in group_reminders.keys():
        jadwal = fetch_jadwal_sholat(chat_id)
        if jadwal:
            jadwal_sholat[chat_id] = jadwal  # Simpan jadwal sholat untuk grup

@scheduler.scheduled_job('interval', minutes=1)
def scheduled_check():
    check_sholat()

@Client.on_message(filters.command("adzan", prefixes=".") & filters.group)
async def toggle_adzan(c: Client, m):
    chat_id = m.chat.id
    if chat_id not in group_reminders:
        group_reminders[chat_id] = True  # Default dihidupkan

    if len(m.command) < 2:
        await m.reply("Penggunaan: `.adzan on` untuk menghidupkan adzan, `.adzan off` untuk mematikan adzan.")
        return

    command = m.command[1].lower()
    if command == "on":
        group_reminders[chat_id] = True
        await m.reply("Pengingat adzan telah dihidupkan.")
    elif command == "off":
        group_reminders[chat_id] = False
        await m.reply("Pengingat adzan telah dimatikan.")
    else:
        await m.reply("Perintah tidak dikenali. Gunakan `.adzan on` atau `.adzan off`.")

@Client.on_message(filters.command("list_adzan", prefixes=".") & filters.group)
async def list_adzan_groups(c: Client, m):
    active_groups = [str(chat_id) for chat_id, enabled in group_reminders.items() if enabled]
    if active_groups:
        await m.reply("Grup yang mengaktifkan pengingat adzan:\n" + "\n".join(active_groups))
    else:
        await m.reply("Tidak ada grup yang mengaktifkan pengingat adzan saat ini.")

@Client.on_message(filters.command("jadwal", prefixes=".") & filters.group)
async def get_jadwal(c: Client, m):
    chat_id = m.chat.id
    jadwal = fetch_jadwal_sholat(chat_id)
    
    if jadwal:
        jadwal_sholat[chat_id] = jadwal  # Simpan jadwal sholat untuk grup
        jadwal_message = (
            f"📅 Jadwal Sholat untuk hari ini:\n"
            f"🕕 Subuh: {jadwal['subuh']}\n"
            f"🕖 Dzuhur: {jadwal['dzuhur']}\n"
            f"🕔 Ashar: {jadwal['ashar']}\n"
            f"🕕 Maghrib: {jadwal['maghrib']}\n"
            f"🕙 Isya: {jadwal['isya']}"
        )
        await m.reply(jadwal_message)
    else:
        await m.reply("⚠️ Gagal mengambil jadwal sholat, silakan coba lagi nanti.")

scheduler.start()  # Mulai scheduler
