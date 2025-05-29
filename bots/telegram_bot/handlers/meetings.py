from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta

from ..keyboards import (get_main_keyboard, get_date_selection_keyboard,
                         get_time_selection_keyboard, get_cancel_keyboard,
                         get_meetings_keyboard)


class MeetingState(StatesGroup):
    subject = State()
    date = State()
    start_time = State()
    end_time = State()
    location = State()


class DeleteMeetingState(StatesGroup):
    meeting_selection = State()


class MeetingHandlers:
    def __init__(self, router: Router, calendar_service):
        self.router = router
        self.calendar = calendar_service
        self._register_handlers()

    def _register_handlers(self):
        # Обработчики создания встречи
        @self.router.message(F.text == "Создать встречу")
        async def create_meeting_start(message: Message, state: FSMContext):
            await state.set_state(MeetingState.subject)
            await message.answer(
                "Введите тему встречи:",
                reply_markup=get_cancel_keyboard()
            )

        @self.router.message(F.text == "Отменить создание")
        async def cancel_creation(message: Message, state: FSMContext):
            await state.clear()
            await message.answer(
                "Создание встречи отменено.",
                reply_markup=get_main_keyboard()
            )

        @self.router.message(MeetingState.subject)
        async def enter_subject(message: Message, state: FSMContext):
            if message.text == "Отменить создание":
                await cancel_creation(message, state)
                return

            await state.update_data(subject=message.text)
            await state.set_state(MeetingState.date)
            await message.answer(
                "Выберите дату встречи:",
                reply_markup=get_date_selection_keyboard()
            )

        @self.router.message(MeetingState.date)
        async def enter_date(message: Message, state: FSMContext):
            if message.text == "Отменить создание":
                await cancel_creation(message, state)
                return

            today = datetime.now().date()
            date_str = None

            if message.text == "Сегодня":
                date_str = today.strftime("%Y-%m-%d")
            elif message.text == "Завтра":
                date_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")
            elif message.text == "Послезавтра":
                date_str = (today + timedelta(days=2)).strftime("%Y-%m-%d")
            elif message.text == "Выбрать другую дату":
                await message.answer(
                    "Введите дату вручную в формате ГГГГ-ММ-ДД:",
                    reply_markup=get_cancel_keyboard()
                )
                return
            else:
                try:
                    datetime.strptime(message.text, "%Y-%m-%d")
                    date_str = message.text
                except ValueError:
                    await message.answer(
                        "Неверный формат даты. Введите в формате ГГГГ-ММ-ДД или выберите из предложенных вариантов.",
                        reply_markup=get_date_selection_keyboard()
                    )
                    return

            await state.update_data(date=date_str)
            await state.set_state(MeetingState.start_time)
            await message.answer(
                "Выберите время начала встречи:",
                reply_markup=get_time_selection_keyboard("start")
            )

        @self.router.message(MeetingState.start_time)
        async def enter_start_time(message: Message, state: FSMContext):
            if message.text == "Отменить создание":
                await cancel_creation(message, state)
                return

            if message.text == "Другое время":
                await message.answer(
                    "Введите время начала вручную в формате ЧЧ:ММ:",
                    reply_markup=get_cancel_keyboard()
                )
                return

            try:
                datetime.strptime(message.text, "%H:%M")
            except ValueError:
                await message.answer(
                    "Неверный формат времени. Выберите из предложенных вариантов или введите вручную в формате ЧЧ:ММ.",
                    reply_markup=get_time_selection_keyboard("start")
                )
                return

            await state.update_data(start_time=message.text)
            await state.set_state(MeetingState.end_time)
            await message.answer(
                "Выберите время окончания встречи:",
                reply_markup=get_time_selection_keyboard("end")
            )

        @self.router.message(MeetingState.end_time)
        async def enter_end_time(message: Message, state: FSMContext):
            if message.text == "Отменить создание":
                await cancel_creation(message, state)
                return

            if message.text == "Другое время":
                await message.answer(
                    "Введите время окончания вручную в формате ЧЧ:ММ:",
                    reply_markup=get_cancel_keyboard()
                )
                return

            try:
                datetime.strptime(message.text, "%H:%M")
            except ValueError:
                await message.answer(
                    "Неверный формат времени. Выберите из предложенных вариантов или введите вручную в формате ЧЧ:ММ.",
                    reply_markup=get_time_selection_keyboard("end")
                )
                return

            await state.update_data(end_time=message.text)
            await state.set_state(MeetingState.location)
            await message.answer(
                "Введите место встречи:",
                reply_markup=get_cancel_keyboard()
            )

        @self.router.message(MeetingState.location)
        async def enter_location(message: Message, state: FSMContext):
            if message.text == "Отменить создание":
                await cancel_creation(message, state)
                return

            data = await state.get_data()
            subject = data["subject"]
            date = data["date"]
            start_time = data["start_time"]
            end_time = data["end_time"]

            start = f"{date}T{start_time}:00"
            end = f"{date}T{end_time}:00"

            meeting = {
                "subject": subject,
                "start": {"dateTime": start},
                "end": {"dateTime": end},
                "location": message.text
            }

            self.calendar.create_meeting(meeting)
            await message.answer(
                "✅ Встреча успешно создана!",
                reply_markup=get_main_keyboard()
            )
            await state.clear()

        # Обработчики просмотра встреч
        @self.router.message(F.text == "Мои встречи")
        async def show_meetings(message: Message):
            now = datetime.utcnow()
            end = now + timedelta(days=7)
            meetings = self.calendar.get_meetings(start_date=now, end_date=end)

            if not meetings:
                await message.answer(
                    "📭 У вас нет запланированных встреч на ближайшую неделю.",
                    reply_markup=get_main_keyboard()
                )
                return

            response = "📅 Ваши встречи на ближайшую неделю:\n\n"
            for m in meetings:
                start_time = datetime.fromisoformat(m['start']['dateTime']).strftime('%d.%m.%Y %H:%M')
                end_time = datetime.fromisoformat(m['end']['dateTime']).strftime('%H:%M')
                subject = m['subject']
                location = m.get('location', 'Не указано')
                response += f"🔹 <b>{subject}</b>\n🕒 {start_time}–{end_time}\n📍 {location}\n\n"

            await message.answer(response, parse_mode="HTML", reply_markup=get_main_keyboard())

        # Обработчики удаления встреч
        @self.router.message(F.text == "Удалить встречу")
        async def delete_meeting_start(message: Message, state: FSMContext):
            now = datetime.utcnow()
            end = now + timedelta(days=30)  # Показываем встречи на ближайшие 30 дней
            meetings = self.calendar.get_meetings(start_date=now, end_date=end)

            if not meetings:
                await message.answer(
                    "У вас нет запланированных встреч для удаления.",
                    reply_markup=get_main_keyboard()
                )
                return

            await state.set_state(DeleteMeetingState.meeting_selection)
            await state.update_data(meetings=meetings)
            await message.answer(
                "Выберите встречу для удаления:",
                reply_markup=get_meetings_keyboard(meetings)
            )

        @self.router.message(F.text == "Отменить удаление")
        async def cancel_deletion(message: Message, state: FSMContext):
            await state.clear()
            await message.answer(
                "Удаление встречи отменено.",
                reply_markup=get_main_keyboard()
            )

        @self.router.message(DeleteMeetingState.meeting_selection)
        async def select_meeting_to_delete(message: Message, state: FSMContext):
            if message.text == "Отменить удаление":
                await cancel_deletion(message, state)
                return

            data = await state.get_data()
            meetings = data["meetings"]

            # Находим выбранную встречу
            selected_meeting = None
            for meeting in meetings:
                start_time = datetime.fromisoformat(meeting['start']['dateTime']).strftime('%d.%m %H:%M')
                if message.text.startswith(meeting['subject']) and message.text.endswith(f"({start_time})"):
                    selected_meeting = meeting
                    break

            if not selected_meeting:
                await message.answer(
                    "Не удалось найти выбранную встречу. Попробуйте еще раз.",
                    reply_markup=get_meetings_keyboard(meetings)
                )
                return

            # Удаляем встречу
            success = self.calendar.delete_meeting(selected_meeting['id'])
            if success:
                await message.answer(
                    "✅ Встреча успешно удалена!",
                    reply_markup=get_main_keyboard()
                )
            else:
                await message.answer(
                    "❌ Не удалось удалить встречу. Попробуйте еще раз.",
                    reply_markup=get_main_keyboard()
                )
            await state.clear()
