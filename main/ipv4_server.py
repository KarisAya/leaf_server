import uvicorn
import sys

import page
from lika.server import Server
from redirect_ipv6 import get_my_IPv6


if __name__ == "__main__":
    port = int(sys.argv[1])
    env = sys.argv[2]
    server = Server(env)
    server.mount("/", "./src", True)
    page.listing(server, "/list", "/")
    server.inner_redirect("/test", "/")
    server.redirect(301, "/", "/index/")
    server.redirect(302, "/image", f"http://[{get_my_IPv6()}]:{port}/image/")
    server.redirect(302, "/doc", "https://karisaya.github.io/")
    server.redirect(302, "/server", f"http://[{get_my_IPv6()}]:{port}/")
    uvicorn.run(server, host="0.0.0.0", port=port)
