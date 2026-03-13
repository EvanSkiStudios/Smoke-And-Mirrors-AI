from discord import app_commands
from discord.ext import commands


from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="help", description="displays help information")
    async def Help(self, interaction):
        logger.debug(f'Command issued: help by {interaction.user}')

        help_string = """
For Full documentation see: [The S.A.M Wiki](<https://github.com/EvanSkiStudios/Smoke-And-Mirrors-AI/wiki>)
"""

        await interaction.response.send_message(f"{help_string}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
