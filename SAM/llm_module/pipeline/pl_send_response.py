from llm_module.tools.text_to_speech.tts_message_helpers import send_tts


async def send_response(bot, message, response, is_tts_message):
    """
    Handles sending multipart responses to Discord.
    """

    response_content = response["content"]

    sent_message = None

    for i, part in enumerate(response_content):

        # First message reply behavior
        if not message.author.bot and i == 0:
            sent_message = await message.reply(
                part,
                suppress_embeds=True,
                mention_author=False
            )
        else:
            if i == 0:
                sent_message = await message.channel.send(
                    part,
                    suppress_embeds=True,
                    mention_author=False
                )
            else:
                await message.channel.send(
                    part,
                    suppress_embeds=True
                )

    # TTS handling (first part only)
    if is_tts_message and response_content:
        await send_tts(
            message,
            response_content[0],
            reply_target=sent_message
        )

    return sent_message
