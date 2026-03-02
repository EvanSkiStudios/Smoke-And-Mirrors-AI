from discord_module.bot_factory import create_bot
from discord_module.config import get_config
from SAM import sam_create

sam_create()

bot = create_bot()
CONFIG = get_config()
bot.run(CONFIG.BOT.TOKEN)

