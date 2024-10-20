import asyncio
import logging
from flask import Flask, jsonify
from core import bot

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

# Endpoint untuk pemeriksaan kesehatan
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status='healthy'), 200

# Fungsi untuk menjalankan aplikasi Flask
def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    try:
        import uvloop
    except ImportError:
        loop = asyncio.get_event_loop()
        # Menjalankan bot di thread terpisah
        loop.run_until_complete(run_bot())
        run_flask()
    else:
        uvloop.install()  # Install uvloop jika tersedia
        loop = asyncio.get_event_loop()
        # Menjalankan bot di thread terpisah
        loop.run_until_complete(run_bot())
        run_flask()
