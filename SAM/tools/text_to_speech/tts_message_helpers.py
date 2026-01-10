import os
import re
import discord

from tools.text_to_speech.elevenlabs_voice import text_to_speech
from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)


def message_is_tts(message):
    message_content = message.clean_content

    is_tts_message = False
    if not message.author.bot and re.search(r"\(tts\)", message_content, re.IGNORECASE):
        logger.debug('Message is a TTS Message')
        is_tts_message = True
        message_content = re.sub(r"\(tts\)", "", message_content, flags=re.IGNORECASE)

    return is_tts_message, message_content


async def send_tts(interaction_or_message, text, reply_target=None):
    text_filtered = re.sub(r"\*(.*?)\*", r"[\1]", text)
    tts_file = await text_to_speech(text_filtered)
    if not tts_file:
        logger.error('TTS Error')
        await (interaction_or_message.followup.send if hasattr(interaction_or_message, "followup")
               else interaction_or_message.channel.send)("Error making TTS.")
        return
    if reply_target:
        await reply_target.reply(file=discord.File(tts_file))
    else:
        if hasattr(interaction_or_message, "followup"):
            await interaction_or_message.followup.send(file=discord.File(tts_file))
        else:
            await interaction_or_message.channel.send(file=discord.File(tts_file))
    os.remove(tts_file)
