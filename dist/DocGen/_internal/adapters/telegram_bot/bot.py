"""Telegram Bot Launcher and Dispatcher Setup."""

import os
import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from adapters.telegram_bot.handlers.start import router as start_router
from adapters.telegram_bot.handlers.wizard import router as wizard_router


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("DocGenBot")

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.warning(
            "TELEGRAM_BOT_TOKEN не задан в переменных окружения. "
            "Для запуска бота выполните: export TELEGRAM_BOT_TOKEN='ваш_токен'"
        )
        if len(sys.argv) > 1 and sys.argv[1] == "--check":
            print("Telegram Bot modules compiled and verified successfully.")
            return
        return

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(wizard_router)

    logger.info("Запуск Telegram-бота DocGen...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
