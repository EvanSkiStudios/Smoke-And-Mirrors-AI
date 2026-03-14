import asyncio
import copy

from discord_module.discord_functions.utility.download_discord_attachments import digest_attachments
from llm_module.llm_create import LLM_CONFIG
from ollama import chat

from llm_module.system_prompts import personality_system_prompt, chat_history_system_prompt
from memory_module.message_history import get_channel_message_cache
from memory_module.process_message import process_message
from utility_scripts.utility import split_response

CONFIG = LLM_CONFIG.SAM


async def sort_attachments(attachments):
    text_data = None
    text_data_string = None
    image_data = None
    if attachments:
        text_data, image_data = await digest_attachments(attachments)
    if text_data is not None:
        text_data_string = "".join(text_data)

    return text_data_string, image_data


async def build_system_prompt(bot, message, message_cache, text_data):
    system_prompt = {
        "role": "system", "content":
            # personality_system_prompt + "\n\n" + chat_history_system_prompt + text_data_prompt
            chat_history_system_prompt
    }

    user_content = await process_message(bot, message)

    user_prompt = copy.deepcopy(user_content)
    formated_content = "(NEW MESSAGE TO RESPOND TO)\n" + user_prompt["content"]
    user_prompt["content"] = formated_content

    if text_data:
        user_prompt["content"] += text_data

    full_prompt = [
        system_prompt,
        *message_cache,
        user_prompt
    ]

    return full_prompt, system_prompt, message_cache


# Main entry point
async def llm_generate_response(bot, message, attachments=None):
    message_cache = await get_channel_message_cache(bot, message)

    text_data, image_data = await sort_attachments(attachments)

    full_prompt, system_prompt, message_cache = await build_system_prompt(bot, message, message_cache, text_data)

    response = await llm_generate_chat_response(full_prompt, system_prompt, message_cache)
    return response


async def llm_generate_chat_response(full_prompt, system_prompt, message_cache):

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

    cleaned = response.message.content.replace("'", "\\'")

    return {
        "content": split_response(cleaned),
        "message": response.message,
        "prompt": system_prompt,
        "history": message_cache
    }
