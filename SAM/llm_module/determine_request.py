from discord_module.utilities.attachments.discord_attachments_manager import get_message_attachments
from llm_module.tools.web_search.search_determinator.internet_search_determinator import is_search_request


def classify_request(message, text: str, attachments) -> str:
    text_file = None
    image_file = None
    audio_file = None

    if attachments:
        text_file = attachments["text"]
        image_file = attachments["image"]
        audio_file = attachments["audio"]

    if image_file:
        return "image"

    if is_search_request(text):
        return "search"

    # if is_weather_request(text):
    #    return ("weather_search",)

    # if none then just normal conversation
    return "conversation"
