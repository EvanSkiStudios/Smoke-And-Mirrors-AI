import discord
from discord import app_commands
from discord.ext import commands

from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)


class Status(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="status", description="Changes Status to supplied custom")
    @app_commands.choices(activity_type=[
        app_commands.Choice(name="Custom", value="custom"),
        app_commands.Choice(name="Playing", value="playing"),
        app_commands.Choice(name="Streaming", value="streaming"),
        app_commands.Choice(name="Listening", value="listening"),
        app_commands.Choice(name="Watching", value="watching"),
        app_commands.Choice(name="Competing", value="competing"),
    ])
    async def status(
        self,
        interaction,
        status: str = None,
        activity_type: app_commands.Choice[str] = None
    ):
        logger.debug(f'Command issued: status by {interaction.user}, {status}, {activity_type}')

        # Clear status if nothing provided
        if status is None:
            await self.client.change_presence(activity=None)
            await interaction.response.send_message("Status has been cleared.", delete_after=6)
            logger.info("Status Cleared")
            return

        # Validate input
        if not status.strip():
            await interaction.response.send_message("You must provide a status message.", ephemeral=True)
            return

        arg = status[:128]

        # Determine activity
        if activity_type is not None:
            mapped_type = discord_keyword_mapper(activity_type.value)

            if mapped_type == discord.ActivityType.streaming:
                activity = discord.Streaming(name=arg, url="https://twitch.tv/")
            elif mapped_type and mapped_type != discord.ActivityType.custom:
                activity = discord.Activity(type=mapped_type, name=arg)
            else:
                activity = discord.CustomActivity(name=arg)

        else:
            # fallback to keyword parsing
            parts = arg.split(" ", 1)
            keyword = parts[0].lower()
            rest = parts[1] if len(parts) > 1 else ""

            mapped_type = discord_keyword_mapper(keyword)

            if isinstance(mapped_type, discord.ActivityType) and mapped_type != discord.ActivityType.custom:
                if not rest:
                    await interaction.response.send_message(
                        "You must provide a name for the activity.",
                        ephemeral=True
                    )
                    return

                if mapped_type == discord.ActivityType.streaming:
                    activity = discord.Streaming(name=rest, url="https://twitch.tv/")
                else:
                    activity = discord.Activity(type=mapped_type, name=rest)
            else:
                activity = discord.CustomActivity(name=arg)

        # Apply presence
        await self.client.change_presence(activity=activity)

        # Respond to user
        if activity.type == discord.ActivityType.custom:
            await interaction.response.send_message(
                f"Custom Status is now: {activity.name}",
                delete_after=6
            )
        else:
            await interaction.response.send_message(
                f"Status is now: {discord_activity_mapper(activity)} {activity.name}",
                delete_after=6
            )

        logger.debug(f"Changed Status to: {activity.type} {activity.name}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))


def discord_keyword_mapper(keyword):
    activity_keyword_map = {
        "playing": discord.ActivityType.playing,
        "streaming": discord.ActivityType.streaming,
        "listening": discord.ActivityType.listening,
        "watching": discord.ActivityType.watching,
        "competing": discord.ActivityType.competing,
        "custom": discord.ActivityType.custom
    }

    return activity_keyword_map.get(keyword)


def discord_activity_mapper(activity):
    activity_type_map = {
        discord.ActivityType.playing: "playing",
        discord.ActivityType.streaming: "streaming",
        discord.ActivityType.listening: "listening to",
        discord.ActivityType.watching: "watching",
        discord.ActivityType.competing: "competing in",
        discord.ActivityType.custom: "Custom"
    }

    return activity_type_map.get(
        activity.type,
        f"Unknown({activity.type.name.lower()})"
    )