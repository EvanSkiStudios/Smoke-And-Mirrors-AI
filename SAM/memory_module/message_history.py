
channels_dict = {}


# creates/gets the section in the dict for the channel
def get_channel(channel_id):
    if channel_id not in channels_dict:
        channels_dict[channel_id] = {}
    return channels_dict[channel_id]


async def channel_cache_message(bot, message):
    channel = bot.get_channel(message.channel.id)
    channel_message_cache = get_channel(channel)

    if len(channel_message_cache) == 0:
        # gather last 20 in channel
        await gather_past_messages(channel)
        pass


