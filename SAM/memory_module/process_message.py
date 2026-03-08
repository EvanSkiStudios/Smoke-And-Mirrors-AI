import re

import discord

TTS_PATTERN = re.compile(r"\(tts\)", re.IGNORECASE)


async def get_replied_to_author_name(bot, message):
    if message.reference is None:
        return None

    referenced = message.reference.resolved

    if referenced is None:
        try:
            referenced = await message.channel.fetch_message(message.reference.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return None

    if referenced.author.id == bot.user.id:
        return None

    return referenced.author.name


async def process_message(bot, message):
    author = message.author
    content = message.clean_content

    # remove (tts) tag
    if not author.bot:
        content = TTS_PATTERN.sub("", content).strip()

    # Assistant (bot) message
    if author.id == bot.user.id:
        return {'role': 'assistant', 'content': content}

    # Message is a reply
    reply_target_author = await get_replied_to_author_name(bot, message)

    if reply_target_author:
        return {
            'role': 'user',
            'content': f'{author.name} ({author.display_name}) (Replying to: {reply_target_author}): "{content}"'
        }

    # Regular user message
    return {'role': 'user', 'content': f'{author.name} ({author.display_name}): "{content}"'}
