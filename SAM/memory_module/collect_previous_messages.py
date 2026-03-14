import discord

from discord_module.message_filters import bots_blacklist, message_is_slash_reply
from memory_module.process_message import process_message


# filters message based on rules
async def skip_message(message):
    if message.author in bots_blacklist:
        # todo -- remove messages from users that are replies to / mention, banned bots
        return True

    # ignore embeds and empty messages
    if message.content == "" and len(message.embeds) == 0:
        return True

    if await message_is_slash_reply(message):
        return True

    if message.type in {discord.MessageType.chat_input_command, discord.MessageType.thread_created}:
        return True

    return False


async def gather_past_messages(bot, message, amount=20):
    channel = message.channel

    messages = []
    async for past_message in channel.history(limit=amount, before=message):

        # filter past messages
        if await skip_message(past_message):
            continue

        messages.append(await process_message(bot, past_message))

    messages.reverse()

    return messages
