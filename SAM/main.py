from discord_module.bot_factory import create_bot
from discord_module.config import get_config
from discord_module.bot_instance import set_bot
from llm_module.llm_create import llm_create

llm_create()

bot = create_bot()
set_bot(bot)
CONFIG = get_config()
bot.run(CONFIG.BOT.TOKEN)

