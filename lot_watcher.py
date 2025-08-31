import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, func

from connection_manager import manager
from models import Lot, Bid, LotStatus
from database import db


class LotWatcher:
    def __init__(self, interval: int = 1):
        self.interval = interval
        self.task = None
        self.timer = 5.0
        self.last_broadcast = datetime.utcnow()

    async def check_lots(self):
        while True:
            async with db.AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Lot).where(Lot.status == LotStatus.running)
                )
                running_lots = result.scalars().all()

                now = datetime.utcnow()
                changed = False

                for lot in running_lots:
                    time_left = (lot.end_time - now).total_seconds()

                    if time_left <= 0:
                        lot.status = LotStatus.ended
                        changed = True

                        result = await session.execute(
                            select(func.max(Bid.amount)).where(Bid.lot_id == lot.id)
                        )
                        highest_bid = result.scalar() or 0

                        await manager.broadcast(
                            lot.id,
                            {
                                "message": "Lot ended",
                                "highest_bid": highest_bid,
                                "lot_id": lot.id
                            }
                        )

                if changed:
                    await session.commit()

                if (now - self.last_broadcast).total_seconds() >= self.timer:
                    for lot in running_lots:
                        if lot.status == LotStatus.running:
                            result = await session.execute(
                                select(func.max(Bid.amount)).where(Bid.lot_id == lot.id)
                            )
                            highest_bid = result.scalar() or 0

                            time_left = max((lot.end_time - now).total_seconds(), 0)
                            await manager.broadcast(
                                lot.id,
                                {
                                    "message": "Time update",
                                    "lot_id": lot.id,
                                    "highest_bid": highest_bid,
                                    "time_till_end": time_left
                                }
                            )
                    self.last_broadcast = now

            await asyncio.sleep(self.interval)

    def start(self):
        if not self.task:
            self.task = asyncio.create_task(self.check_lots())


lot_watcher = LotWatcher()
