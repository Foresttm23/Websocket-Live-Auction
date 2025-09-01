from fastapi import FastAPI
import asyncio

from lot_watcher import lot_watcher
from database import db
import endpoints

app = FastAPI()

app.include_router(endpoints.router)


@app.on_event("startup")
async def init_db():
    await db.create_db()


@app.on_event("startup")
async def start_watcher():
    asyncio.create_task(lot_watcher.check_lots())
