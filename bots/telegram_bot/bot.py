from datetime import datetime, timedelta
from typing import Dict

from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from interfaces.iconnection import IUserInterface
from interfaces.ioutlook import ICalendarService
from .handlers.base import BaseHandler
from redis.asyncio import Redis
from services.notification_service.notification_service import NotificationService
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .handlers.notifications import setup_notification_handlers


class TelegramBot(IUserInterface):
    def __init__(self, token: str, calendar_service: ICalendarService):
        redis = Redis.from_url("redis://localhost:6379/0")
        storage = MemoryStorage()
        self.notification_service = NotificationService()
        self.scheduler = AsyncIOScheduler()
        self._setup_notifications()
        self.bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher(storage=storage)
        self.router = Router()
        setup_notification_handlers(self.router, self.notification_service)
        self.calendar_service = calendar_service

        # Инициализация обработчиковB
        self.handlers = BaseHandler(calendar_service)
        self.dp.include_router(self.handlers.router)

    def _setup_notifications(self):
        # Проверка каждые 5 минут
        self.scheduler.add_job(
            self._check_upcoming_meetings,
            'interval',
            minutes=5,
            next_run_time=datetime.now()
        )
        self.scheduler.start()

    async def _check_upcoming_meetings(self):
        now = datetime.now()
        for chat_id, settings in self.notification_service.settings.items():
            if not settings.enabled:
                continue

            # Проверяем рабочее время
            current_time = now.time()
            if not (settings.work_start_time <= current_time <= settings.work_end_time):
                continue

            # Получаем предстоящие встречи
            end_time = now + timedelta(minutes=settings.notify_before_minutes)
            meetings = self.calendar_service.get_meetings(now, end_time)

            for meeting in meetings:
                await self._send_meeting_notification(chat_id, meeting)

    async def _send_meeting_notification(self, chat_id: int, meeting: Dict):
        start_time = datetime.fromisoformat(meeting['start']['dateTime'])
        message = (
            "🔔 Напоминание о встрече!\n\n"
            f"Тема: {meeting['subject']}\n"
            f"Время: {start_time.strftime('%H:%M')}\n"
            f"Место: {meeting.get('location', 'Не указано')}"
        )
        await self.send_message(chat_id, message)

    async def start(self):
        await self.dp.start_polling(self.bot)

    async def send_message(self, chat_id: int, text: str, **kwargs):
        await self.bot.send_message(chat_id=chat_id, text=text, **kwargs)

    async def ask_question(self, chat_id: int, question: str, options: list[str] = None, **kwargs):
        from .keyboards import get_reply_keyboard
        if options:
            kwargs['reply_markup'] = get_reply_keyboard(options)
        await self.send_message(chat_id, question, **kwargs)
