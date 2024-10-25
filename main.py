import logging
import asyncio
from core import bot
from flask import Flask, jsonify
import threading


app = Flask(__name__)

async def main():
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info("initializing userbots...")
    await bot.client.start()
    logger.info("userbots initializing✓")
    logger.info("idling...")
    await bot.idle()  # Menunggu hingga bot dihentikan
    logger.info("stopping userbots...")
    await bot.client.stop()
    logger.info("userbots stopped!")

@app.route('/')
def index():
    return jsonify({"message": "Bot is running! by Mz"})

def run_flask():
    app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    # Menggunakan event loop default
    loop = asyncio.get_event_loop()
    
    # Menjalankan Flask di thread terpisah
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    # Menjalankan bot di event loop utama
    loop.run_until_complete(main())
    
    # Tunggu hingga thread Flask selesai sebelum keluar
    flask_thread.join()
