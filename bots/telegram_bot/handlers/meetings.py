from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from ..keyboards import get_main_keyboard


class MeetingCreationStates(StatesGroup):
    waiting_title = State()
    waiting_date = State()
    waiting_time = State()
    waiting_duration = State()


class MeetingHandlers:
    def __init__(self, router: Router, calendar_service):
        self.router = router
        self.calendar = calendar_service
        self._register_handlers()

    def _register_handlers(self):
        # Обработчик начала создания встречи
        @self.router.message(F.text == "Создать встречу")
        async def start_meeting_creation(message: Message, state: FSMContext):
            await message.answer(
                "Введите название встречи:",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.set_state(MeetingCreationStates.waiting_title)

        # Обработчик названия встречи
        @self.router.message(MeetingCreationStates.waiting_title)
        async def process_title(message: Message, state: FSMContext):
            await state.update_data(title=message.text)
            await message.answer("Введите дату встречи (формат: ДД.ММ.ГГГГ):")
            await state.set_state(MeetingCreationStates.waiting_date)

        # Обработчик даты встречи
        @self.router.message(MeetingCreationStates.waiting_date)
        async def process_date(message: Message, state: FSMContext):
            try:
                date = datetime.strptime(message.text, "%d.%m.%Y").date()
                await state.update_data(date=date)
                await message.answer("Введите время начала (формат: ЧЧ:ММ):")
                await state.set_state(MeetingCreationStates.waiting_time)
            except ValueError:
                await message.answer("❌ Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ:")

        # Обработчик времени встречи
        @self.router.message(MeetingCreationStates.waiting_time)
        async def process_time(message: Message, state: FSMContext):
            try:
                time = datetime.strptime(message.text, "%H:%M").time()
                data = await state.get_data()
                start_datetime = datetime.combine(data['date'], time)
                await state.update_data(start=start_datetime)
                await message.answer("Введите продолжительность встречи в минутах:")
                await state.set_state(MeetingCreationStates.waiting_duration)
            except ValueError:
                await message.answer("❌ Неверный формат времени. Введите время в формате ЧЧ:ММ:")

        # Обработчик продолжительности и сохранение встречи
        @self.router.message(MeetingCreationStates.waiting_duration)
        async def process_duration(message: Message, state: FSMContext):
            try:
                duration = int(message.text)
                data = await state.get_data()

                meeting_data = {
                    "subject": data['title'],
                    "start": {
                        "dateTime": data['start'].isoformat(),
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": (data['start'] + timedelta(minutes=duration)).isoformat(),
                        "timeZone": "UTC"
                    },
                    "location": "Online",
                    "attendees": []
                }

                created_meeting = self.calendar.create_meeting(meeting_data)

                await message.answer(
                    "✅ Встреча успешно создана!\n"
                    f"📌 Тема: {created_meeting['subject']}\n"
                    f"⏰ Время: {created_meeting['start']['dateTime']} - {created_meeting['end']['dateTime']}",
                    reply_markup=get_main_keyboard()
                )
                await state.clear()

            except ValueError:
                await message.answer("❌ Пожалуйста, введите число (продолжительность в минутах):")

        # Обработчик отмены
        @self.router.message(Command("cancel"))
        @self.router.message(F.text.casefold() == "отмена")
        async def cancel_creation(message: Message, state: FSMContext):
            current_state = await state.get_state()
            if current_state is None:
                return

            await state.clear()
            await message.answer(
                "❌ Создание встречи отменено",
                reply_markup=get_main_keyboard()
            )