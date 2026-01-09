import discord
from discord import app_commands
from discord.ext import commands
from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)


def analyze_message(message):
    details = [
        "",
        f"ID: {message.id}",
        f"Author: {message.author}",
        f"Type: {message.type}"
    ]

    if message.attachments:
        details.append(f"\nAttachments: {message.attachments}\n")
        for media in message.attachments:
            details.append(
                f"\nAttachment:\n  Name: {str(media.filename).lower()}\n  Type: {str(media.content_type).lower()}\n  URL: {media.url}"
            )

    if message.embeds:
        for embed in message.embeds:
            details.append(
                "\nEmbed:"
                f"\n  Title: {embed.title}"
                f"\n  Description: {embed.description}"
                f"\n  URL: {embed.url}"
                f"\n  Fields: {embed.fields}"
                f"\n  Footer: {embed.footer}"
                f"\n  Author: {embed.author}"
                f"\n  Image: {embed.image}"
            )

    logger.info("\n".join(details))


class Analyze(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="analyze", description="analyze messages")
    async def Analyze(self, interaction, message_id: str):
        logger.debug(f'Command issued: analyze {interaction.user} | Message: {message_id}')

        try:
            msg_id = int(message_id)
            message = await interaction.channel.fetch_message(msg_id)
            analyze_message(message)
        except discord.NotFound:
            logger.error("Message not found")
        except discord.Forbidden:
            logger.error("Missing permissions")
        except discord.HTTPException as e:
            logger.error(f"HTTP error: {e}")

        msg = await interaction.response.send_message("Analysis sent to console", delete_after=6)


async def setup(bot: commands.Bot):
    await bot.add_cog(Analyze(bot))
