from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta

from ..keyboards import get_main_keyboard


class MeetingState(StatesGroup):
    subject = State()
    date = State()
    start_time = State()
    end_time = State()
    location = State()


class MeetingHandlers:
    def __init__(self, router: Router, calendar_service):
        self.router = router
        self.calendar = calendar_service
        self._register_handlers()

    def _register_handlers(self):
        @self.router.message(F.text == "Создать встречу")
        async def create_meeting_start(message: Message, state: FSMContext):
            await state.set_state(MeetingState.subject)
            await message.answer("Введите тему встречи:")

        @self.router.message(MeetingState.subject)
        async def enter_subject(message: Message, state: FSMContext):
            await state.update_data(subject=message.text)
            await state.set_state(MeetingState.date)
            await message.answer("Введите дату встречи в формате ГГГГ-ММ-ДД:")

        @self.router.message(MeetingState.date)
        async def enter_date(message: Message, state: FSMContext):
            try:
                datetime.strptime(message.text, "%Y-%m-%d")
            except ValueError:
                await message.answer("Неверный формат даты. Введите в формате ГГГГ-ММ-ДД.")
                return
            await state.update_data(date=message.text)
            await state.set_state(MeetingState.start_time)
            await message.answer("Введите время начала встречи в формате ЧЧ:ММ (24ч):")

        @self.router.message(MeetingState.start_time)
        async def enter_start_time(message: Message, state: FSMContext):
            try:
                datetime.strptime(message.text, "%H:%M")
            except ValueError:
                await message.answer("Неверный формат времени. Введите в формате ЧЧ:ММ.")
                return
            await state.update_data(start_time=message.text)
            await state.set_state(MeetingState.end_time)
            await message.answer("Введите время окончания встречи в формате ЧЧ:ММ (24ч):")

        @self.router.message(MeetingState.end_time)
        async def enter_end_time(message: Message, state: FSMContext):
            try:
                datetime.strptime(message.text, "%H:%M")
            except ValueError:
                await message.answer("Неверный формат времени. Введите в формате ЧЧ:ММ.")
                return
            await state.update_data(end_time=message.text)
            await state.set_state(MeetingState.location)
            await message.answer("Введите место встречи:")

        @self.router.message(MeetingState.location)
        async def enter_location(message: Message, state: FSMContext):
            data = await state.get_data()
            subject = data["subject"]
            date = data["date"]
            start_time = data["start_time"]
            end_time = message.text

            start = f"{date}T{start_time}:00"
            end = f"{date}T{data['end_time']}:00"

            meeting = {
                "subject": subject,
                "start": {"dateTime": start},
                "end": {"dateTime": end},
                "location": message.text
            }

            self.calendar.create_meeting(meeting)
            await message.answer("✅ Встреча успешно создана!", reply_markup=get_main_keyboard())
            await state.clear()

        @self.router.message(F.text == "Мои встречи")
        async def show_meetings(message: Message):
            now = datetime.utcnow()
            end = now + timedelta(days=7)
            meetings = self.calendar.get_meetings(start_date=now, end_date=end)

            if not meetings:
                await message.answer("📭 У вас нет запланированных встреч на ближайшую неделю.", reply_markup=get_main_keyboard())
                return

            response = "📅 Ваши встречи на ближайшую неделю:\n\n"
            for m in meetings:
                start_time = datetime.fromisoformat(m['start']['dateTime']).strftime('%d.%m.%Y %H:%M')
                end_time = datetime.fromisoformat(m['end']['dateTime']).strftime('%H:%M')
                subject = m['subject']
                location = m.get('location', 'Не указано')
                response += f"🔹 <b>{subject}</b>\n🕒 {start_time}–{end_time}\n📍 {location}\n\n"

            await message.answer(response, parse_mode="HTML", reply_markup=get_main_keyboard())
