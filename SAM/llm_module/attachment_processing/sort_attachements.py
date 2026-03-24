from discord_module.utilities.attachments.discord_attachments_manager import digest_attachments


async def sort_attachments(attachments):
    text_data = None
    text_data_string = None
    image_data = None
    audio_data = None
    audio_data_string = None

    if attachments:
        attachment_data = await digest_attachments(attachments)

        text_data = attachment_data["text"]
        image_data = attachment_data["image"]
        audio_data = attachment_data["audio"]

    if text_data is not None:
        text_data_string = "".join(text_data)

    if audio_data is not None:
        audio_data_string = "".join(audio_data)

    return {
        "text": text_data_string,
        "image": image_data,
        "audio": audio_data_string
    }

