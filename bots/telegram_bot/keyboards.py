from aiogram.utils.keyboard import ReplyKeyboardBuilder
from datetime import datetime, timedelta


def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Мои встречи")
    builder.button(text="Создать встречу")
    builder.button(text="Удалить встречу")
    builder.button(text="Настройки уведомлений")
    builder.adjust(2, 2)
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )


def get_reply_keyboard(options: list[str]):
    builder = ReplyKeyboardBuilder()
    for option in options:
        builder.button(text=option)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_date_selection_keyboard():
    builder = ReplyKeyboardBuilder()
    today = datetime.now().date()

    builder.button(text="Сегодня")
    builder.button(text="Завтра")
    builder.button(text="Послезавтра")
    builder.button(text="Выбрать другую дату")
    builder.button(text="Отменить создание")

    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_time_selection_keyboard(time_type: str = "start"):
    builder = ReplyKeyboardBuilder()

    # Добавляем стандартные варианты времени
    times = ["09:00", "10:00", "11:00", "12:00",
             "13:00", "14:00", "15:00", "16:00",
             "17:00", "18:00", "Другое время"]

    for time in times:
        builder.button(text=time)

    builder.button(text="Отменить создание")
    builder.adjust(3, 3, 3, 2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_cancel_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Отменить создание")
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_meetings_keyboard(meetings: list):
    builder = ReplyKeyboardBuilder()
    for meeting in meetings:
        start_time = datetime.fromisoformat(meeting['start']['dateTime']).strftime('%d.%m %H:%M')
        builder.button(text=f"{meeting['subject']} ({start_time})")
    builder.button(text="Отменить удаление")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)