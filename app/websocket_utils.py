from typing import Set
from fastapi import WebSocket

active_connections: Set[WebSocket] = set()

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        active_connections.remove(websocket)

async def send_update_to_connections(message: str):
    for connection in active_connections:
        await connection.send_text(message)

async def commit_and_notify(session, num_rows: int):
    try:
        session.commit()
    except Exception as e:
        print(f"Error during commit: {e}")
    else:
        message = f"Se han añadido {num_rows} nuevas entradas a la base de datos."
        await send_update_to_connections(message)