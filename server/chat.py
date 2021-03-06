import ujson

from sanic import Sanic
from sanic import response
from sanic.request import Request
from sanic.exceptions import abort
from sanic.websocket import WebSocketCommonProtocol

from websockets.exceptions import ConnectionClosed

from room import Room, UserAlreadyExists


app = Sanic('chat')
app.static('/static', './static')
app.config.rooms = {}


@app.route('/')
async def index(request: Request):
    return await response.file('static/index.html')


@app.websocket('/chat')
async def register_user(request: Request, ws: WebSocketCommonProtocol):

    if 'name' not in request.args or 'room' not in request.args:
        abort(400)

    name_s = request.args['name'][0]
    room_s = request.args['room'][0]

    if room_s not in app.config.rooms:
        app.config.rooms[room_s] = Room(room_s)

    room = app.config.rooms[room_s]
    try:
        room.add_user(name_s, ws)
    except UserAlreadyExists:
        print(f'{name_s} already exists')
        await ws.close(code=1003, reason='UserAlreadyExists')
        return

    while True:
        try:
            data = ujson.loads(await ws.recv())
        except ConnectionClosed:
            return

        await room.send_message(**data)



