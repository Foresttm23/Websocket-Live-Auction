from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, lot_id: int):
        await websocket.accept()
        if lot_id not in self.connections:
            self.connections[lot_id] = []

        self.connections[lot_id].append(websocket)

    def disconnect(self, websocket: WebSocket, lot_id: int):
        if lot_id in self.connections and websocket in self.connections[lot_id]:
            self.connections[lot_id].remove(websocket)

    async def broadcast(self, lot_id: int, message: dict):
        for ws in self.connections.get(lot_id, []):
            await ws.send_json(message)


manager = ConnectionManager()
