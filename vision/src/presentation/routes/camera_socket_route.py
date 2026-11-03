from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.dependencies import get_web_socket_service

camera_socket_router = APIRouter(tags=["camera socket"])


@camera_socket_router.websocket("/ws")
async def camera_socket(websocket: WebSocket):
    service = await get_web_socket_service()

    await websocket.accept()
    service.subscribe(websocket, dict(websocket.query_params))

    try:
        while True:
            raw_message = await websocket.receive_text()
            await service.handle_message(websocket, raw_message)
    except WebSocketDisconnect:
        pass
    finally:
        service.unsubscribe(websocket)
