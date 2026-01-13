import asyncio
import os
import sys

from dotenv import load_dotenv
from ollama import Client, chat

from discord_functions.utility.download_discord_attachments import digest_attachments
from sam_config import SAM_personality, chat_history_system_prompt
from discord_functions.discord_message_cache import session_chat_cache
from utility_scripts.system_logging import setup_logger
from utility_scripts.utility import split_response


# configure logging
logger = setup_logger(__name__)

load_dotenv()
os.environ["OLLAMA_API_KEY"] = os.getenv("OLLAMA_API")

# model settings for easy swapping
sam_model_name = 'SAM-deepseek-r1'
sam_ollama_model = 'huihui_ai/deepseek-r1-abliterated'
sam_vision_model = 'gemma3'


def sam_create():
    try:
        client = Client()
        response = client.create(
            model=sam_model_name,
            from_=sam_ollama_model,
            system=SAM_personality,
            stream=False,
        )
        # print(f"# Client: {response.status}")
        logger.info(f"# Client: {response.status}")
        return

    except ConnectionError as e:
        logger.error('Ollama is not running!')
        sys.exit(1)  # Exit program with error code 1

    except Exception as e:
        # Catches any other unexpected errors
        logger.error("❌ An unexpected error occurred:", e)
        sys.exit(1)


# === Main Entry Point ===
async def sam_message(message_author_name=None, message_author_nickname=None, message_content=None, image_file=None,
                      message_attachments=None) -> dict[str, any]:
    """
    :return: dict [
    message content: string,
    message object ]
    """

    text_data = None
    image_data = None
    if message_attachments:
        text_data, image_data = await digest_attachments(message_attachments)

    if text_data is not None:
        text_data_string = "".join(text_data)
        llm_response, full_prompt = await sam_converse_files(text_data=text_data_string)
    else:
        llm_response, full_prompt = await sam_converse()

    cleaned = llm_response.content.replace("'", "\\'")
    return {
        "content": split_response(cleaned),
        "message": llm_response,
        "prompt": full_prompt
    }


async def sam_converse():
    current_session_chat_cache = session_chat_cache()
    chat_log = list(current_session_chat_cache)

    # Keep assistant vs user turns distinct (LLMs are trained on role-tagged conversations)
    def build_role_message(entry: str):
        role = "user"
        if entry.startswith("SAM:"):
            role = "assistant"
            entry = entry.replace("SAM: ", "")
        return {"role": role, "content": entry}

    system_prompt = {"role": "system", "content": SAM_personality + "\n\n" + chat_history_system_prompt}

    full_prompt = [
        system_prompt,
        *[build_role_message(entry) for entry in chat_log]  # Store an array of role-tagged turns
    ]

    response = await asyncio.to_thread(
        chat,
        model=sam_model_name,
        messages=full_prompt,
        options={
            'num_ctx': 16384,
            'temperature': 0.5,
            'think': True
        },
        stream=False
    )

    # return response
    return response.message, system_prompt


async def sam_converse_files(text_data=None, image_data=None):
    current_session_chat_cache = session_chat_cache()
    chat_log = list(current_session_chat_cache)

    def build_role_message(entry: str):
        role = "user"
        if entry.startswith("SAM:"):
            role = "assistant"
            entry = entry.replace("SAM: ", "")
        return {"role": role, "content": entry}

    text_data_prompt = ""
    if text_data is not None:
        text_data_prompt = "\n\nThe user has provided the following file context/s to help form a response to their message:\n" + text_data

    system_prompt = {"role": "system", "content": SAM_personality + "\n\n" + chat_history_system_prompt + text_data_prompt}

    full_prompt = [
        system_prompt,
        *[build_role_message(entry) for entry in chat_log]  # Store an array of role-tagged turns
    ]

    response = await asyncio.to_thread(
        chat,
        model=sam_model_name,
        messages=full_prompt,
        options={
            'num_ctx': 16384,
            'temperature': 1,
            'think': True
        },
        stream=False
    )

    # return response
    return response.message, system_prompt
