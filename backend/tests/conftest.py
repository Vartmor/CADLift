import asyncio
import sys
from pathlib import Path

import pytest

# Ensure backend/ is on sys.path so `app` package imports resolve when running tests from repo root.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

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
