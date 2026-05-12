from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UsersRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        normalized_email = email.lower().strip()
        result = await self.session.execute(select(User).where(User.email == normalized_email))
        return result.scalar_one_or_none()

    async def create(self, *, email: str, password_hash: str, role: str = "user") -> User:
        user = User(email=email.lower().strip(), password_hash=password_hash, role=role)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
