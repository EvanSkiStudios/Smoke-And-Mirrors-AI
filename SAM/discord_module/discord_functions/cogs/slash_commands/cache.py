import os
from types import SimpleNamespace
from dotenv import load_dotenv


import discord
from discord import app_commands
from discord.ext import commands

from memory_module.message_history import get_channel_message_cache
from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)

# Load Env
load_dotenv()

def ns(d: dict) -> SimpleNamespace:
    """Convert dict into a dot-accessible namespace (recursively)."""
    return SimpleNamespace(**{k: ns(v) if isinstance(v, dict) else v for k, v in d.items()})


config_dict = {
    "MASTER_USER_ID": os.getenv("MASTER_USER_ID"),
}
CONFIG = ns(config_dict)


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