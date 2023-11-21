import uvicorn
import sys

import page
from lika.server import Server
from lika.response import Response, Headers
from redirect_ipv6 import get_my_IPv6

if __name__ == "__main__":
    # port = int(sys.argv[1])
    # env = sys.argv[2]
    port = 8080
    env = "dev"
    server = Server(env)
    root = server.router_map
    root.mount("./src", True)
    page.listing(root, "/list", "/")
    root.redirect(301, "/", "/index/")

    @root.router("/test", k="Hello World")
    async def _(scope, receive, k):
        return Response(200, Headers.from_ext("txt"), [k.encode()])

    sub_map = root.set_map("/sub_map")

    @sub_map.router("/code/{code}/{others}/ok")
    async def _(scope, receive, code, others):
        return Response(int(code), Headers.from_ext("txt"), [others.encode()])

    # root.redirect(302, "/image", f"http://[{get_my_IPv6()}]:{port}/image/")
    # root.redirect(302, "/doc", "https://karisaya.github.io/")
    # root.redirect(302, "/server", f"http://[{get_my_IPv6()}]:{port}/")

    uvicorn.run(server, host="127.0.0.1", port=port)
