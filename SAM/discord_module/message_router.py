import re
import discord

from discord_functions.discord_message_cache import message_history_cache

from discord_module.llm_handler import llm_chat
from discord_module.message_filters import should_ignore_message

COMMAND_PREFIXES = ["$s "]


def is_keyword_trigger(message_content: str) -> bool:
    if re.search(r"\bsam[\s,.?!]", message_content, re.IGNORECASE):
        return True
    if message_content.lower().endswith("sam"):
        return True
    return False


async def route_message(bot, message):
    """
    Central message routing logic.
    Determines whether a message should be handled by the LLM layer.
    """

    # ---------------------------------
    # 1. Global Ignore Check
    # ---------------------------------
    if await should_ignore_message(bot, message):
        return

    # ---------------------------------
    # 2. Allow command processing
    # ---------------------------------
    await bot.process_commands(message)

    # If message is a command, stop here
    if any(message.content.startswith(prefix) for prefix in COMMAND_PREFIXES):
        return

    # ---------------------------------
    # 3. Ignore empty embed-only messages
    # ---------------------------------
    if message.content == "" and len(message.embeds) != 0:
        # todo manage embeds
        return

    # ---------------------------------
    # 4. Gather Cache
    # ---------------------------------
    # await message_history_cache(bot, message)
    # channel_session_cache = await channel_cache_save_user_message(bot, message)

    # ---------------------------------
    # 5. Hard Routing Decisions
    # ---------------------------------

    # ---------------------------------
    # Direct Message
    # ---------------------------------
    if isinstance(message.channel, discord.DMChannel):
        await llm_chat(bot, message)
        return

    # ---------------------------------
    # Reply to bot message
    # ---------------------------------
    # todo -- Supply copy of referenced message to keep context
    if message.reference and message.type != discord.MessageType.thread_created:
        try:
            # Use resolved message if already provided
            referenced = message.reference.resolved

            # Fallback to API fetch if not cached
            if referenced is None:
                referenced = await message.channel.fetch_message(
                    message.reference.message_id
                )

            if referenced and referenced.author == bot.user:
                await llm_chat(bot, message)
                return

        except discord.NotFound:
            return

    # ---------------------------------
    # Bot mention
    # ---------------------------------
    if bot.user.mentioned_in(message):
        await llm_chat(bot, message)
        return

    # ---------------------------------
    # 6. Keyword Trigger ("sam")
    # ---------------------------------
    message_content = message.clean_content

    if is_keyword_trigger(message_content):
        await llm_chat(bot, message)

