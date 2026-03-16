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

