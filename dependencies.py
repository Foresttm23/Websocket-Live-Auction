from database import db

async def get_session():
    async with db.AsyncSessionLocal() as session:
        yield session
