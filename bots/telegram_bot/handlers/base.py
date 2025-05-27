from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime, timedelta

from interfaces.ioutlook import ICalendarService
from ..keyboards import get_main_keyboard


class BaseHandler:
    def __init__(self, calendar_service: ICalendarService):
        self.router = Router()
        self.calendar_service = calendar_service
        self._register_handlers()

    def _register_handlers(self):
        @self.router.message(Command("start"))
        async def cmd_start(message: Message):
            await message.answer(
                "📅 <b>Бот для управления встречами</b>\n"
                "Выберите действие:",
                reply_markup=get_main_keyboard()
            )

        @self.router.message(F.text == "Мои встречи")
        async def show_meetings(message: Message):
            start_date = datetime.now()
            end_date = start_date + timedelta(days=7)
            meetings = self.calendar_service.get_meetings(start_date, end_date)

            if not meetings:
                await message.answer("У вас нет запланированных встреч на ближайшую неделю.")
                return

            text = ["<b>Ваши встречи:</b>"]
            for meeting in meetings:
                text.append(
                    f" {meeting['subject']}\n"
                    f" {meeting['start']['dateTime']} - {meeting['end']['dateTime']}\n"
                    f" {', '.join(meeting['attendees'])}"
                )

            await message.answer("\n\n".join(text))