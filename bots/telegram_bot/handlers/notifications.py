from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import time
import logging

logger = logging.getLogger(__name__)


class NotificationSettingsState(StatesGroup):
    waiting_for_start_time = State()
    waiting_for_end_time = State()
    waiting_for_minutes = State()


def setup_notification_handlers(router: Router, notification_service):
    logger.info("Регистрация обработчиков уведомлений")

    @router.message(F.text == "Настройки уведомлений")
    async def notification_settings(message: Message):
        logger.info(f"Обработка нажатия кнопки уведомлений для {message.chat.id}")
        try:
            settings = notification_service.get_settings(message.chat.id)
            kb = ReplyKeyboardMarkup(keyboard=[
                ["Изменить время уведомлений"],
                ["Изменить рабочее время"],
                [f"Включить уведомления {'🔴' if settings.enabled else '🟢'}"],
                ["Назад"]
            ], resize_keyboard=True)

            await message.answer(
                f"Текущие настройки:\n"
                f"Уведомлять за: {settings.notify_before_minutes} мин.\n"
                f"Рабочее время: {settings.work_start_time.strftime('%H:%M')}-{settings.work_end_time.strftime('%H:%M')}\n"
                f"Статус: {'Вкл' if settings.enabled else 'Выкл'}",
                reply_markup=kb
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике уведомлений: {e}")
            await message.answer("Произошла ошибка при обработке запроса")

    @router.message(F.text == "Изменить время уведомлений")
    async def change_notification_time(message: Message, state: FSMContext):
        await state.set_state(NotificationSettingsState.waiting_for_minutes)
        await message.answer("За сколько минут до встречи уведомлять? (Введите число)")

    @router.message(NotificationSettingsState.waiting_for_minutes)
    async def process_notification_time(message: Message, state: FSMContext):
        try:
            minutes = int(message.text)
            if not 1 <= minutes <= 1440:
                raise ValueError
            notification_service.update_settings(
                message.chat.id,
                notify_before_minutes=minutes
            )
            await message.answer(f"Теперь уведомления будут приходить за {minutes} минут до встречи")
        except ValueError:
            await message.answer("Пожалуйста, введите число от 1 до 1440")
        await state.clear()

    @router.message(F.text == "Изменить рабочее время")
    async def change_work_time(message: Message, state: FSMContext):
        await state.set_state(NotificationSettingsState.waiting_for_start_time)
        await message.answer("Введите время начала рабочего дня в формате ЧЧ:ММ")

    @router.message(NotificationSettingsState.waiting_for_start_time)
    async def process_start_time(message: Message, state: FSMContext):
        try:
            start_time = time.fromisoformat(message.text)
            await state.update_data(start_time=start_time)
            await state.set_state(NotificationSettingsState.waiting_for_end_time)
            await message.answer("Введите время окончания рабочего дня в формате ЧЧ:ММ")
        except ValueError:
            await message.answer("Неверный формат времени. Используйте ЧЧ:ММ")

    @router.message(NotificationSettingsState.waiting_for_end_time)
    async def process_end_time(message: Message, state: FSMContext):
        try:
            end_time = time.fromisoformat(message.text)
            data = await state.get_data()
            notification_service.update_settings(
                message.chat.id,
                work_start_time=data['start_time'],
                work_end_time=end_time
            )
            await message.answer(
                f"Рабочее время обновлено: "
                f"{data['start_time'].strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
            )
        except ValueError:
            await message.answer("Неверный формат времени. Используйте ЧЧ:ММ")
        await state.clear()

    @router.message(F.text.startswith("Включить уведомления"))
    async def toggle_notifications(message: Message):
        settings = notification_service.get_settings(message.chat.id)
        new_status = not settings.enabled
        notification_service.update_settings(
            message.chat.id,
            enabled=new_status
        )
        await message.answer(f"Уведомления {'включены' if new_status else 'выключены'}")
