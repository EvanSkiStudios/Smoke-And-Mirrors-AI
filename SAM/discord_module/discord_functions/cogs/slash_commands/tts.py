import os
import random

import discord
from discord import app_commands
from discord.ext import commands

from llm_module.tools.text_to_speech.elevenlabs_voice import text_to_speech
from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)

# todo -- split message down by sentence by sentence, generate by sentence then stitch them back together


class TTS(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="tts", description="text to speech")
    @app_commands.describe(
        text="Text to speak",
        message_id="Message ID to read",
        voice="Choose a voice"
    )
    @app_commands.choices(voice=[
        app_commands.Choice(name="ISABEL", value="ISABEL"),
        app_commands.Choice(name="SAM", value="SAM"),
        app_commands.Choice(name="Gilbert", value="GILBERT"),
        app_commands.Choice(name="Colt 45", value="COLT"),
        app_commands.Choice(name="Hermaeus Mora", value="HERMA"),
    ])
    async def tts(
            self,
            interaction,
            text: str = None,
            message_id: str = None,
            voice: app_commands.Choice[str] = None
    ):
        logger.debug(f'Command issued: tts by {interaction.user}, MessageID: {message_id}, Text: {text}, voice: {voice}')
        await interaction.response.defer()

        # Require at least one
        if not text and not message_id:
            await interaction.followup.send("You must provide either text or a message ID.")
            return

        # If message_id is provided, fetch message
        if message_id:
            try:
                message = await interaction.channel.fetch_message(int(message_id))
                text = message.content
            except Exception as e:
                logger.error(f"Failed to fetch message: {e}")
                await interaction.followup.send("Invalid message ID or message not found.")
                return

        selected_voice = voice.value if voice else "default"

        tts_file = await text_to_speech(text, file_name=text, voice=selected_voice)
        if not tts_file:
            logger.error('TTS Error')

            # 🎲 Easter Egg: 1 in 100 chance to drop gag
            if random.randint(1, 100) == 45:
                # send YouTube video of spongebob clip of patrick "that was my last quarter"
                await interaction.followup.send('https://youtu.be/c4MAh9nCddc?t=5')
            else:
                await interaction.followup.send('Error making TTS. Probably out of cash.')
            return

        await interaction.followup.send(file=discord.File(tts_file))
        os.remove(tts_file)


async def setup(bot: commands.Bot):
    await bot.add_cog(TTS(bot))
