from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileRead(BaseModel):
    id: str
    role: str
    storage_key: str
    original_name: str
    mime_type: str | None
    size_bytes: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
