
channels_dict = {}


def get_channel(channel_id):
    if channel_id not in channels_dict:
        channels_dict[channel_id] = {}
    return channels_dict[channel_id]


async def channel_cache_message(bot, message):
    channel = message.channel.id
