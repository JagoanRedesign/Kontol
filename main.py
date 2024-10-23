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
    await bot.idle()
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
    
    # Menjalankan bot di thread terpisah
    bot_thread = threading.Thread(target=lambda: loop.run_until_complete(main()))
    bot_thread.start()
    
    # Menjalankan Flask di thread utama
    run_flask()
    
    # Tunggu hingga thread bot selesai sebelum keluar
    bot_thread.join()
