import http.server
import http.client
import urllib.parse

from typing import Callable, Literal, Dict
from pathlib import Path


class Server:
    WEB_DICT: Dict[str, Callable] = {}

    def web(self, network_path: Path, Content_type: str = "text/html"):
        """
        添加web资源
        """

        def decorator(function: Callable):
            def wrapper(handler: http.server.SimpleHTTPRequestHandler):
                handler.send_response(200)
                handler.send_header("Content-type", Content_type)
                handler.end_headers()
                return function(handler)

            self.WEB_DICT[
                urllib.parse.quote(str(network_path).replace("\\", "/"))
            ] = wrapper

        return decorator

    def file(self, network_path: Path, src_file: Path, Content_type: str):
        """
        文件添加为web资源
            network_path:网络路径
            src_path:本地资源路径
            Content_type:响应类型
        """
        with open(src_file, "rb") as f:
            resp = f.read()

        @self.web(network_path, Content_type)
        def _(handler: http.server.SimpleHTTPRequestHandler):
            handler.wfile.write(resp)

    def html(self, network_path: Path, src_file: Path):
        self.file(network_path, src_file, "text/html")

    def plain(self, network_path: Path, src_file: Path):
        self.file(network_path, src_file, "text/plain")

    def javascript(self, network_path: Path, src_file: Path):
        self.file(network_path, src_file, "application/javascript")

    def image(self, network_path: Path, src_file: Path, ext: str = "png"):
        self.file(network_path, src_file, f"image/{ext}")

    def video(self, network_path: Path, src_file: Path, ext: str = "mp4"):
        self.file(network_path, src_file, f"video/{ext}")

    def path(self, network_path: Path, src_path: Path):
        """
        把本地路径添加为web资源
            network_path:网络路径
            src_path:本地资源路径
        """
        src_path = Path(src_path)
        network_path = Path(network_path)
        for son_src_path in src_path.iterdir():
            son_network_path = network_path / son_src_path.relative_to(src_path)
            if son_src_path.is_dir():
                self.path(son_network_path, son_src_path)
                continue
            if son_src_path.name == "index.html":
                self.html(son_network_path, son_src_path)
                self.inner_redirect(son_network_path.parent, son_network_path)
                continue
            ext = son_src_path.suffix
            if ext in {".html"}:
                self.html(son_network_path, son_src_path)
            elif ext in {".js"}:
                self.javascript(son_network_path, son_src_path)
            elif ext in {".jpg", ".png", ".jpeg", "gif", "webp"}:
                self.image(son_network_path, son_src_path, ext.lstrip("."))
            elif ext in {".mp4", ".avi", ".mkv", "webm"}:
                self.video(son_network_path, son_src_path, ext.lstrip("."))
            else:
                self.plain(son_network_path, son_src_path)

    def path_mapping(self, network_path: str, mapping_path: str):
        """
        网络位置映射另一个网络位置
            network_path:网络位置
            mapping_path:映射的网络位置
        """
        network_path = network_path.replace("\\", "/").rstrip("/") or "/"
        mapping_path = mapping_path.replace("\\", "/").rstrip("/") or "/"
        temp_path = [
            path
            for path in self.WEB_DICT.keys()
            if path.startswith(mapping_path) and not path.startswith(network_path)
        ]
        l = len(mapping_path) - 1
        for path in temp_path:
            self.WEB_DICT[network_path + path[l:]] = self.WEB_DICT[path]

    def api(self, network_path: Path, **kwargs):
        """
        添加应用接口
        """

        def decorator(function: Callable):
            def wrapper(handler: http.server.SimpleHTTPRequestHandler):
                return function(handler, **kwargs)

            self.WEB_DICT[
                urllib.parse.quote(str(network_path).replace("\\", "/"))
            ] = wrapper

        return decorator

    def son_path(self, network_path: str):
        return [x for x in self.WEB_DICT if x.startswith(network_path)]

    def listing(self, network_path: Path, src_path: Path):
        """
        展示本地路径，包括子文件夹
            network_path:网络路径
            src_path:本地资源路径
        """
        src_path = Path(src_path)
        network_path = Path(network_path)
        self.dir_list(network_path, src_path)
        for son_src_path in src_path.iterdir():
            son_network_path = network_path / son_src_path.relative_to(src_path)
            if son_src_path.is_dir():
                self.listing(son_network_path, son_src_path)

    def dir_list(self, network_path: Path, src_path: Path):
        body = []
        for f in src_path.iterdir():
            f_network_path = str(network_path / f.relative_to(src_path)).replace(
                "\\", "/"
            )
            f_network_path = f_network_path + "/" if f.is_dir() else f_network_path
            body.append(f'<li><a href="{f_network_path}">{f.name}</a></li>')
        body = "\n".join(body)
        network_path = str(network_path).replace("\\", "/")
        resp = f"""
        <!DOCTYPE html>
        <html lang="cn">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{src_path.name}</title>
        </head>
        <body>
            <h1>Directory listing for {network_path}</h1>
            <hr>
            <ul>
            {body}
            </ul>
        </body>
        </html>
        """
        resp = resp.encode()

        @self.web(network_path, "text/html")
        def _(handler: http.server.SimpleHTTPRequestHandler):
            handler.wfile.write(resp)

    def inner_redirect(self, network_path: str, redirect_path: str):
        """
        内部重定向
        """
        network_path = str(network_path).replace("\\", "/")
        redirect_path = str(redirect_path).replace("\\", "/")
        self.WEB_DICT[network_path] = self.WEB_DICT[redirect_path]

    def redirect(self, status: Literal[301, 302], network_path: str, url: str):
        """
        重定向
        """

        def wrapper(handler: http.server.SimpleHTTPRequestHandler):
            handler.send_response(status)
            handler.send_header("Location", url)
            handler.end_headers()

        self.WEB_DICT[network_path] = wrapper

    def proxy(self, network_path: str, url: str):
        """
        代理
        """
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port
        path = parsed_url.path.lstrip("/")

        def wrapper(handler: http.server.SimpleHTTPRequestHandler):
            conn = http.client.HTTPConnection(host, port)

            def request(network_path: str):
                conn.request(handler.command, network_path)
                resp = conn.getresponse()
                if resp.status == 301:
                    return request(resp.getheader("Location"))
                return resp

            resp = request(path + network_path)
            handler.send_response(resp.status)
            for header in resp.getheaders():
                handler.send_header(*header)
            handler.end_headers()
            handler.wfile.write(resp.read())
            conn.close()

        self.WEB_DICT[network_path] = wrapper
