import asyncio
from datetime import datetime, timedelta
from sqlalchemy import Sequence

from connection_manager import manager
from models import Lot, Bid, LotStatus
from sqlalchemy.ext.asyncio import AsyncSession
from database import db_dependency
from db_repository import Repository


class LotWatcher:
    def __init__(self, interval: int = 1):
        self.interval = interval
        self.task = None
        self.timer = 5.0
        self.last_broadcast = datetime.utcnow()

    @staticmethod
    async def _update_ended_lots(db: AsyncSession, running_lots: Sequence[Lot], now: datetime, repository: Repository):
        """
        Updates `status` of `lot` if time elapsed
        Calls `manager.broadcast` to notify all `lot` subscribers
        """
        changed = False
        for lot in running_lots:
            time_left = (lot.end_time - now).total_seconds()

            if time_left <= 0:
                lot.status = LotStatus.ended
                changed = True

                max_bid = await repository.get_lot_max_bid(db, lot.lot_id) or 0

                await manager.broadcast(
                    lot.id,
                    {
                        "message": "Lot ended",
                        "start_price": float(lot.start_price),
                        "max_bid": float(max_bid),
                        "lot_id": lot.id
                    }
                )
        if changed:
            await db.commit()

    async def _update_lots_on_timer(self, db: AsyncSession, running_lots: Sequence[Lot], now: datetime,
                                    repository: Repository):
        """
        Updates `time` until `lot` is ended
        Calls `manager.broadcast` to notify all `lot` subscribers
        """
        if (now - self.last_broadcast).total_seconds() >= self.timer:
            for lot in running_lots:
                if lot.status == LotStatus.running:
                    max_bid = await repository.get_lot_max_bid(db, lot.lot_id) or 0

                    time_left = max((lot.end_time - now).total_seconds(), 0)
                    await manager.broadcast(
                        lot.id,
                        {
                            "message": "Time update",
                            "lot_id": lot.id,
                            "start_price": float(lot.start_price),
                            "max_bid": float(max_bid),
                            "time_till_end": time_left
                        }
                    )
            self.last_broadcast = now

    async def check_lots(self, db: AsyncSession = db_dependency):
        """
        Checks `lots` if time elapsed
        Updates time on `lots` each time timer elapsed
        Calls `manager.broadcast` to notify all `lot` subscribers
        """
        repository = Repository()
        while True:
            running_lots = await repository.get_active_lots(db)
            now = datetime.utcnow()

            await self._update_ended_lots(db, running_lots, now, repository)
            await self._update_lots_on_timer(db, running_lots, now, repository)

            await asyncio.sleep(self.interval)


lot_watcher = LotWatcher()
