from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    display_name: str
    locale: str = "en"
    theme: str = "system"


class UserRead(UserBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
