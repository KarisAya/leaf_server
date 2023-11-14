import http.server
import os
import sys

from pathlib import Path


from redirect_ipv6 import get_my_IPv6
from Server import Server


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.path = self.path.rstrip("/") or "/"
        if self.path in server.WEB_DICT:
            return server.WEB_DICT[self.path](self)
        self.send_response(404)
        self.end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1])
    env = sys.argv[2]
    server = Server(env)
    src = Path(os.path.join(os.path.dirname(__file__), "./src"))
    server.path("/", src)

    server.redirect(301, "/", "/index/")
    server.redirect(302, "/image", f"http://[{get_my_IPv6()}]:{port}/image/")
    server.redirect(302, "/doc", "https://karisaya.github.io/")
    server.redirect(302, "/server", f"http://[{get_my_IPv6()}]:{port}/")

    server.path_mapping("/list", "/")
    server.listing_src("/list", src)  # 用目录覆盖映射

    # for x in server.WEB_DICT:
    #     print(x)

    print(f"IPv4 服务器正在启动,port:{port},env:{env}")
    http.server.HTTPServer(("0.0.0.0", port), CustomHandler).serve_forever()
