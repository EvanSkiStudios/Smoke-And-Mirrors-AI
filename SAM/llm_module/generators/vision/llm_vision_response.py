import asyncio

from ollama import chat

from discord_module.utilities.attachments.discord_attachments_manager import cleanup_image_file
from llm_module.generators.vision.vision_system_prompt import build_vision_system_prompt
from llm_module.llm_create import LLM_CONFIG
from llm_module.process_response import process_response
from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)

CONFIG = LLM_CONFIG.ISABEL


async def llm_generate_vision_response(bot, message, attachments=None):
    prompt_data = await build_vision_system_prompt(bot, message, attachments)

    full_prompt = prompt_data["full_prompt"]
    system_prompt = prompt_data["system_prompt"]
    message_cache = prompt_data["message_cache"]
    cached_user_message = prompt_data["cached_user_message"]

    response = await llm_vision_response(full_prompt)
    response_data = process_response(response, system_prompt, message_cache)

    response_data["user"] = cached_user_message
    response_data["file_txt"] = attachments["text"]

    return response_data


async def llm_vision_response(full_prompt):

    response = await asyncio.to_thread(
        chat,
        model=CONFIG.VISION_MODEL,
        messages=full_prompt,
        options={
            "num_ctx": CONFIG.DEFAULT_CONTEXT,
            "temperature": CONFIG.DEFAULT_TEMPERATURE,
            "think": True
        },
        stream=False
    )

    # clean up image
    user_prompt = full_prompt[-1]
    cleanup_image_file(user_prompt["images"])

    return response
