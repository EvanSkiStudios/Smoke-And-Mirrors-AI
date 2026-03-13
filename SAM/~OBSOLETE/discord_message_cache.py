import asyncio

import re
from collections import deque

import discord


class CachedBotMessage:
    def __init__(self, bot_user, content):
        self.author = bot_user          # The bot user
        self.content = content          # Original content
        self.clean_content = content    # Used in process_message
        self.type = discord.MessageType.default  # Default type so process_message works
        self.reference = None           # No reply reference


# used for conversations
current_session_chat_cache = deque(maxlen=40)


def session_chat_cache():
    global current_session_chat_cache
    return current_session_chat_cache


def clear_chat_cache():
    global current_session_chat_cache
    current_session_chat_cache.clear()


# Create a lock
lock = asyncio.Lock()


async def message_history_cache(client, message):
    # Acquire the lock
    async with lock:
        global current_session_chat_cache

        def build_user_prompt(author, nick, content, reply_to=None):
            if reply_to == client.user.name:
                reply_to = None

            if reply_to:
                return f'{author} ({nick}) (Replying to: {reply_to}): "{content}"'
            else:
                return f'{author} ({nick}): "{content}"'

        def build_assistant_prompt(content=""):
            return f'SAM: {content}'

        async def process_message(msg):
            """Process a single Discord message into prompts."""
            # Skip irrelevant messages
            if msg.type in {discord.MessageType.chat_input_command, discord.MessageType.thread_created}:
                return []
            if msg.author in bots_blacklist:
                return []

            author_name = msg.author.name
            author_nick = msg.author.display_name
            content = msg.clean_content

            # remove (tts) tag
            if not message.author.bot and re.search(r"\(tts\)", content, re.IGNORECASE):
                content = re.sub(r"\(tts\)", "", content, flags=re.IGNORECASE)

            # Assistant (bot) message
            if msg.author.id == client.user.id:
                return [build_assistant_prompt(content)]

            # Reply message
            if msg.type == discord.MessageType.reply and msg.reference:
                try:
                    referenced = await msg.channel.fetch_message(msg.reference.message_id)
                except discord.NotFound:
                    referenced = None  # message was deleted
                except discord.Forbidden:
                    referenced = None  # missing permissions
                except discord.HTTPException:
                    referenced = None  # network or other fetch error

                if referenced is None:
                    return []

                prompts = [
                    build_user_prompt(author_name, author_nick, content, referenced.author.name)
                ]
                return prompts

            # Regular user message
            prompts = [build_user_prompt(author_name, author_nick, content)]
            return prompts

        # First-time cache build
        if not current_session_chat_cache:
            logger.debug("Session Cache Not Found -- Creating")
            channel = client.get_channel(message.channel.id)

            history_prompts = []
            async for past_message in channel.history(limit=20):

                if past_message.author in bots_blacklist:
                    # todo -- remove messages from users that are replies to / mention, banned bots
                    continue
                # ignore embeds and empty messages
                if past_message.content == "" and len(past_message.embeds) == 0:
                    continue
                if await message_is_slash_reply(past_message):
                    continue

                history_prompts.extend(await process_message(past_message))

            current_session_chat_cache.extend(reversed(history_prompts))
            logger.debug("Session Cache Created")
            return

        # Incremental update (no assistant prompt for user messages here)
        new_prompts = await process_message(message)
        current_session_chat_cache.extend(new_prompts)
        logger.info(current_session_chat_cache)
