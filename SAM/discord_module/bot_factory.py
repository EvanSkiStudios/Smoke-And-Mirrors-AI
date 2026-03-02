import discord
from discord.ext import commands
from discord_module.config import get_config
from discord_module.events import register_events


# set discord_functions intents
intents = discord.Intents.default()
intents.message_content = True
intents.emojis_and_stickers = True

# gather namespace config
CONFIG = get_config()


class MyBot(commands.Bot):
    async def setup_hook(self):
        # Load cogs here
        cogs = [
            "discord_functions.cogs.bot_commands",
            "discord_functions.cogs.slash_commands.analyze",
            "discord_functions.cogs.slash_commands.delete",
            "discord_functions.cogs.slash_commands.help",
            "discord_functions.cogs.slash_commands.neuralize",
            "discord_functions.cogs.slash_commands.parrot",
            "discord_functions.cogs.slash_commands.search",
            "discord_functions.cogs.slash_commands.status",
            "discord_functions.cogs.slash_commands.tts",
            "discord_functions.cogs.slash_commands.weather"
        ]
        for cog in cogs:
            await self.load_extension(cog)

        # 👇 Sync all commands to one guild
        guild = discord.Object(id=CONFIG.SERVERS.GMCD_SERVER_ID)
        self.tree.copy_global_to(guild=guild)  # copy any global commands
        await self.tree.sync(guild=guild)  # sync them instantly


def create_bot():
    bot = MyBot(
        command_prefix=["$s "],
        intents=intents,
        status=discord.Status.online
    )

    register_events(bot)
    return bot

