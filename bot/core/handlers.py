from aiogram import Router, F
from aiogram.types import Message
from bot.core.strategies import NotificationContext, TelegramNotificationStrategy
import logging
from aiogram.utils.keyboard import ReplyKeyboardBuilder

logger = logging.getLogger(__name__)
# Создаем роутер
router = Router()

@router.message(F.text == "/start")
async def start_cmd(message: Message):
    await message.answer("Привет! Я бот для уведомлений из Outlook.")

@router.message(F.text == "/notify")
async def notify_without_args(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="Создать встречу")
    await message.answer(
        "Пожалуйста, укажите название события:",
        reply_markup=builder.as_markup()
    )

@router.message(F.text.startswith("/notify"))
async def notify_cmd(message: Message):
    try:
        # Разбиваем текст на части и проверяем наличие аргумента
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Пожалуйста, укажите название события после команды:\n/notify Название события")
            return

        event_name = parts[1]
        notification = NotificationContext(TelegramNotificationStrategy())
        await notification.send(message.from_user.id, f"Напоминание: {event_name}")
        await message.answer(f"Уведомление для события '{event_name}' создано!")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")
        logger.error(f"Error in notify_cmd: {e}")
# Функция для регистрации всех обработчиков
def register_handlers(dp):
    dp.include_router(router)  # Подключаем роутер к диспетчеру