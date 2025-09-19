from sqlalchemy.ext.asyncio import AsyncSession
from models import Lot, Bid, LotStatus
from sqlalchemy import select


class Repository:
    @staticmethod
    async def get_active_lots(session: AsyncSession):
        result = await session.execute(
            select(Lot).where(Lot.status == LotStatus.running)
        )
        return result.scalars().all()
