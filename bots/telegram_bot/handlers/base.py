from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from datetime import datetime, timedelta

from interfaces.ioutlook import ICalendarService
from ..keyboards import get_main_keyboard
from .meetings import MeetingHandlers


class BaseHandler:
    def __init__(self, calendar_service: ICalendarService):
        self.router = Router()
        self.calendar_service = calendar_service
        MeetingHandlers(self.router, calendar_service)
        self._register_base_handlers()

    def _register_base_handlers(self):
        @self.router.message(Command("start"))
        async def cmd_start(message: Message, state: FSMContext):
            await state.clear()  # Сбрасываем любое предыдущее состояние
            await message.answer(
                "📅 <b>Бот для управления встречами</b>\n"
                "Выберите действие:",
                reply_markup=get_main_keyboard()
            )
