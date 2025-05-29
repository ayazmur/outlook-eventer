import pytest
from aiogram import types
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from bots.telegram_bot.handlers.meetings import MeetingHandlers, MeetingState


@pytest.mark.asyncio
async def test_meeting_creation_flow(mock_calendar_service):
    router = MagicMock()
    handler = MeetingHandlers(router, mock_calendar_service)

    # Имитируем сообщения пользователя
    message = AsyncMock(spec=types.Message)
    message.text = "Test Meeting"
    state = AsyncMock()

    # Шаг 1: Ввод темы
    await handler._register_handlers()["enter_subject"](message, state)
    state.update_data.assert_called_with(subject="Test Meeting")

    # Шаг 2: Ввод даты
    message.text = "2023-01-01"
    await handler._register_handlers()["enter_date"](message, state)
    state.update_data.assert_called_with(date="2023-01-01")