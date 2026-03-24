import asyncio

from ollama import chat

from llm_module.generators.chat.chat_system_prompt import build_system_prompt
from llm_module.llm_create import LLM_CONFIG
from llm_module.process_response import process_response
from memory_module.message_history import get_channel_message_cache

from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)

CONFIG = LLM_CONFIG.SAM


# Main entry point
async def llm_generate_response(bot, message, attachments=None):
    message_cache = await get_channel_message_cache(bot, message)

    prompt_info = {
        "message_cache": message_cache,
        "attachment_data": attachments,
    }

    prompt_data = await build_system_prompt(bot, message, prompt_info)

    full_prompt = prompt_data["full_prompt"]
    system_prompt = prompt_data["system_prompt"]
    message_cache = prompt_data["message_cache"]
    cached_user_message = prompt_data["cached_user_message"]

    response = await llm_generate_chat_response(full_prompt)
    response_data = process_response(response, system_prompt, message_cache)
    response_data["user"] = cached_user_message

    if attachments:
        response_data["file_txt"] = attachments["text"]

    return response_data


async def llm_generate_chat_response(full_prompt):

    response = await asyncio.to_thread(
        chat,
        model=CONFIG.MODEL_NAME,
        messages=full_prompt,
        options={
            "num_ctx": CONFIG.DEFAULT_CONTEXT,
            "temperature": CONFIG.DEFAULT_TEMPERATURE,
            "think": True
        },
        stream=False
    )

    return response
