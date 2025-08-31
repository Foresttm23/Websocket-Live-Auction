from fastapi import FastAPI

from connection_manager import manager
from lot_watcher import lot_watcher
from database import db

app = FastAPI()


@app.on_event("startup")
async def init_db():
    await db.create_db()
    lot_watcher.start()
