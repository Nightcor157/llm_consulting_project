import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot.handlers import router
from app.core.config import settings
from app.infra.redis import close_redis

logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is empty")
    return Bot(token=settings.telegram_bot_token)


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    return dispatcher


async def start_polling() -> None:
    bot = create_bot()
    dispatcher = create_dispatcher()
    try:
        await dispatcher.start_polling(bot)
    finally:
        await close_redis()
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_polling())
