import pytest
import os
from unittest.mock import patch
from services.factory import ServiceFactory

@patch.dict(os.environ, {"CALENDAR_SERVICE": "mock"})
def test_create_mock_service():
    service = ServiceFactory.create_calendar_service()
    assert service.__class__.__name__ == "MockOutlookService"

@patch.dict(os.environ, {"CALENDAR_SERVICE": "invalid"})
def test_invalid_service_type():
    with pytest.raises(ValueError):
        ServiceFactory.create_calendar_service()