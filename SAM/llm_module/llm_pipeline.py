from discord_module.utilities.discord_bot_users_ratelimit import bot_message_cooldown
from llm_module.pipeline.pl_generate_response import generate_response
from llm_module.pipeline.pl_post_process import post_process
from llm_module.pipeline.pl_send_response import send_response


from llm_module.tools.text_to_speech.tts_message_helpers import message_is_tts

from utility_scripts.system_logging import setup_logger


logger = setup_logger(__name__)


# ============================================================
# PUBLIC ENTRY POINT
# ============================================================

async def llm_chat(bot, message):
    """
    Main orchestration layer for AI responses.

    Responsible for:
    - Preprocessing
    - Response generation
    - Sending output to Discord
    - Post-processing (cache + logging)
    """

    username = message.author.name

    # --------------------------------------------------------
    # 1. Prevent bot loops
    # --------------------------------------------------------
    if message.author.bot:
        result = bot_message_cooldown(username)
        if result == -1:
            return

    # --------------------------------------------------------
    # 2. TTS detection + clean content
    # --------------------------------------------------------
    is_tts_message, message_content = message_is_tts(message)

    # --------------------------------------------------------
    # 3. Generate AI response
    # --------------------------------------------------------
    async with message.channel.typing():
        response = await generate_response(bot, message, message_content)

    if not response:
        return

    # --------------------------------------------------------
    # 4. Send response to Discord
    # --------------------------------------------------------
    sent_message = await send_response(
        bot=bot,
        message=message,
        response=response,
        is_tts_message=is_tts_message
    )

    # --------------------------------------------------------
    # 5. Post-processing (cache + logging)
    # --------------------------------------------------------
    await post_process(
        bot=bot,
        message=message,
        response=response,
        sent_message=sent_message,
    )
