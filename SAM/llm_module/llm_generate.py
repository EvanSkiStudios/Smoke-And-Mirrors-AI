import asyncio
import copy

from discord_module.utilities.attachments.discord_attachments_manager import digest_attachments, cleanup_image_file
from discord_module.utilities.split_message import split_response
from llm_module.llm_create import LLM_CONFIG
from ollama import chat

from llm_module.system_prompts import personality_system_prompt, chat_history_system_prompt
from memory_module.message_history import get_channel_message_cache
from memory_module.process_message import process_message

from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)

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


async def build_system_prompt(bot, message, message_cache, file_data):

    system_prompt = {
        "role": "system", "content":
            personality_system_prompt + "\n" + chat_history_system_prompt
    }

    user_content = await process_message(bot, message)

    user_prompt = copy.deepcopy(user_content)
    formated_content = "(NEW MESSAGE TO RESPOND TO): " + user_prompt["content"]
    user_prompt["content"] = formated_content

    cached_user_message = copy.deepcopy(user_content)

    # File data
    text_data = file_data["text"]
    if text_data:
        user_prompt["content"] += text_data
        cached_user_message["content"] += text_data

    # Images
    image_data = file_data["image"]
    if image_data:
        user_prompt["images"] = image_data

    full_prompt = [
        system_prompt,
        *message_cache,
        user_prompt
    ]

    return full_prompt, system_prompt, message_cache, cached_user_message


# Main entry point
async def llm_generate_response(bot, message, attachments=None):
    message_cache = await get_channel_message_cache(bot, message)

    text_data, image_data = await sort_attachments(attachments)
    file_data = {
        "text": text_data,
        "image": image_data
    }

    full_prompt, system_prompt, message_cache, cached_user_message = await build_system_prompt(bot, message, message_cache, file_data)

    response = await llm_generate_chat_response(full_prompt, system_prompt, message_cache)

    response["user"] = cached_user_message
    response["file_txt"] = text_data

    return response


async def llm_generate_chat_response(full_prompt, system_prompt, message_cache):
    llm_model = CONFIG.MODEL_NAME

    user_prompt = full_prompt[-1]
    if isinstance(user_prompt, dict) and "images" in user_prompt:
        llm_model = CONFIG.VISION_MODEL

    response = await asyncio.to_thread(
        chat,
        model=llm_model,
        messages=full_prompt,
        options={
            "num_ctx": CONFIG.DEFAULT_CONTEXT,
            "temperature": CONFIG.DEFAULT_TEMPERATURE,
            "think": True
        },
        stream=False
    )

    cleaned = response.message.content.replace("'", "\\'")

    # clean up images
    if llm_model == CONFIG.VISION_MODEL:
        cleanup_image_file(user_prompt["images"])

    # Extract token usage from response
    token_usage = {
        "prompt_tokens": getattr(response, "prompt_eval_count", 0),
        "tokens_generated": getattr(response, "eval_count", 0),
        "total_tokens": getattr(response, "prompt_eval_count", 0) + getattr(response, "eval_count", 0),
        "model_load_time": getattr(response, "load_duration", 0),
        "prompt_processing_time": getattr(response, "prompt_eval_duration", 0),
        "generation_time": getattr(response, "eval_duration", 0),
        "total_duration": getattr(response, "total_duration", 0)
    }

    return {
        "content": split_response(cleaned),
        "message": response.message,
        "prompt": system_prompt,
        "history": message_cache,
        "token_usage": token_usage
    }
