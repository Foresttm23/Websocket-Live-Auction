from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


class DB:
    def __init__(self):
        self.DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"
        self.engine = create_async_engine(self.DATABASE_URL, echo=True)
        self.AsyncSessionLocal = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def get_db(self):
        async with self.AsyncSessionLocal() as session:
            yield session
