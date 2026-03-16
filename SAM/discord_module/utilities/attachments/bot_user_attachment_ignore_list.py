import os
from utility_scripts.system_logging import setup_logger
from dotenv import load_dotenv
from types import SimpleNamespace

# configure logging
logger = setup_logger(__name__)


def ns(d: dict) -> SimpleNamespace:
    """Convert dict into a dot-accessible namespace (recursively)."""
    return SimpleNamespace(**{k: ns(v) if isinstance(v, dict) else v for k, v in d.items()})


# Load Env
load_dotenv()

config_dict = {
    "BOTS": {
        "FOOTNOTE": os.getenv("BOT_ID_FOOTNOTE"),
        "MYURI": os.getenv("BOT_ID_MYURI"),
        "DANNY": os.getenv("BOT_ID_DANNY")
    }
}
CONFIG = ns(config_dict)
bots_blacklist = [int(b) for b in CONFIG.BOTS.__dict__.values()]


def ignore_bot_attachment(user_id):
    if user_id in bots_blacklist:
        return True

    # bot not in blacklist
    return False

