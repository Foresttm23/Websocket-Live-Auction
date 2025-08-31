from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DB:
    def __init__(self):
        self.DATABASE_URL = "postgresql+asyncpg://forest:2515@db:5432/auction"
        self.engine = create_async_engine(self.DATABASE_URL, echo=True)
        self.AsyncSessionLocal = async_sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def create_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

db = DB()
