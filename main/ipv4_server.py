import uvicorn
import sys

import page
from lika.server import Server
from lika.response import Response, Headers
from redirect_ipv6 import get_my_IPv6

if __name__ == "__main__":
    port = int(sys.argv[1])
    env = sys.argv[2]
    server = Server(env)
    root = server.router_map
    root.mount("./src", True)
    page.listing(root, "/list", "/")
    root.redirect(301, "/", "/index/")
    root.redirect(302, "/image", f"http://[{get_my_IPv6()}]:{port}/image/")
    root.redirect(302, "/doc", "https://karisaya.github.io/")
    root.redirect(302, "/server", f"http://[{get_my_IPv6()}]:{port}/")

    uvicorn.run(server, host="127.0.0.1", port=port)
