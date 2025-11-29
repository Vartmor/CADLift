from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings

settings = get_settings()


class StorageService:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _target_path(self, *parts: str) -> Path:
        path = self.base_path.joinpath(*parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    async def save_upload(self, file: UploadFile, role: str, job_id: str, max_bytes: int | None = None) -> tuple[str, int]:
        extension = Path(file.filename or "upload.bin").suffix
        storage_key = f"{job_id}/{role}/{uuid4().hex}{extension}"
        path = self._target_path(storage_key)
        size = 0
        with path.open("wb") as buffer:
            while chunk := await file.read(8192):
                buffer.write(chunk)
                size += len(chunk)
                if max_bytes and size > max_bytes:
                    buffer.close()
                    path.unlink(missing_ok=True)
                    raise ValueError("Uploaded file exceeds maximum allowed size")
        await file.close()
        return storage_key, size

    def open(self, storage_key: str) -> BinaryIO:
        path = self.base_path / storage_key
        return path.open("rb")

    def resolve_path(self, storage_key: str) -> Path:
        return self.base_path / storage_key

    def save_bytes(self, data: bytes, role: str, job_id: str, filename: str) -> tuple[str, int]:
        storage_key = f"{job_id}/{role}/{filename}"
        path = self._target_path(storage_key)
        path.write_bytes(data)
        return storage_key, len(data)


storage_service = StorageService(settings.storage_path)
