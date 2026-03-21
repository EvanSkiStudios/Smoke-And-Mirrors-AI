import os
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from memory_module.message_history import clear_channel_cache
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


class Neuralize(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="neuralize", description="Empties the conversation cache")
    async def Neuralize(self, interaction):
        logger.debug(f'Command issued: neuralize by {interaction.user}')
        if interaction.user.id != int(CONFIG.MASTER_USER_ID):
            await interaction.response.send_message("The inner mechanisms of my mind are an enigma")
        else:

            channel_id = interaction.channel.id
            channel_name = getattr(interaction.channel, "name", str(interaction.user.name))

            logger.info(f'Clearing cache for channel {channel_name}')
            clear_channel_cache(channel_id)

            # send response
            await interaction.response.send_message(
                "https://tenor.com/view/men-in-black-mib-will-smith-u-saw-nothing-kharter-gif-12731469441707899432",
                delete_after=5
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Neuralize(bot))
