import datetime

from typing import NamedTuple


class MimeType(NamedTuple):
    """Parsed MIME type.

    media_type: top-level type (e.g. 'text', 'image')
    media_subtype: subtype (e.g. 'plain', 'webp')
    params: MIME parameters (e.g. {'charset': 'utf-8'})
    """
    media_type: str
    media_subtype: str
    params: dict[str, str]


def parse_mime_type(mime: str) -> MimeType:
    """
    media_type:"text"
    media_subtype: "plain"
    params: {"charset": "utf-8"}
    """

    type_part, _, param_part = mime.partition(";")
    media_type, media_subtype = type_part.split("/", 1)

    params = {}
    if param_part:
        for item in param_part.split(";"):
            key, _, value = item.strip().partition("=")
            if key and value:
                params[key] = value

    return MimeType(media_type, media_subtype, params)


def split_response(response, max_len=2000):
    if len(response) < max_len:
        return [response]

    chunks = []
    while len(response) > max_len:
        # Find the last space or line break within the first max_len characters
        split_index = max(response.rfind(' ', 0, max_len), response.rfind('\n', 0, max_len))
        if split_index == -1:
            # If no space or newline is found, just split at max_len
            split_index = max_len
        chunks.append(response[:split_index].rstrip())
        response = response[split_index:].lstrip()
    if response:
        chunks.append(response)
    return chunks


# Get current date and time
def current_date_time():
    now = datetime.datetime.now()
    date = now.strftime("%B %d, %Y")
    time = now.strftime("%I:%M %p")

    return f"The current date is {date}. The current time is {time}."
