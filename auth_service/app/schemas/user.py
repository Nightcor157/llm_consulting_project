from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
