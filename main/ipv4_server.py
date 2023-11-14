import http.server
import os
import random

from pathlib import Path


from redirect_ipv6 import get_my_IPv6
from Server import Server


server = Server()


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.path = self.path.rstrip("/") or "/"
        if self.path in server.WEB_DICT:
            return server.WEB_DICT[self.path](self)
        self.send_response(404)
        self.end_headers()


src = Path(os.path.join(os.path.dirname(__file__), "./src"))
server.path("/", src)


@server.api("/image", image_list=server.son_path("/image/"))
def _(handler: CustomHandler, image_list):
    server.WEB_DICT[random.choice(image_list)](handler)


server.redirect(301, "/", "/index/")
server.redirect(302, "/doc", "https://karisaya.github.io/")
server.redirect(302, "/server", f"http://[{get_my_IPv6()}]:{8888}/")

server.path_mapping("/list", "/")
server.listing("/list", src)  # 用目录覆盖映射

if __name__ == "__main__":
    print("IPv4 服务器正在启动")
    http.server.HTTPServer(("0.0.0.0", 8888), CustomHandler).serve_forever()
