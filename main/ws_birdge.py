import asyncio
import websockets

try:
    import ujson as json
except ModuleNotFoundError:
    import json


async def bridge(from_websocket, to_websocket):
    """
    websocket消息转发器
    """
    try:
        async for message in from_websocket:
            await to_websocket.send(message)
    except websockets.exceptions.ConnectionClosedOK:
        pass
    finally:
        print(f"Client disconnected")


async def connect(url, extra_headers: dict = {}):
    print(f"尝试链接 {url}")
    while True:
        try:
            websocket = await websockets.connect(url, extra_headers=extra_headers)
            break
        except Exception as e:
            print(e)
        await asyncio.sleep(10)
    return websocket


async def handle_connection(websocket, path):
    request_headers: dict = websocket.request_headers._dict
    extra_headers = {
        "x-client-role": request_headers["x-client-role"],
        "x-self-id": request_headers["x-self-id"],
    }
    print(extra_headers)
    nonebot = await connect("ws://localhost:10001/onebot/v11/", extra_headers)
    await asyncio.gather(bridge(websocket, nonebot), bridge(nonebot, websocket))


async def server():
    server = await websockets.serve(handle_connection, "0.0.0.0", 11100)
    await server.wait_closed()


asyncio.run(server())
