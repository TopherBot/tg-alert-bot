from .bot import AlertBot
import asyncio
import os
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

async def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TARGET_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN and TARGET_CHAT_ID must be set")
    bot = AlertBot(token=token, chat_id=chat_id, config_path=Path(__file__).parent.parent / "config.yaml")
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
