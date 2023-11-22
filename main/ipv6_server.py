import uvicorn
import sys
import random
import json
from pathlib import Path

import page
from lika.server import Server, RouterMap
from lika.response import Response, Headers
from redirect_ipv6 import get_my_IPv6

if __name__ == "__main__":
    port = int(sys.argv[1])
    env = sys.argv[2]
    server = Server(env)
    root = server.router_map
    root.mount("./src", True)
    page.listing(root, "/list", "/")
    root.redirect(301, "/", "/server/")

    @root.router("/image", image_src=list(Path("./src/image").iterdir()))
    async def _(scope, receive, image_src: list):
        image = random.choice(image_src)
        with open(image, "rb") as f:
            return Response(200, Headers.from_ext(image.suffix), [f.read()])

    @root.router("/terminal")
    async def _(scope, receive):
        request = await receive()
        data = request["body"].decode()
        resp = {}
        if data == "init":
            resp["path"] = "/server"
            resp["contect"] = ""
        else:
            resp["path"] = "/server"
            resp["contect"] = f"recived:{data}"
        return Response(200, Headers.from_ext("txt"), [json.dumps(resp).encode()])

    uvicorn.run(server, host="::", port=port)
