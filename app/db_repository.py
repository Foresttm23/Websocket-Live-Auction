from sqlalchemy.ext.asyncio import AsyncSession
from models import Lot, Bid, LotStatus
from sqlalchemy import select, Row, RowMapping


class Repository:
    @staticmethod
    async def get_active_lots(session: AsyncSession):
        result = await session.execute(
            select(Lot).where(Lot.status == LotStatus.running)
        )
        return result.scalars().all()

    @staticmethod
    async def get_lot(session: AsyncSession, lot_id: int):
        result = await session.execute(
            select(Lot).where(Lot.id == lot_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_lot_max_bid(session: AsyncSession, lot_id: int):
        result = await session.execute(
            select(Bid).where(Bid.lot_id == lot_id).order_by(Bid.amount.desc())
        )
        return result.scalars().first()
