import asyncio

from discord_module.utilities.attachments.discord_attachments_manager import download_attachments, get_message_attachments
from llm_module.attachment_processing.sort_attachements import sort_attachments
from llm_module.determine_request import classify_request
from llm_module.generators.chat.llm_chat_response import llm_generate_response
from llm_module.generators.vision.llm_vision_response import llm_generate_vision_response
from utility_scripts.system_logging import setup_logger

logger = setup_logger(__name__)


async def generate_response(bot, message, message_content):
    """
    Determines which backend should handle the request
    and returns a standardized response object.
    """

    # ---------------------------------
    # Attachment detection
    # ---------------------------------
    message_attachments = get_message_attachments(message)
    attachment_data = None

    if message_attachments:
        loop = asyncio.get_event_loop()
        gathered_attachments = await loop.run_in_executor(
            None,
            download_attachments,
            message_attachments
        )

        attachment_data = await sort_attachments(gathered_attachments)

    request_type = classify_request(message, message_content, attachment_data)
    logger.info(f"Classification={request_type}, Content={message_content}")

    # ---------------------------------
    # Route to correct backend
    # ---------------------------------
    match request_type:

        # todo - all of the tools are old and outdated and need rewritten
        # Right now we just skip the tool call and do basic chat instead

        # ---------------------------------
        # Image
        # ---------------------------------
        case "image":
            logger.info("Vision Triggered")
            return await llm_generate_vision_response(bot, message, attachment_data)

        # ---------------------------------
        # web search
        # ---------------------------------
        case "search":
            logger.info("Web search triggered")
            # return await llm_internet_search(bot, message)
            return await llm_generate_response(bot, message, attachment_data)

        # ---------------------------------
        # weather
        # ---------------------------------
        case "weather_search":
            logger.info("Weather search triggered")
            # return await weather_search(message_content)
            return await llm_generate_response(bot, message, attachment_data)

        # ---------------------------------
        # default chat
        # ---------------------------------
        case _:
            return await llm_generate_response(bot, message, attachment_data)

