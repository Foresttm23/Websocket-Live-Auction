from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from connection_manager import manager
from database import db
from dependencies import get_session
from models import Lot, Bid, LotStatus
from requests import LotRequest, BidRequest, LotResponse
from datetime import datetime, timedelta

router = APIRouter()


@router.post("/lots")
async def create_lot(lot_request: LotRequest, session: AsyncSession = Depends(get_session)):
    """
    Creates a lot.
    Default launch parameters at models.py
    """
    lot = Lot(**lot_request.model_dump())
    session.add(lot)
    await session.commit()

    return {
        "message": "Lot created",
        "lot_id": lot.id
    }


@router.post("/lots/{lot_id}/bids")
async def place_bid(lot_id: int, bid_request: BidRequest, session: AsyncSession = Depends(get_session)):
    """
    Places a bid, and refreshes the timer
    """
    result = await session.execute(select(Lot).where(Lot.id == lot_id))
    lot = result.scalars().first()

    if not lot or lot.status != LotStatus.running:
        raise HTTPException(status_code=400, detail="Lot not available")

    result = await session.execute(
        select(Bid).where(Bid.lot_id == lot_id).order_by(Bid.amount.desc())
    )
    max_bid = result.scalars().first()

    if max_bid and bid_request.amount <= max_bid.amount:
        raise HTTPException(status_code=400, detail="Bid must be higher than current maximum")

    new_bid = Bid(**bid_request.model_dump(), lot_id=lot_id)
    session.add(new_bid)

    if datetime.utcnow() - lot.end_time <= timedelta(seconds=60):
        lot.end_time = datetime.utcnow() + timedelta(seconds=60)

    await session.commit()

    await manager.broadcast(lot_id, {
        "message": "New bid placed",
        "amount": bid_request.amount,
        "bidder": bid_request.bidder,
        "time left": abs(datetime.utcnow() - lot.end_time)
    })

    return {
        "message": "Bid placed",
        "new_bid": bid_request.amount
    }


@router.get("/lots", response_model=list[LotResponse])
async def get_active_lots(session: AsyncSession = Depends(get_session)):
    """
    Returns all active lots.
    """
    result = await session.execute(select(Lot).where(Lot.status == LotStatus.running))
    return result.scalars().all()


@router.websocket("/ws/lots/{lot_id}")
async def ws_subscribe_to_lot(websocket: WebSocket, lot_id: int):
    await manager.connect(websocket, lot_id)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket, lot_id)

    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, lot_id)
