import os
from types import SimpleNamespace
from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands
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


class Delete(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="delete", description="delete messages")
    async def Delete(self, interaction, messages: str):
        logger.debug(f'Command issued: delete by {interaction.user}')

        if interaction.user.id != int(CONFIG.MASTER_USER_ID):
            msg = await interaction.response.send_message("This is an Admin only command.",
                                                          delete_after=6)
            return

        messages = messages.split(',')

        deleted = []
        failed = []

        for msg_id in messages:
            try:
                msg_id = int(msg_id)
                msg = await interaction.channel.fetch_message(msg_id)
                if msg.author == self.client.user:
                    await msg.delete()
                    deleted.append(msg_id)
                else:
                    failed.append((msg_id, "Not sent by bot"))
            except discord.NotFound:
                failed.append((msg_id, "Message not found"))
            except discord.Forbidden:
                failed.append((msg_id, "Missing permissions"))
            except discord.HTTPException as e:
                failed.append((msg_id, f"HTTP error: {e}"))

        report = []
        if deleted:
            report.append(f"✅ Deleted: {', '.join(map(str, deleted))}")
        if failed:
            report.append("❌ Failed:\n" + "\n".join(f"{i}: {reason}" for i, reason in failed))

        logger.debug(report)
        msg = await interaction.response.send_message("Deleted: (" + str(len(deleted)) + ") Messages", delete_after=6)


async def setup(bot: commands.Bot):
    await bot.add_cog(Delete(bot))
