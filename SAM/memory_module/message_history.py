from memory_module.collect_previous_messages import gather_past_messages
from utility_scripts.system_logging import setup_logger


logger = setup_logger(__name__)

channels_dict = {}

# todo -- Append users message, and assitant response to cache after we have created it


# creates/gets the section in the dict for the channel
def get_channel_cache(channel_id) -> list:
    if channel_id not in channels_dict:
        channels_dict[channel_id] = []
    return channels_dict[channel_id]


async def get_channel_message_cache(bot, message) -> list:
    logger.info(f'Getting Cache for {message.channel.name}')

    channel = bot.get_channel(message.channel.id)
    channel_message_cache = get_channel_cache(channel)

    # if the cache is empty we will fill it with past messages
    if len(channel_message_cache) == 0:
        logger.info(f'Channel Cache Empty, generating...')
        # gather last 20 in channel
        past_messages = await gather_past_messages(bot, channel)
        channel_message_cache.extend(past_messages)
        channel_message_cache.reverse()
        channel_message_cache.pop()  # remove last message as it should be what we just sent

    logger.info(f'Channel Cache Complete')
    return channel_message_cache

