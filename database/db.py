from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, autocommit=False, autoflush=False,)


async def get_db():
    """
    Retrieves the database session for request processing.

    Returns:
        Session: The async SQLAlchemy database session.
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
