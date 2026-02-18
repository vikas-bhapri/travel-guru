from typing import AsyncGenerator
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from dotenv import load_dotenv
import os
import asyncpg
from urllib.parse import urlparse
from ..models.inventory_model import Base

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

DATABASE_CONN_STRING = os.getenv("AUTH_DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/auth_db.db")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

async def ensure_database_exists() -> None:
    """Create the database if it doesn't exist (for PostgreSQL only)"""
    if not DATABASE_CONN_STRING.startswith("postgresql"):
        return
    
    # Parse the database URL
    parsed = urlparse(DATABASE_CONN_STRING.replace("postgresql+asyncpg://", "postgresql://"))
    database_name = parsed.path.lstrip("/")
    
    # Create connection URL to 'postgres' database (without the target database)
    postgres_url = f"postgresql://{parsed.netloc}/postgres"
    
    try:
        # Connect to the default 'postgres' database
        conn = await asyncpg.connect(postgres_url)
        try:
            # Check if the database exists
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", database_name
            )
            
            if not exists:
                # Create the database
                await conn.execute(f'CREATE DATABASE "{database_name}"')
                print(f"Database '{database_name}' created successfully")
            else:
                print(f"Database '{database_name}' already exists")
        finally:
            await conn.close()
    except Exception as e:
        print(f"Error ensuring database exists: {e}")
        raise

# Ensure database exists before creating engine (for PostgreSQL)
if DATABASE_CONN_STRING.startswith("postgresql"):
    import asyncio
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No event loop running, create one
        asyncio.run(ensure_database_exists())

engine = create_async_engine(
    DATABASE_CONN_STRING,
    echo=DEBUG,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,
    connect_args={
        "server_settings": {"application_name": "inventory_service"},
        "command_timeout": 60,
        "statement_cache_size": 0  # Disable prepared statement cache for asyncpg
    } if DATABASE_CONN_STRING.startswith("postgresql") else {},
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def init_db() -> None:
    # Ensure database exists (if not already done)
    await ensure_database_exists()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        
async def dispose_engine() -> None:
    await engine.dispose()