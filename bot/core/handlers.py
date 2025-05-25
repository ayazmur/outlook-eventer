from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from datetime import datetime, timedelta

from bot.core.strategies import NotificationContext, TelegramNotificationStrategy

import logging

logger = logging.getLogger(__name__)
router = Router()


# FSM состояния
class ReminderStates(StatesGroup):
    waiting_for_event_name = State()
    choosing_date = State()
    choosing_hour = State()
    choosing_minute = State()


# /start
@router.message(Command("start"))
async def start_cmd(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать напоминание", callback_data="start_create_reminder")]
    ])
    await message.answer("Привет! Я бот для уведомлений из Outlook.\n\nНажми кнопку ниже, чтобы создать напоминание.", reply_markup=kb)


# Нажатие "Создать напоминание"
@router.callback_query(F.data == "start_create_reminder")
async def start_reminder(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите название события:")
    await state.set_state(ReminderStates.waiting_for_event_name)


# Ввод названия
@router.message(ReminderStates.waiting_for_event_name)
async def process_event_name(message: Message, state: FSMContext):
    event_name = message.text.strip()
    if not event_name:
        await message.answer("Название события не может быть пустым. Введите снова:")
        return

    await state.update_data(event_name=event_name)

    # Предложение выбрать дату
    kb = InlineKeyboardBuilder()
    today = datetime.now().date()
    options = [
        ("Сегодня", today),
        ("Завтра", today + timedelta(days=1)),
        ("Послезавтра", today + timedelta(days=2)),
    ]
    for label, date in options:
        kb.button(text=label, callback_data=f"date:{date.isoformat()}")
    await message.answer("Выберите дату:", reply_markup=kb.as_markup())
    await state.set_state(ReminderStates.choosing_date)


# Выбор даты
@router.callback_query(F.data.startswith("date:"))
async def process_date(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split(":")[1]
    await state.update_data(date=date_str)

    # Кнопки выбора часов
    kb = InlineKeyboardBuilder()
    for hour in range(8, 21):  # например, с 8 до 20
        kb.button(text=f"{hour:02d}:00", callback_data=f"hour:{hour}")
    kb.adjust(4)
    await callback.message.edit_text("Выберите час:", reply_markup=kb.as_markup())
    await state.set_state(ReminderStates.choosing_hour)


# Выбор часа
@router.callback_query(F.data.startswith("hour:"))
async def process_hour(callback: CallbackQuery, state: FSMContext):
    hour = int(callback.data.split(":")[1])
    await state.update_data(hour=hour)

    # Минуты: 00, 15, 30, 45
    kb = InlineKeyboardBuilder()
    for minute in [0, 15, 30, 45]:
        kb.button(text=f"{minute:02d} мин", callback_data=f"minute:{minute}")
    kb.adjust(2)
    await callback.message.edit_text("Выберите минуты:", reply_markup=kb.as_markup())
    await state.set_state(ReminderStates.choosing_minute)


# Выбор минут + подтверждение
@router.callback_query(F.data.startswith("minute:"))
async def process_minute(callback: CallbackQuery, state: FSMContext):
    minute = int(callback.data.split(":")[1])
    user_data = await state.get_data()

    # Сбор всех данных
    event_name = user_data["event_name"]
    date_str = user_data["date"]
    hour = user_data["hour"]

    # Финальная дата-время
    event_dt = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=hour, minute=minute)
    readable_time = event_dt.strftime("%d.%m.%Y %H:%M")

    # Отправка уведомления
    try:
        notification = NotificationContext(TelegramNotificationStrategy())
        await notification.send(
            callback.from_user.id,
            f"✅ Напоминание:\n<b>{event_name}</b>\n🕒 {readable_time}"
        )
        await callback.message.edit_text(f"Готово! Напоминание '<b>{event_name}</b>' на {readable_time} создано ✅")
    except Exception as e:
        logger.error(f"Ошибка при создании уведомления: {e}")
        await callback.message.edit_text("Произошла ошибка при создании напоминания.")
    finally:
        await state.clear()


# Регистрация
def register_handlers(dp):
    dp.include_router(router)
