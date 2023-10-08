import dataclasses
import json
import typing

from websockets.client import connect
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

from . import config


@dataclasses.dataclass
class Json(object):
    def to_json(self) -> str:
        return json.dumps(dataclasses.asdict(self))


@dataclasses.dataclass
class Options(Json):
    model: str
    content_type: typing.Literal['text', 'html', 'pdf']
    compress_coef: float = 0.5


@dataclasses.dataclass
class SummarizeBody(Json):
    content: str
    options: Options


async def send_data(
    content: str,
    callback,
    model: str = "BART",
    content_type: typing.Literal['text', 'html', 'pdf'] = 'text',
    compress_coef: float = 0.5
):
    data = SummarizeBody(
        content=content,
        options=Options(
            model=model,
            content_type=content_type,
            compress_coef=compress_coef
        )
    )
    async with connect(config.endpoint) as websocket:
        print("Client: Connected to websocket")
        await websocket.send(data.to_json())
        print("Client: Sent json response")
        try:
            while True:
                data = await websocket.recv()
                message = json.loads(data)[0]["summary_text"]
                callback.emit(message)
        except ConnectionClosedOK:
            pass
        except ConnectionClosedError as ex:
            print("Error")