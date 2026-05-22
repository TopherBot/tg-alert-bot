import os
from pathlib import Path
import pytest
from tg_alert_bot.bot import Alert, AlertBot

@pytest.fixture
def dummy_config(tmp_path: Path):
    content = """
alerts:
  - cron: "0 0 * * *"
    message: "Test message"
"""
    cfg = tmp_path / "config.yaml"
    cfg.write_text(content)
    return cfg

def test_alert_render():
    a = Alert(cron="* * * * *", message="Hello {{ name }}")
    # No variables used – render returns unchanged string
    assert a.render() == "Hello {{ name }}"

@pytest.mark.asyncio
async def test_bot_loads_config(dummy_config: Path, monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")
    monkeypatch.setenv("TARGET_CHAT_ID", "12345")
    bot = AlertBot(token="fake-token", chat_id="12345", config_path=dummy_config)
    bot.load_config()
    assert len(bot.alerts) == 1
    assert bot.alerts[0].cron == "0 0 * * *"
    assert bot.alerts[0].message == "Test message"
