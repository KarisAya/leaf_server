import socket
import http.server
import http.client
import os
import sys
import random
import json
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

    def do_POST(self):
        self.path = self.path.rstrip("/") or "/"
        if self.path in server.WEB_DICT:
            return server.WEB_DICT[self.path](self)
        self.send_response(404)
        self.end_headers()


class HTTPServerV6(http.server.HTTPServer):
    address_family = socket.AF_INET6


if __name__ == "__main__":
    port = int(sys.argv[1])
    env = sys.argv[2]
    server = Server()
    src = Path(os.path.join(os.path.dirname(__file__), "./src"))

    server.path("/", src)
    server.redirect(301, "/", "/server/")

    @server.api("/image", image_list=server.list_subpaths("/image/"))
    def _(handler: CustomHandler, image_list):
        server.WEB_DICT[random.choice(image_list)](handler)

    @server.api("/terminal")
    def _(handler: CustomHandler):
        content_length = int(handler.headers["Content-Length"])
        post_data = handler.rfile.read(content_length)
        data = json.loads(post_data).get("data") if post_data else "none"
        handler.send_response(200)
        handler.end_headers()
        resp = {}
        # 假的响应
        if data == "init":
            resp["path"] = "/server"
            resp["contect"] = ""
        else:
            resp["path"] = "/server"
            resp["contect"] = f"Recived:{data}"
        handler.wfile.write(json.dumps(resp).encode())

    server.path_mapping("/list", "/")
    server.listing_src("/list", src)  # 用目录覆盖映射

    print(f"IPv6 服务器正在启动,port:{port},env:{env}")
    HTTPServerV6(("::", port), CustomHandler).serve_forever()
