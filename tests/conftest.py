import pytest
from unittest.mock import AsyncMock, MagicMock
from interfaces.ioutlook import ICalendarService
from interfaces.iconnection import IUserInterface

@pytest.fixture
def mock_calendar_service():
    service = MagicMock(spec=ICalendarService)
    service.get_meetings.return_value = []
    service.create_meeting.return_value = {"id": "test123"}
    return service

@pytest.fixture
def mock_user_interface():
    ui = MagicMock(spec=IUserInterface)
    ui.send_message = AsyncMock()
    ui.ask_question = AsyncMock()
    return ui