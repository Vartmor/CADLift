import asyncio
import pytest

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure anyio to only use asyncio backend."""
    return "asyncio"


@pytest.fixture(autouse=True)
def reset_database():
    settings = get_settings()
    settings.enable_task_queue = False
    settings.llm_provider = "none"

    async def _reset():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_reset())
