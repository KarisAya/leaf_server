import http.server
import http.client
import urllib.parse

from typing import Callable, Literal, Dict
from pathlib import Path


class Server:
    WEB_DICT: Dict[str, Callable] = {}

    def __init__(self, env: Literal["dev", "test", "prod"] = "dev"):
        self.env = env

    @staticmethod
    def path_to_url(path: Path) -> str:
        result = str(path).replace("\\", "/")
        if path.is_dir():
            result += "/"
        return urllib.parse.quote(result)

    def web(self, network_path: Path, Content_type: str):
        """
        添加web资源
        """

        def decorator(function: Callable):
            def wrapper(handler: http.server.SimpleHTTPRequestHandler):
                handler.send_response(200)
                handler.send_header("Content-type", Content_type)
                handler.end_headers()
                return function(handler)

            self.WEB_DICT[self.path_to_url(network_path)] = wrapper

        return decorator

    def file(self, network_path: Path, src_path: Path, Content_type: str):
        """
        文件添加为web资源
            network_path:网络路径
            src_path:本地资源路径
            Content_type:响应类型
        """

        if self.env == "prod":
            with open(src_path, "rb") as f:
                resp = f.read()

            @self.web(network_path, Content_type)
            def _(handler: http.server.SimpleHTTPRequestHandler):
                handler.wfile.write(resp)

        else:

            @self.web(network_path, Content_type)
            def _(handler: http.server.SimpleHTTPRequestHandler):
                with open(src_path, "rb") as f:
                    resp = f.read()
                handler.wfile.write(resp)

    def html(self, network_path: Path, src_path: Path):
        self.file(network_path, src_path, "text/html")

    def plain(self, network_path: Path, src_path: Path):
        self.file(network_path, src_path, "text/plain")

    def javascript(self, network_path: Path, src_path: Path):
        self.file(network_path, src_path, "application/javascript")

    def image(self, network_path: Path, src_path: Path, ext: str = "png"):
        self.file(network_path, src_path, f"image/{ext}")

    def video(self, network_path: Path, src_path: Path, ext: str = "mp4"):
        self.file(network_path, src_path, f"video/{ext}")

    def path(self, network_path: Path, src_path: Path):
        """
        把本地路径添加为web资源
            network_path:网络路径
            src_path:本地资源路径
        """
        src_path = Path(src_path)
        network_path = Path(network_path)
        for src_subpath in src_path.iterdir():
            network_subpath = network_path / src_subpath.relative_to(src_path)
            if src_subpath.is_dir():
                self.path(network_subpath, src_subpath)
                continue
            if src_subpath.name == "index.html":
                self.html(network_subpath, src_subpath)
                self.inner_redirect(
                    self.path_to_url(network_subpath.parent),
                    self.path_to_url(network_subpath),
                )
                continue
            ext = src_subpath.suffix
            if ext in {".html"}:
                self.html(network_subpath, src_subpath)
            elif ext in {".js"}:
                self.javascript(network_subpath, src_subpath)
            elif ext in {".jpg", ".png", ".jpeg", "gif", "webp"}:
                self.image(network_subpath, src_subpath, ext.lstrip("."))
            elif ext in {".mp4", ".avi", ".mkv", "webm"}:
                self.video(network_subpath, src_subpath, ext.lstrip("."))
            else:
                self.plain(network_subpath, src_subpath)

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

    def path_mapping(self, network_path: str, mapping_path: str):
        """
        网络位置映射另一个网络位置
            network_path:网络位置
            mapping_path:映射的网络位置
            network_path 不能是 mapping_path 的子目录
        """
        network_path = network_path.replace("\\", "/").rstrip("/") or "/"
        mapping_path = mapping_path.replace("\\", "/").rstrip("/")
        temp_path = [
            path
            for path in self.WEB_DICT.keys()
            if path.startswith(mapping_path) and not path.startswith(network_path)
        ]
        l = len(mapping_path)
        for path in temp_path:
            self.WEB_DICT[network_path + path[l:]] = self.WEB_DICT[path]

    def list_subpaths(self, network_path: str):
        return [x for x in self.WEB_DICT if x.startswith(network_path)]

    def listing_src(self, network_path: Path, src_path: Path):
        """
        展示本地路径，包括子文件夹
            network_path:网络路径
            src_path:本地资源路径
        """
        src_path = Path(src_path)
        network_path = Path(network_path)
        self.dir_list(network_path, src_path)
        for src_subpath in src_path.iterdir():
            network_subpath = network_path / src_subpath.relative_to(src_path)
            if src_subpath.is_dir():
                self.listing_src(network_subpath, src_subpath)

    def dir_list(self, network_path: Path, src_path: Path):
        body = []
        for src_subpath in src_path.iterdir():
            network_subpath = network_path / src_subpath.relative_to(src_path)
            network_subpath = self.path_to_url(network_subpath)
            body.append(f'<li><a href="{network_subpath}">{src_subpath.name}</a></li>')
        body = "\n".join(body)
        resp = f"""
        <!DOCTYPE html>
        <html lang="cn">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{src_path.name}</title>
        </head>
        <body>
            <h1>Directory listing for {str(network_path).replace("\\","/")}</h1>
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

    def inner_redirect(self, form_url: str, to_url: str):
        """
        内部重定向
        """
        self.WEB_DICT[form_url] = self.WEB_DICT[to_url]

    def redirect(self, status: Literal[301, 302], form_url: str, to_url: str):
        """
        重定向
        """

        def wrapper(handler: http.server.SimpleHTTPRequestHandler):
            handler.send_response(status)
            handler.send_header("Location", to_url)
            handler.end_headers()

        self.WEB_DICT[form_url] = wrapper

    def proxy(self, key: str, url: str):
        """
        代理
        """
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port
        path = parsed_url.path

        def wrapper(handler: http.server.SimpleHTTPRequestHandler):
            conn = http.client.HTTPConnection(host, port)

            def request(network_path: str):
                conn.request(handler.command, network_path)
                resp = conn.getresponse()
                if resp.status == 301:
                    return request(resp.getheader("Location"))
                return resp

            resp = request(path)
            handler.send_response(resp.status)
            for header in resp.getheaders():
                handler.send_header(*header)
            handler.end_headers()
            handler.wfile.write(resp.read())
            conn.close()

        self.PROXY_DICT[key] = wrapper
