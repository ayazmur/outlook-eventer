# test_bot/test_telegram_bot.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.utils.token import TokenValidationError
from bots.telegram_bot.bot import TelegramBot


@pytest.fixture
def valid_token():
    return "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"


@pytest.mark.asyncio
async def test_bot_initialization(valid_token):
    with patch('aiogram.Bot'), patch('aiogram.Dispatcher'):
        bot = TelegramBot(valid_token, MagicMock())
        assert hasattr(bot, "dp")
        assert hasattr(bot, "router")


@pytest.mark.asyncio
async def test_send_message(valid_token):
    mock_calendar = MagicMock()
    bot = TelegramBot(valid_token, mock_calendar)
    bot.bot = AsyncMock()

    await bot.send_message(123, "Test")
    bot.bot.send_message.assert_awaited_once_with(chat_id=123, text="Test")