from memory_module.collect_previous_messages import gather_past_messages

channels_dict = {}


# creates/gets the section in the dict for the channel
def get_channel_cache(channel_id):
    if channel_id not in channels_dict:
        channels_dict[channel_id] = []
    return channels_dict[channel_id]


async def channel_cache_message(bot, message):
    channel = bot.get_channel(message.channel.id)
    channel_message_cache = get_channel_cache(channel)

    # if the cache is empty we will fill it with past messages
    if len(channel_message_cache) == 0:
        # gather last 20 in channel
        past_messages = await gather_past_messages(bot, channel)
        channel_message_cache.extend(past_messages)

    return channel_message_cache

