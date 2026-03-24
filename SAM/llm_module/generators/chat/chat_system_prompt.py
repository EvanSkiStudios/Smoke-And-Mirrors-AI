import copy
import re

from llm_module.system_prompts import personality_system_prompt, chat_history_system_prompt
from memory_module.process_message import process_message

from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)


async def build_system_prompt(bot, message, prompt_data):
    message_cache = prompt_data["message_cache"]
    file_data = prompt_data["attachment_data"]

    if file_data is None:
        file_data = {"text": None, "audio": None}

    system_prompt = {
        "role": "system", "content":
            personality_system_prompt + "\n" + chat_history_system_prompt
    }

    user_content = await process_message(bot, message)
    user_prompt = copy.deepcopy(user_content)

    # todo -- move this over to attachment processing in pipeline to have it change the request based on the audio
    # replace content with audio content
    audio_data = file_data["audio"]
    if audio_data:
        if user_prompt["content"] == "" or re.search(r"\bisabel\b", user_prompt["content"], re.IGNORECASE):
            user_prompt["content"] = audio_data

    # format message as described in chat history prompt
    formated_content = "(NEW MESSAGE TO RESPOND TO): " + user_prompt["content"]
    user_prompt["content"] = formated_content
    cached_user_message = copy.deepcopy(user_content)

    # edit cached message if we edited the content above
    if audio_data:
        cached_user_message["content"] = audio_data

    # File data
    text_data = file_data["text"]
    if text_data:
        user_prompt["content"] += text_data
        cached_user_message["content"] += text_data

    full_prompt = [
        system_prompt,
        *message_cache,
        user_prompt
    ]

    return {
        "full_prompt": full_prompt,
        "system_prompt": system_prompt,
        "message_cache": message_cache,
        "cached_user_message": cached_user_message
    }
