from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Мои встречи")
    builder.button(text="Создать встречу")
    builder.button(text="Удалить встречу")
    return builder.as_markup(resize_keyboard=True)

def get_reply_keyboard(options: list[str]):
    builder = ReplyKeyboardBuilder()
    for option in options:
        builder.button(text=option)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)