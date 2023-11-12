import http.server
import http.client
from redirect_ipv6 import get_my_IPv6
from Server import Server


server = Server()


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in server.WEB_DICT:
            return server.WEB_DICT[self.path](self)
        else:
            if self.path.startswith("/list"):
                self.path = self.path[5:]
            conn = http.client.HTTPConnection("127.0.0.1", 12345)
            conn.request(self.command, self.path)
            response = conn.getresponse()
            if response.status == 301:
                conn.request(self.command, response.getheader("Location"))
                response = conn.getresponse()
            self.send_response(response.status)
            for header in response.getheaders():
                self.send_header(header[0], header[1])
            self.end_headers()
            self.wfile.write(response.read())
            conn.close()


server.redirect(301, "/", "/index/")
server.redirect(301, "/list", "/list/")
server.redirect(301, "/index/home", "/home/")
server.redirect(302, "/index/doc", "https://karisaya.github.io/")
server.redirect(302, "/index/server", f"http://[{get_my_IPv6()}]:{8888}/")
server.redirect(302, "/index/server/", f"http://[{get_my_IPv6()}]:{8888}/")

if __name__ == "__main__":
    print("IPv4 服务器正在启动")
    http.server.HTTPServer(("0.0.0.0", 8888), CustomHandler).serve_forever()
