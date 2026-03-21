import os
import discord

from utility_scripts.namespace_utility import namespace
from utility_scripts.system_logging import setup_logger
from dotenv import load_dotenv

# configure logging
logger = setup_logger(__name__)


# Load Env
load_dotenv()

config_dict = {
    "THREADS_ALLOW": {
        "GMCD_CHANNEL_ID": os.getenv("GMCD_CHANNEL_ID"),
        "TEST_CHANNEL_ID": os.getenv("TEST_CHANNEL_ID")
    },
    "BOTS": {
        "SCUNGEONMASTER": os.getenv("BOT_ID_SCUNGE"),
        "FOOTNOTE": os.getenv("BOT_ID_FOOTNOTE")
    }
}
CONFIG = namespace(config_dict)
bots_blacklist = [int(b) for b in CONFIG.BOTS.__dict__.values()]
channels_whitelist = [int(t) for t in CONFIG.THREADS_ALLOW.__dict__.values()]


async def should_ignore_message(client, message):
    if message.guild is not None:
        if message.channel.id not in channels_whitelist:
            return True

    if message.content == "" and len(message.embeds) == 0:
        # ignores empty messages
        return True

    if await message_is_slash_reply(message):
        return True
    if message.author.id in bots_blacklist:
        return True
    if message.type == discord.MessageType.chat_input_command:
        # slash command messages
        return True
    if message.mention_everyone:
        return True
    if message.author == client.user:
        return True

    return False


async def message_is_slash_reply(message):
    if message.type == discord.MessageType.reply and message.reference:
        try:
            referenced = await message.channel.fetch_message(message.reference.message_id)
        except discord.NotFound:
            referenced = None  # message was deleted
        except discord.Forbidden:
            referenced = None  # missing permissions
        except discord.HTTPException:
            referenced = None  # network or other fetch error

        if referenced is None:
            return False

        if referenced.interaction_metadata is not None:
            # This message is a reply to a slash command response
            return True

    return False
