import socket
import http.server
import http.client
import random
from pathlib import Path
from redirect_ipv6 import get_my_IPv6
from Server import Server


server = Server()


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        if self.path in server.WEB_DICT:
            return server.WEB_DICT[self.path](self)
        else:
            self.send_response(301)
            self.send_header("location", f"http://[{get_my_IPv6()}]:{12345}")
            self.end_headers()


class HTTPServerV6(http.server.HTTPServer):
    address_family = socket.AF_INET6


server.redirect(301, "/", "/server/")


@server.add_page("/server/")
def _(handler: CustomHandler):
    with open("./src/server/index.html", "rb") as f:
        handler.wfile.write(f.read())


@server.add_page("/server/bundle.js", ("Content-Type", "application/javascript"))
def _(handler: CustomHandler):
    with open("./src/server/bundle.js", "rb") as f:
        handler.wfile.write(f.read())


image_folder = Path("./src/image")


@server.add_page("/image", ("Content-type", "image/png"))
def _(handler: CustomHandler):
    files = [f for f in image_folder.iterdir() if f.is_file()]
    file = random.choice(files)
    with open(file, "rb") as f:
        handler.wfile.write(f.read())


@server.add_page("/info")
def _(handler: CustomHandler):
    handler.wfile.write("Hello World".encode())


if __name__ == "__main__":
    print("IPv6 服务器正在启动")
    HTTPServerV6(("::", 8888), CustomHandler).serve_forever()
