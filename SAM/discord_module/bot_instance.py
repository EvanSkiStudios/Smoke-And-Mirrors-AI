# discord_module/bot_instance.py
_bot_instance = None


def get_bot():
    """Get the global Discord bot instance."""
    return _bot_instance


def set_bot(bot):
    """Set the global Discord bot instance."""
    global _bot_instance
    _bot_instance = bot
