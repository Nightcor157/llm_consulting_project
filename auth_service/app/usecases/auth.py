from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.repositories.users import UsersRepository
from app.schemas.auth import RegisterRequest, TokenResponse


class AuthUseCase:
    def __init__(self, users_repo: UsersRepository, session: AsyncSession) -> None:
        self.users_repo = users_repo
        self.session = session

    async def register(self, data: RegisterRequest) -> User:
        email = data.email.lower().strip()
        existing_user = await self.users_repo.get_by_email(email)
        if existing_user is not None:
            raise UserAlreadyExistsError()

        try:
            user = await self.users_repo.create(
                email=email,
                password_hash=hash_password(data.password),
                role="user",
            )
            await self.session.commit()
            return user
        except IntegrityError as exc:
            await self.session.rollback()
            raise UserAlreadyExistsError() from exc

    async def login(self, *, email: str, password: str) -> TokenResponse:
        user = await self.users_repo.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        token = create_access_token(subject=user.id, role=user.role)
        return TokenResponse(access_token=token, token_type="bearer")

    async def me(self, user_id: int) -> User:
        user = await self.users_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        return user
