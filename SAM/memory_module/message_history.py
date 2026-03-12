from memory_module.collect_previous_messages import gather_past_messages
from utility_scripts.system_logging import setup_logger


logger = setup_logger(__name__)

channels_dict = {}


# creates/gets the section in the dict for the channel
def get_channel_cache(channel_id) -> list:
    if channel_id not in channels_dict:
        channels_dict[channel_id] = []
    return channels_dict[channel_id]


async def get_channel_message_cache(bot, message) -> list:
    channel_name = getattr(message.channel, "name", None)

    if channel_name is None:
        channel_name = str(message.channel.recipient)

    logger.info(f'Getting Cache for {channel_name}')

    channel_message_cache = get_channel_cache(message.channel.id)

    # if the cache is empty we will fill it with past messages
    if len(channel_message_cache) == 0:
        logger.info(f'Channel Cache Empty, generating...')
        # gather last 20 in channel
        past_messages = await gather_past_messages(bot, message)

        channel_message_cache.extend(past_messages)
        channel_message_cache.reverse()
        channel_message_cache.pop()  # remove last message as it should be what we just sent

    logger.info(f'Channel Cache Complete, Gathered {len(channel_message_cache)} Messages')
    return channel_message_cache

