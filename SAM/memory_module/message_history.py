from collections import deque

from memory_module.collect_previous_messages import gather_past_messages
from utility_scripts.system_logging import setup_logger


logger = setup_logger(__name__)

channels_dict = {}
MAX_CACHE_SIZE = 40


# for neuralize command
def clear_channel_cache(channel_id):
    if channel_id in channels_dict:
        channels_dict[channel_id].clear()


# creates/gets the section in the dict for the channel
def get_channel_cache(channel_id) -> list:
    if channel_id not in channels_dict:
        channels_dict[channel_id] = deque(maxlen=MAX_CACHE_SIZE)
    return channels_dict[channel_id]


async def get_channel_message_cache(bot, message, amount=20) -> list:
    channel_name = getattr(message.channel, "name", None)

    if channel_name is None:
        channel_name = str(message.author.name)

    logger.info(f'Getting Cache for {channel_name}')

    channel_message_cache = get_channel_cache(message.channel.id)

    # if the cache is empty we will fill it with past messages
    if len(channel_message_cache) == 0:
        logger.info(f'Channel Cache Empty, generating...')
        past_messages = await gather_past_messages(bot, message, amount)

        channel_message_cache.extend(past_messages)
        channel_message_cache.reverse()
        if len(channel_message_cache) > 0:
            channel_message_cache.pop()  # remove last message

    logger.info(f'Channel Cache Complete, Gathered {len(channel_message_cache)} Messages')
    return channel_message_cache

