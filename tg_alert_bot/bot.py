import os
import logging
from pathlib import Path
from typing import List

import yaml
from jinja2 import Template
from telegram import Bot
from telegram.error import TelegramError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

LOGGER = logging.getLogger(__name__)

class Alert:
    def __init__(self, cron: str, message: str):
        self.cron = cron
        self.message = message

    def render(self) -> str:
        # Jinja2 rendering – currently simple but allows variables later
        tmpl = Template(self.message)
        return tmpl.render()

class AlertBot:
    def __init__(self, token: str, chat_id: str, config_path: Path):
        self.bot = Bot(token=token)
        self.chat_id = int(chat_id)
        self.config_path = config_path
        self.scheduler = AsyncIOScheduler()
        self.alerts: List[Alert] = []

    def load_config(self) -> None:
        LOGGER.info("Loading config from %s", self.config_path)
        data = yaml.safe_load(self.config_path.read_text())
        for item in data.get("alerts", []):
            self.alerts.append(Alert(cron=item["cron"], message=item["message"]))

    def schedule_alerts(self) -> None:
        for alert in self.alerts:
            trigger = CronTrigger.from_crontab(alert.cron)
            self.scheduler.add_job(self.send_message, trigger, args=[alert])
            LOGGER.debug("Scheduled alert: %s -> %s", alert.cron, alert.message)
        self.scheduler.start()
        LOGGER.info("Scheduler started with %d alerts", len(self.alerts))

    async def send_message(self, alert: Alert) -> None:
        txt = alert.render()
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=txt)
            LOGGER.info("Sent alert: %s", txt)
        except TelegramError as exc:
            LOGGER.error("Failed to send alert: %s", exc)

    async def run(self) -> None:
        self.load_config()
        self.schedule_alerts()
        # Keep the event loop alive – APScheduler runs in background
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    import asyncio
    import sys

    logging.basicConfig(
        level=logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TARGET_CHAT_ID")
    if not token or not chat_id:
        sys.exit("TELEGRAM_BOT_TOKEN and TARGET_CHAT_ID must be set in environment")

    bot = AlertBot(token=token, chat_id=chat_id, config_path=Path(__file__).parent.parent / "config.yaml")
    asyncio.run(bot.run())
