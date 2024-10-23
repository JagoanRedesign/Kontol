import asyncio
import logging
from flask import Flask, jsonify
from core import bot
import threading

app = Flask(__name__)

# Fungsi utama untuk bot
async def run_bot():
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info("initializing userbots...")
    await bot.client.start()
    logger.info("userbots initializing✓")
    logger.info("berjalan ...")
    await bot.idle()  # Menunggu sampai bot dihentikan
    logger.info("stopping userbots...")
    await bot.client.stop()
    logger.info("userbots stopped!")

# Endpoint untuk pemeriksaan kesehatan (diganti menjadi '/')
@app.route('/', methods=['GET'])
def health_check():
    return jsonify(status='healthy'), 200

# Fungsi untuk menjalankan aplikasi Flask
def run_flask():
    app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()  # Ambil event loop saat ini
    
    # Menjalankan bot di thread terpisah
    bot_thread = threading.Thread(target=lambda: loop.run_until_complete(run_bot()))
    bot_thread.start()
    
    # Menjalankan Flask di thread utama
    run_flask()
    
    # Tunggu hingga thread bot selesai sebelum keluar
    bot_thread.join()
