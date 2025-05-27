from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from interfaces.iconnection import IUserInterface
from interfaces.ioutlook import ICalendarService
from .handlers.base import BaseHandler


class TelegramBot(IUserInterface):
    def __init__(self, token: str, calendar_service: ICalendarService):
        self.bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher(storage=MemoryStorage())
        self.router = Router()
        self.calendar_service = calendar_service

        # Инициализация обработчиков
        self.handlers = BaseHandler(calendar_service)
        self.dp.include_router(self.handlers.router)

    async def start(self):
        await self.dp.start_polling(self.bot)

    async def send_message(self, chat_id: int, text: str, **kwargs):
        await self.bot.send_message(chat_id=chat_id, text=text, **kwargs)

    async def ask_question(self, chat_id: int, question: str, options: list[str] = None, **kwargs):
        from .keyboards import get_reply_keyboard
        if options:
            kwargs['reply_markup'] = get_reply_keyboard(options)
        await self.send_message(chat_id, question, **kwargs)