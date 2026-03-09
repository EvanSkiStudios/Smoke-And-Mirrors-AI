import asyncio

from llm_module.llm_create import LLM_CONFIG
from ollama import chat

from llm_module.system_prompts import personality_system_prompt, chat_history_system_prompt
from memory_module.message_history import get_channel_message_cache
from memory_module.process_message import process_message
from utility_scripts.utility import split_response

CONFIG = LLM_CONFIG.SAM

# todo -- break this down into its own pipeline


async def llm_generate_chat_response(bot, message):
    message_cache = await get_channel_message_cache(bot, message)

    system_prompt = {"role": "system", "content": personality_system_prompt + "\n\n" + chat_history_system_prompt}

    full_prompt = [
        system_prompt,
        *message_cache,
        await process_message(bot, message)
    ]

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
