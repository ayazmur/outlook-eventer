# test_handlers/test_meetings.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from bots.telegram_bot.handlers.meetings import MeetingHandlers


# @pytest.mark.asyncio
# async def test_meeting_creation_flow():
#     mock_calendar = MagicMock()
#     mock_calendar.create_meeting.return_value = {"id": "test123"}
#
#     router = MagicMock()
#     handler = MeetingHandlers(router, mock_calendar)
#
#     # Имитируем сообщения
#     message = AsyncMock()
#     message.text = "Test Meeting"
#     state = AsyncMock()
#
#     # Находим нужный обработчик
#     for handler_func in router.message.call_args_list:
#         if handler_func[0][0].__ne__ == "create_meeting_start":
#             await handler_func[0][0](message, state)
#             break
#
#     state.set_state.assert_called_once()