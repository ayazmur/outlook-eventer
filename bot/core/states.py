from aiogram.fsm.state import State, StatesGroup

class ReminderStates(StatesGroup):
    waiting_for_event_name = State()
    waiting_for_event_time = State()
