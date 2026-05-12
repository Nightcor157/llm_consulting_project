from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from app.core.jwt import TokenExpiredValidationError, TokenValidationError, decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()
TOKEN_KEY_TEMPLATE = "token:{telegram_user_id}"


def token_key(telegram_user_id: int) -> str:
    return TOKEN_KEY_TEMPLATE.format(telegram_user_id=telegram_user_id)


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        "Здравствуйте! Сначала получите JWT в Auth Service, затем отправьте /token <jwt>."
    )


@router.message(Command("token"))
async def token_handler(message: Message, command: CommandObject) -> None:
    if message.from_user is None:
        await message.answer("Не удалось определить Telegram user_id.")
        return

    token = (command.args or "").strip()
    if not token:
        await message.answer("Передайте токен командой: /token <jwt>")
        return

    try:
        decode_and_validate(token)
    except TokenExpiredValidationError:
        await message.answer("Токен истёк. Получите новый токен в Auth Service.")
        return
    except TokenValidationError:
        await message.answer("Токен невалиден. Получите JWT в Auth Service.")
        return

    redis = get_redis()
    await redis.set(token_key(message.from_user.id), token)
    await message.answer("Токен принят и сохранён. Теперь можно отправлять вопросы.")


@router.message(F.text)
async def text_handler(message: Message) -> None:
    if message.from_user is None:
        await message.answer("Не удалось определить Telegram user_id.")
        return

    redis = get_redis()
    key = token_key(message.from_user.id)
    token = await redis.get(key)
    if not token:
        await message.answer(
            "Нет сохранённого токена. Получите JWT в Auth Service и отправьте /token <jwt>."
        )
        return

    try:
        decode_and_validate(token)
    except TokenExpiredValidationError:
        await redis.delete(key)
        await message.answer("Сохранённый токен истёк. Получите новый JWT в Auth Service.")
        return
    except TokenValidationError:
        await redis.delete(key)
        await message.answer("Сохранённый токен невалиден. Отправьте новый JWT командой /token <jwt>.")
        return

    prompt = message.text or ""
    llm_request.delay(message.chat.id, prompt)
    await message.answer("Запрос принят в обработку. Ответ придёт отдельным сообщением.")
