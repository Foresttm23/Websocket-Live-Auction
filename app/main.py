from fastapi import FastAPI

from lot_watcher import lot_watcher
from database import db
import endpoints
app = FastAPI()

app.include_router(endpoints.router)

@app.on_event("startup")
async def init_db():
    await db.create_db()
    lot_watcher.start()
