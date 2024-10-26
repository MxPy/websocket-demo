from fastapi import Depends, FastAPI, status, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator
import uvicorn
import logging
import sys
import asyncio
import json
import logging
import random
import uuid
from websocket.connectionManager import ConnectionManager

# Konfiguracja loggera
ch = logging.StreamHandler(sys.stdout)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[ch]
)

MSG_LOG = dict()
PREFECTH_COUNT = 100
logger = logging.getLogger()
manager = ConnectionManager()

async def send_periodic_messages():
    room_id = "chuj"
    while True:
        try:
            logging.info("message sent")
            message = {
                "timestamp": datetime.now().isoformat(),
                "message": f"Automatyczna wiadomość: {random.randint(1, 1000)}"
            }
            await manager.broadcast(room_id, message)
            await asyncio.sleep(1)  # Czekaj 1 sekundę
        except Exception as e:
            logger.error(f"Błąd podczas wysyłania okresowej wiadomości: {e}")
            await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    periodic_task = asyncio.create_task(send_periodic_messages())
    yield
    periodic_task.cancel()
    try:
        await periodic_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def logging_init():
    logging.info("Starting websocket")

@app.get("/")
async def read_root():
    return JSONResponse(content={"Hello": "World"})

@app.get("/healthcheck")
def healthcheck():
    """
    Check the health of the application.
    """
    return JSONResponse(content={"status": "ok"})

@app.websocket("/connect")
async def user_connect(websocket: WebSocket):
    room_id = "chuj"
    await manager.connect(str(room_id), websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(str(room_id), data)
    except WebSocketDisconnect:
        await manager.disconnect(str(room_id), websocket)

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)