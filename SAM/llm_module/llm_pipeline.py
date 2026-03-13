import asyncio

from discord_module.discord_functions.discord_bot_users_manager import bot_message_cooldown
from discord_module.discord_functions.utility.download_discord_attachments import download_attachments
from llm_module.llm_generate import llm_generate_chat_response
from memory_module.process_message import process_message

from message_logs.log_message import log_message

from tools.determine_request import classify_request
from tools.text_to_speech.tts_message_helpers import message_is_tts, send_tts
from tools.weather_search.weather_tool import weather_search
from tools.web_search.internet_tool import llm_internet_search

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
        response = await _generate_response(bot, message, message_content)

    if not response:
        return

    # --------------------------------------------------------
    # 4. Send response to Discord
    # --------------------------------------------------------
    sent_message = await _send_response(
        bot=bot,
        message=message,
        response=response,
        is_tts_message=is_tts_message
    )

    # --------------------------------------------------------
    # 5. Post-processing (cache + logging)
    # --------------------------------------------------------
    await _post_process(
        bot=bot,
        message=message,
        response=response,
        sent_message=sent_message,
    )


# ============================================================
# RESPONSE GENERATION
# ============================================================

async def _generate_response(bot, message, message_content):
    """
    Determines which backend should handle the request
    and returns a standardized response object.
    """

    # ---------------------------------
    # Attachment detection
    # ---------------------------------
    request_type, *attachments = classify_request(message, message_content)

    if attachments:
        message_attachments = attachments[0]
    else:
        message_attachments = None

    logger.info(f"Classification={request_type}, Content={message_content}")

    # ---------------------------------
    # Route to correct backend
    # ---------------------------------
    match request_type:

        # ---------------------------------
        # attachments
        # ---------------------------------
        case "attachment":
            loop = asyncio.get_event_loop()
            gathered = await loop.run_in_executor(
                None,
                download_attachments,
                message_attachments
            )

            if not gathered:
                logger.error("Attachment download failed. Falling back to default chat.")
                return await llm_generate_chat_response(bot, message)

            # return await sam_message(message_attachments=gathered)

        # ---------------------------------
        # weather
        # ---------------------------------
        case "weather_search":
            logger.info("Weather search triggered")
            return await weather_search(message_content)

        # ---------------------------------
        # web search
        # ---------------------------------
        case "search":
            logger.info("Web search triggered")
            return await llm_internet_search(message_content)

        # ---------------------------------
        # default chat
        # ---------------------------------
        case _:
            return await llm_generate_chat_response(bot, message)


# ============================================================
# DISCORD RESPONSE SENDING
# ============================================================

async def _send_response(bot, message, response, is_tts_message):
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


# ============================================================
# POST PROCESSING
# ============================================================

async def _post_process(bot, message, response, sent_message):
    """
    Handles:
    - Assistant message caching
    - Logging metadata
    """

    # add users message to cache, then add assistant's response
    chat_history = response.get("history")

    user_message = await process_message(bot, message)
    bot_message = {'role': 'assistant', 'content': response.get("message").content}

    # appends to the cache as well
    chat_history.append(user_message)
    chat_history.append(bot_message)

    # Prepare log data
    user_message_log = {
        "id": message.id,
        "content": message.clean_content,
        "name": message.author.name
    }

    msg = response.get("message")
    thinking = getattr(msg, "thinking", "No Thinking")

    await log_message(
        sent_message,
        thinking,
        user_message_log,
        response.get("prompt"),
        chat_history
    )

