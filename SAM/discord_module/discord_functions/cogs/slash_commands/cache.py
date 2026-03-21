import os
from dotenv import load_dotenv


from discord import app_commands
from discord.ext import commands

from memory_module.message_history import get_channel_message_cache
from utility_scripts.namespace_utility import namespace
from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)

# Load Env
load_dotenv()

config_dict = {
    "MASTER_USER_ID": os.getenv("MASTER_USER_ID"),
}
CONFIG = namespace(config_dict)


class Cache(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="cache", description="Caches N past messages")
    async def Cache(self, interaction, amount: int):
        logger.debug(f'Command issued: cache {interaction.user}, amount: {amount}')

        if interaction.user.id != int(CONFIG.MASTER_USER_ID):
            msg = await interaction.response.send_message("This is an Admin only command.",
                                                          delete_after=6)
            return

        await get_channel_message_cache(self.client, interaction, amount=amount)

        msg = await interaction.response.send_message("cache complete", delete_after=6)


async def setup(bot: commands.Bot):
    await bot.add_cog(Cache(bot))
