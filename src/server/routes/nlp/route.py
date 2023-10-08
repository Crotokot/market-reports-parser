from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi import status, HTTPException
from pydantic import ValidationError

from . import models
from handlers import handlers


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        await websocket.close()
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()
nlp_route = APIRouter(prefix='/nlp')


@nlp_route.post("/summarize_test")
async def summarize_test(data: models.SummarizeBody):
    from websockets.client import connect
    from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
    async with connect("ws://localhost:8000/api/nlp/summarize") as websocket:
        print("Client: Connected to websocket")
        await websocket.send(data.model_dump_json())
        print("Client: Sent json response")
        try:
            while True:
                message = await websocket.recv()
                print(message)
        except ConnectionClosedOK:
            pass
        except ConnectionClosedError as ex:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Web socket closed error"
            )


@nlp_route.websocket("/summarize")
async def summarize(
    websocket: WebSocket
):
    await manager.connect(websocket)
    print("Server: establish connection")
    try:
        json_data = await websocket.receive_json()
        print("Server: receive request")
        data = models.SummarizeBody(**json_data)
        print("Server: validate request")
    except ValidationError as ex:
        print("Server: send json error")
        await websocket.send_json(ex.json())
    else:
        try:
            print("Server: summarize")
            for summary in handlers.summarize(
                content=data.content,
                model_name=data.options.model,
                compress_coef=data.options.compress_coef
            ):
                print("Server: send summary part")
                await websocket.send_json(summary)
        except WebSocketDisconnect:
            print("Server: WebSocketDisconnect exception")
            pass
        except ValueError as ex:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ex.args[0]
            )
        finally:
            print("Server: disconnect")
            await manager.disconnect(websocket)