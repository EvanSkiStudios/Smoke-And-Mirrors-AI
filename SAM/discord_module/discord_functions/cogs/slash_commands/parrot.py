import os

from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

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


class Parrot(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="parrot", description="speak")
    async def Parrot(self, interaction, text: str):
        logger.debug(f'Command issued: parrot by {interaction.user}, {text}')

        if interaction.user.id != int(CONFIG.MASTER_USER_ID):
            await interaction.response.send_message("Squawk!")
        else:
            await interaction.response.send_message(f"{text}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Parrot(bot))
