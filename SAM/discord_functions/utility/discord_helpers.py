from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)


def get_message_attachments(message):
    message_attachments = None
    if message.attachments:
        logger.info("Message has attachments")
        message_attachments = []
        for media in message.attachments:
            content_type = str(media.content_type).lower()

            # Unhandled formats will give  (status code: 500) from the bot
            # currently only looks at one image if there are multiple
            message_attachments.append({
                "type": content_type,
                "filename": media.filename,
                "attachment_url": media.url
            })
    return message_attachments
