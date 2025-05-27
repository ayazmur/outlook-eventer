import os
from dotenv import load_dotenv
from interfaces.ioutlook import ICalendarService
from interfaces.iconnection import IUserInterface
from services.outlook_mock_service.outlook_mock import MockOutlookService
from bots.telegram_bot.bot import TelegramBot

load_dotenv()


class ServiceFactory:
    @staticmethod
    def create_calendar_service() -> ICalendarService:
        service_type = os.getenv('CALENDAR_SERVICE', 'mock')

        if service_type == 'mock':
            return MockOutlookService()

    @staticmethod
    async def create_user_interface(calendar_service: ICalendarService) -> IUserInterface:
        ui_type = os.getenv('USER_INTERFACE', 'telegram')

        if ui_type == 'telegram':
            token = os.getenv('TELEGRAM_BOT_TOKEN')
            if not token:
                raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env")
            return TelegramBot(token, calendar_service)
