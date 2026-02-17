from typing import AsyncGenerator
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from dotenv import load_dotenv
import os
from ..models.inventory_model import Base

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

DATABASE_CONN_STRING = os.getenv("AUTH_DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/auth_db.db")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

engine = create_async_engine(
    DATABASE_CONN_STRING,
    echo=DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=10,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        await init_db()  # Ensure tables are created before yielding the session
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        
async def dispose_engine() -> None:
    await engine.dispose()