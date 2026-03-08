import re


def process_message(bot, message):
    author_name = message.author.name
    author_nick = message.author.display_name
    content = message.clean_content

    # remove (tts) tag
    if not message.author.bot and re.search(r"\(tts\)", content, re.IGNORECASE):
        content = re.sub(r"\(tts\)", "", content, flags=re.IGNORECASE)

    # Assistant (bot) message
    if message.author.id == bot.user.id:
