# Standard library
import asyncio
import os
import re
from types import SimpleNamespace

# Third-party
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Project / local
from SAM import sam_create, sam_message

from discord_functions.discord_bot_users_manager import handle_bot_message
from discord_functions.discord_message_cache import (
    CachedBotMessage,
    message_history_cache,
    should_ignore_message,
)
from discord_functions.utility.discord_helpers import get_message_attachments
from discord_functions.utility.download_discord_attachments import download_attachments

from message_logs.log_message import log_message

from tools.determine_request import classify_request
from tools.text_to_speech.tts_message_helpers import message_is_tts, send_tts
from tools.weather_search.weather_tool import weather_search
from tools.web_search.internet_tool import llm_internet_search

from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)

# Load Env
load_dotenv()


def ns(d: dict) -> SimpleNamespace:
    """Convert dict into a dot-accessible namespace (recursively)."""
    return SimpleNamespace(**{k: ns(v) if isinstance(v, dict) else v for k, v in d.items()})


config_dict = {
    "BOT": {
        "TOKEN": os.getenv("TOKEN"),
        "APPLICATION_ID": os.getenv("APPLICATION_ID"),
        "SERVER_ID": os.getenv("GMCD_SERVER_ID"),
        "TEST_SERVER_ID": os.getenv("TEST_SERVER_ID"),
        "DM_CHANNEL_ID": os.getenv("DM_CHANNEL_ID"),
        "CHANNEL_ID": os.getenv("GMCD_CHANNEL_ID"),
    },
    "MASTER_USER_ID": os.getenv("MASTER_USER_ID"),
}
CONFIG = ns(config_dict)

# set discord_functions intents
intents = discord.Intents.default()
intents.message_content = True
intents.emojis_and_stickers = True


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
        guild = discord.Object(id=CONFIG.BOT.SERVER_ID)
        self.tree.copy_global_to(guild=guild)  # copy any global commands
        await self.tree.sync(guild=guild)  # sync them instantly


client = MyBot(
    command_prefix=["$s "],
    intents=intents,
    status=discord.Status.online
)

# Startup LLM
sam_create()


# --------- BOT EVENTS ---------
@client.event
async def on_ready():
    # When the bot has logged in, call back
    logger.info(f'We have logged in as {client.user}')


@client.event
async def on_disconnect():
    logger.error(f"{client.user} disconnected!")


@client.event
async def on_connect():
    logger.info(f"{client.user} connected!")


# ------- MESSAGE HANDLERS ---------
async def llm_chat(message):
    username = message.author.name
    user_nickname = message.author.display_name

    # Handle Bot messages
    if message.author.bot:
        result = handle_bot_message(username)
        if result == -1:
            return

    # handle if message is TTS request
    is_tts_message, message_content = message_is_tts(message)

    # ===========================================
    # MAIN MESSAGE HANDLING
    # ===========================================
    async with message.channel.typing():

        # ===========================================
        # Attachments
        # ===========================================
        message_attachments = get_message_attachments(message)

        if message_attachments:
            request_classification = "attachment"
        else:
            request_classification = classify_request(message_content)

        # ===========================================
        # CLASSIFY WHAT TYPE OF RESPONSE IS NEEDED
        # ===========================================

        logger.info(f"Classification={request_classification}, Content={message_content}")

        match request_classification:
            case "attachment":
                loop = asyncio.get_event_loop()
                gathered_attachments = await loop.run_in_executor(None, download_attachments, message_attachments)

                if not gathered_attachments:
                    logger.error("Attachments missing- reverting to basic chat")
                    response = await sam_message()
                else:
                    response = await sam_message(message_attachments=gathered_attachments)

            case "weather_search":
                logger.warning(f"Weather Search")
                logger.info(message.content)
                response = await weather_search(message_content)

            case "search":
                logger.warning(f"WEB Search")
                logger.info(message.content)
                response = await llm_internet_search(message_content)

            case _:
                response = await sam_message()

    # ===========================================
    # Sending Response to Discord
    # ===========================================
    if not response:
        return

    response_content = response["content"]

    # Send messages in parts but store the full response
    full_response = " ".join(response_content)  # combine all parts into one string

    # response should have been split in the above function returns
    sent_message = None
    for i, part in enumerate(response_content):
        if not message.author.bot and i == 0:
            sent_message = await message.reply(part, suppress_embeds=True, mention_author=False)
        else:
            if i != 0:
                await message.channel.send(part, suppress_embeds=True)
            else:
                sent_message = await message.channel.send(part, suppress_embeds=True, mention_author=False)

    if is_tts_message:
        await send_tts(message, response_content[0], reply_target=sent_message)

    # Add the full response to the cache as a single assistant message
    cached_msg = CachedBotMessage(client.user, full_response)
    await message_history_cache(client, cached_msg)

    # ===========================================
    # Logging
    # ===========================================
    user_message = {
        "id": message.id,
        "content": message_content,
        "name": username
    }

    msg = response["message"]

    if hasattr(msg, "thinking"):
        thinking = msg.thinking
    else:
        thinking = "No Thinking"

    await log_message(sent_message, thinking, user_message, response["prompt"])


@client.event
async def on_message(message):
    # ============================
    # If we should ignore the new message
    # ============================

    if await should_ignore_message(client, message):
        return

    await client.process_commands(message)

    if any(message.content.startswith(prefix) for prefix in ["$s "]):
        return

    if message.content == "" and len(message.embeds) != 0:
        # todo manage embeds
        # await message_history_cache(client, message)
        return

    # noinspection PyAsyncCall
    # asyncio.create_task(react_to_messages(message))

    # Gather chat cache
    await message_history_cache(client, message)

# ============================
# Get kind of response
# ============================

    # DMs
    if isinstance(message.channel, discord.DMChannel):
        await llm_chat(message)
        return

    # replying to bot directly
    if message.reference:
        if message.type == discord.MessageType.thread_created:
            return
        referenced_message = await message.channel.fetch_message(message.reference.message_id)
        if referenced_message.author == client.user:
            await llm_chat(message)
            return

    # ping
    if client.user.mentioned_in(message):
        await llm_chat(message)
        return

    # clean content to use for re
    message_content = message.clean_content

    # if the message includes "sam " it will trigger and run the code
    if re.search(r"\bsam[\s,.?!]", message_content, re.IGNORECASE):
        await llm_chat(message)
        return

    if message_content.lower().endswith('sam'):
        await llm_chat(message)
        return


# ============================
# FINISH
# ============================

# Startup discord_functions Bot
client.run(CONFIG.BOT.TOKEN)
