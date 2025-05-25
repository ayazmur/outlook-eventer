import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from bot.core.dispatcher import get_dispatcher
from config import config


async def start_bot():
    bot = Bot(
        token=config.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = get_dispatcher(bot)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Bot stopped with error: {e}")
    finally:
        await bot.session.close()
        print("Bot session closed")


if __name__ == "__main__":
    asyncio.run(start_bot())