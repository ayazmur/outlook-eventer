from aiogram import Dispatcher
from bot.core.handlers import register_handlers

def get_dispatcher(bot) -> Dispatcher:
    dp = Dispatcher()
    register_handlers(dp)
    return dp