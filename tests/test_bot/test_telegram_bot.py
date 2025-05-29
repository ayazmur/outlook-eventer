import pytest
from unittest.mock import AsyncMock, MagicMock
from bots.telegram_bot.bot import TelegramBot


@pytest.mark.asyncio
async def test_bot_initialization():
    bot = TelegramBot("test_token", MagicMock())
    assert hasattr(bot, "dp")
    assert hasattr(bot, "router")


@pytest.mark.asyncio
async def test_send_message():
    mock_calendar = MagicMock()
    bot = TelegramBot("test_token", mock_calendar)
    bot.bot = AsyncMock()

    await bot.send_message(123, "Test")
    bot.bot.send_message.assert_awaited_once()