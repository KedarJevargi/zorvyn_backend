from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

class Base(DeclarativeBase):
    pass

# Engine configuration optimized for high-concurrency production environments
engine = create_async_engine(
    settings.database_url, 
    echo=settings.environment == "development",
    
    # --- Production Pool Settings ---
    pool_pre_ping=True,      # Verify connection health before usage (prevents "server closed connection" errors)
    pool_size=20,            # Baseline number of persistent connections in the pool
    max_overflow=10,         # Allow up to 10 additional connections during traffic bursts
    pool_recycle=3600,       # Recycle connections every hour to prevent DB-side timeouts
    pool_timeout=30,         # How long to wait for an available connection before throwing an error
)

async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False, 
    autoflush=False          # Prevents premature flushes, giving you tighter control over transactions
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to provide an async database session per request.
    Ensures safe rollback on application errors and clean return to the connection pool.
    """
    async with async_session() as session:
        try:
            yield session
        except Exception:
            # If an error occurs in the request layer, rollback any uncommitted changes
            await session.rollback()
            raise
        # The 'async with' context manager automatically calls session.close() here, 
        # cleanly releasing the connection back to the pool.