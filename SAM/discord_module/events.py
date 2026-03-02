from discord_module.message_router import route_message

from utility_scripts.system_logging import setup_logger


# configure logging
logger = setup_logger(__name__)


def register_events(bot):
    @bot.event
    async def on_ready():
        logger.info(f'We have logged in as {bot.user}')

    @bot.event
    async def on_disconnect():
        logger.error(f"{bot.user} disconnected!")

    @bot.event
    async def on_connect():
        logger.info(f"{bot.user} connected!")

    @bot.event
    async def on_message(message):
        await route_message(bot, message)

