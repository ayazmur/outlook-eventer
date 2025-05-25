import pytest
from bot.core.strategies import NotificationContext, TelegramNotificationStrategy

class MockNotificationStrategy:
    async def send(self, user_id: int, message: str) -> None:
        self.last_user = user_id
        self.last_message = message

@pytest.mark.asyncio
async def test_notification_strategy():
    mock_strategy = MockNotificationStrategy()
    notifier = NotificationContext(mock_strategy)
    await notifier.send(123, "Test")
    assert mock_strategy.last_user == 123
    assert mock_strategy.last_message == "Test"