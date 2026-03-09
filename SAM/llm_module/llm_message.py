from typing import Any

from discord_functions.utility.download_discord_attachments import digest_attachments
from llm_module.llm_generate import run_model
from llm_module.system_prompts import personality_system_prompt, chat_history_system_prompt
from memory_module.message_history import get_channel_message_cache
from utility_scripts.utility import split_response


async def build_prompt(file_text: str | None = None):

    file_context = ""

    if file_text:
        file_context = (
            "\n\nThe user has provided the following file context "
            "to help form a response:\n" + file_text
        )

    system_prompt = {
        "role": "system",
        "content": (
            personality_system_prompt
            + "\n\n"
            + chat_history_system_prompt
            + file_context
        )
    }

    message_cache = await get_channel_message_cache(bot, message)

    messages = [
        system_prompt,
        *gather_chat_history() # {"role": role, "content": entry}
    ]

    return messages, system_prompt


async def sam_message(message_attachments=None) -> dict[str, Any]:

    text_data = None
    image_data = None

    if message_attachments:
        text_data, image_data = await digest_attachments(message_attachments)

    file_context = "".join(text_data) if text_data else None

    messages, system_prompt = build_prompt(file_context)

    llm_message = await run_model(messages, file_context)

    cleaned = llm_message.content.replace("'", "\\'")

    return {
        "content": split_response(cleaned),
        "message": llm_message,
        "prompt": system_prompt
    }