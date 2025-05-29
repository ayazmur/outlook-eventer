import pytest
from datetime import datetime, timedelta
from services.outlook_mock_service.outlook_mock import MockOutlookService


@pytest.fixture
def mock_service(tmp_path):
    data_file = tmp_path / "test_data.json"
    return MockOutlookService(data_file=str(data_file))


class TestMockOutlookService:
    def test_create_and_get_meeting(self, mock_service):
        now = datetime.now()
        meeting_data = {
            "subject": "Test Meeting",
            "start": {"dateTime": now.isoformat()},
            "end": {"dateTime": (now + timedelta(hours=1)).isoformat()}
        }

        created = mock_service.create_meeting(meeting_data)
        assert "id" in created

        fetched = mock_service.get_meeting(created["id"])
        assert fetched["subject"] == "Test Meeting"

    def test_get_meetings_in_range(self, mock_service):
        # Очищаем существующие встречи
        mock_service._load_data = lambda: {"meetings": [], "last_updated": datetime.now().isoformat()}

        now = datetime.now()
        meeting_data = {
            "subject": "Range Test",
            "start": {"dateTime": now.isoformat()},
            "end": {"dateTime": (now + timedelta(hours=1)).isoformat()}
        }
        mock_service.create_meeting(meeting_data)

        meetings = mock_service.get_meetings(now - timedelta(days=1), now + timedelta(days=1))
        assert len(meetings) == 1
        assert meetings[0]["subject"] == "Range Test"