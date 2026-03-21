import os
from dotenv import load_dotenv

from utility_scripts.namespace_utility import namespace

load_dotenv()


config_dict = {
    "BOT": {
        "TOKEN": os.getenv("TOKEN"),
        "APPLICATION_ID": os.getenv("APPLICATION_ID"),
    },
    "SERVERS": {
        "GMCD_SERVER_ID": os.getenv("GMCD_SERVER_ID"),
        "GMCD_CHANNEL_ID": os.getenv("GMCD_CHANNEL_ID"),
        "TEST_SERVER_ID": os.getenv("TEST_SERVER_ID"),
        "DM_CHANNEL_ID": os.getenv("DM_CHANNEL_ID"),
    },
    "MASTER_USER_ID": os.getenv("MASTER_USER_ID"),
}

CONFIG = namespace(config_dict)


def get_config():
    return CONFIG
