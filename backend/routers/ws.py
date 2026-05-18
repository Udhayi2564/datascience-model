import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pipeline_executor import ws_connections

router = APIRouter()


@router.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await websocket.accept()
    if job_id not in ws_connections:
        ws_connections[job_id] = []
    ws_connections[job_id].append(websocket)
    try:
        while True:
            # Keep alive - client can send pings
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_connections[job_id].remove(websocket)
        if not ws_connections[job_id]:
            del ws_connections[job_id]
