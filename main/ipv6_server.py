import uvicorn
import sys
import random
import json
import page
from lika.server import Server, RouterMap
from lika.response import Response
from redirect_ipv6 import get_my_IPv6

if __name__ == "__main__":
    port = int(sys.argv[1])
    env = sys.argv[2]
    server = Server(env)
    server.mount("/", "./src", True)
    page.listing(server, "/list", "/")
    server.redirect(301, "/", "/server/")

    @server.api(
        "/image",
        image_list=[x["/"] for x in server.get_router("image").values() if "/" in x],
    )
    async def _(scope, receive, send, image_list: RouterMap):
        await random.choice(image_list)(scope, receive, send)

    @server.api("/terminal")
    async def _(scope, receive, send):
        data = json.loads((await receive())["body"])
        data = data["data"]
        resp = {}
        # 假的响应
        if data == "init":
            resp["path"] = "/server"
            resp["contect"] = ""
        else:
            resp["path"] = "/server"
            resp["contect"] = f"recived:{data}"
        await Response(
            headers=[(b"Content-type", b"text/plain")],
            bodys=[json.dumps(resp).encode()],
            send_method=send,
        ).send()

    uvicorn.run(server, host="::", port=port)
