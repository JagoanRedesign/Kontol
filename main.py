import logging
from core import bot


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


if __name__  == "__main__":
    try:
        import uvloop
    except ImportError:
        pass
    else:
        uvloop.install()
    bot.client.run(main())
