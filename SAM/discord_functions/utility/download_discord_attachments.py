import os
import requests

from pathlib import Path
from dotenv import load_dotenv

from utility_scripts.system_logging import setup_logger
from utility_scripts.utility import parse_mime_type

# configure logging
logger = setup_logger(__name__)

# Load Env
load_dotenv()

# headers for request
HEADERS = {
    "User-Agent": os.getenv("USER_AGENT"),
    "Accept-Language": "en-US,en;q=0.5"
}

# temp dir for attachments
parent_dir = Path(__file__).resolve().parent
temp_path = parent_dir / 'attachments_temp'
temp_path.mkdir(exist_ok=True)


def download_attachments(message_attachments: list) -> dict:
    if not message_attachments:
        return {}

    gathered_attachments = {}

    for attachment in message_attachments:
        file_name = attachment["filename"]
        media_type, media_subtype, params = parse_mime_type(attachment["type"])
        attach_url = attachment["attachment_url"]

        try:
            with requests.get(attach_url, headers=HEADERS, stream=True) as response:
                response.raise_for_status()

                # setup temp path for attachment
                file_path = temp_path / file_name

                with file_path.open("wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)

                attachment_data = {
                    "filepath": file_path,
                    "mediatype": media_type,
                    "mediasubtype": media_subtype,
                    "params": params
                }

                gathered_attachments[str(file_name)] = attachment_data

        except requests.RequestException as e:
            logger.error(f"{file_name} || Request failed: {e}")
            pass

    # END
    return gathered_attachments


async def digest_attachments(message_attachments):
    text_data = []
    image_data = []

    for filename, attachment in message_attachments.items():
        file_path = attachment["filepath"]
        media_type = attachment["mediatype"]
        media_subtype = attachment["mediasubtype"]
        params = attachment["params"]

        if media_type == "image" and media_subtype in ("png", "jpeg", "webp"):
            image_data.append(file_path)

        if media_type == "text":
            charset = params.get("charset", "utf-8")

            text_string = f"\n```{filename}\n"

            with file_path.open("r", encoding=charset, errors="replace") as f:
                content = f.read()

            text_string += (content + "\n```")
            text_data.append(text_string)

        # clean up
        os.remove(file_path)

    return text_data, image_data
