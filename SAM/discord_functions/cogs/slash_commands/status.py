import discord
from discord import app_commands
from discord.ext import commands

from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)


def discord_activity_mapper(activity):
    # used to convert the type to string name
    activity_type_map = {
        discord.ActivityType.playing: "playing",
        discord.ActivityType.streaming: "streaming",
        discord.ActivityType.listening: "listening to",
        discord.ActivityType.watching: "watching",
        discord.ActivityType.competing: "competing in",
        discord.ActivityType.custom: "Custom"
    }
    return activity_type_map.get(activity.type, f"Unknown({activity.type.name.lower()})")


class Status(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="status", description="Changes Status to supplied custom")
    async def Status(self, interaction, status: str = None):
        logger.debug(f'Command issued: status by {interaction.user}, {status}')

        if status is not None:
            # max character limit
            arg = status[:128]
            activity = discord.CustomActivity(name=f"{arg}", emoji=' ')
            await self.client.change_presence(activity=activity)
        else:
            activity = None
            await self.client.change_presence(activity=activity)

        # Get the new activity to respond with the new info about the status
        if activity is not None:
            if activity.type == discord.ActivityType.custom:
                await interaction.response.send_message(f"Custom Status is now: {activity.name}")
            else:
                await interaction.response.send_message(f"Status is now: {discord_activity_mapper(activity)} {activity.name}")
        else:
            await interaction.response.send_message("Status has been cleared.")
            logger.info("Status Cleared")
            return

        logger.debug(f"Changed Status to: {activity.type} {activity.name}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))
