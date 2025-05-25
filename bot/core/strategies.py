from abc import ABC, abstractmethod
from typing import Protocol

class INotificationStrategy(Protocol):
    async def send(self, user_id: int, message: str) -> None:
        ...

class TelegramNotificationStrategy:
    async def send(self, user_id: int, message: str) -> None:
        from aiogram import Bot
        from config import config
        bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        await bot.send_message(user_id, message)

class NotificationContext:
    def __init__(self, strategy: INotificationStrategy):
        self._strategy = strategy

    async def send(self, user_id: int, message: str) -> None:
        await self._strategy.send(user_id, message)