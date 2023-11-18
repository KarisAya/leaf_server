from typing import Any, Coroutine, Literal, Self, Dict
from pathlib import Path


from .response import Response, Headers
from .router import RouterPath


Env = Literal["dev", "test", "prod"]

Not_Found = Response(404)


class ResponseMap(Dict[str, Self]):
    def set_map(self, response_map: Self):
        self.clear()
        self.update(response_map)

    def set_router(self, path: RouterPath) -> Self:
        response = self
        for k in RouterPath(path):
            response = response.setdefault(k, ResponseMap())
        return response

    def get_router(self, path: RouterPath) -> Self:
        response = self
        for k in RouterPath(path):
            if k in response:
                response = response[k]
            else:
                return None
        return response

    def is_file(self):
        return len(self) == 1 and "/" in self

    def is_dir(self):
        return not self.is_file()


class Server:
    response_map = ResponseMap()

    def __init__(self, env: Env = "dev"):
        self.env = env

    async def __call__(self, scope, receive, send):
        response = self.get_router(RouterPath(scope["path"]))
        if response and "/" in response:
            return await response["/"](scope, receive, send)
        Not_Found.send_method = send
        return await Not_Found.send()

    def set_router(self, path: RouterPath):
        return self.response_map.set_router(path)

    def get_router(self, path: RouterPath):
        return self.response_map.get_router(path)

    def web(self, network_path: RouterPath):
        """
        添加web资源
        """
        response = self.set_router(RouterPath(network_path))

        def decorator(function: Coroutine):
            response["/"] = function

        return decorator

    def file(self, network_path: RouterPath, src_path: Path, headers: Headers):
        """
        文件添加为web资源
            network_path:网络路径
            src_path:本地资源路径
            Content_type:响应类型
        """
        if self.env == "prod":
            with open(src_path, "rb") as f:
                resp = Response(200, headers, [f.read()])

            @self.web(network_path)
            async def _(scope, receive, send):
                resp.send_method = send
                await resp.send()

        else:

            @self.web(network_path)
            async def _(scope, receive, send):
                with open(src_path, "rb") as f:
                    await Response(200, headers, [f.read()], send).send()

    def html(self, network_path: RouterPath, src_path: Path):
        headers = [(b"Content-type", b"text/html")]
        self.file(network_path, src_path, headers)

    def plain(self, network_path: RouterPath, src_path: Path):
        headers = [(b"Content-type", b"text/plain")]
        self.file(network_path, src_path, headers)

    def javascript(self, network_path: RouterPath, src_path: Path):
        headers = [(b"Content-type", b"application/javascript")]
        self.file(network_path, src_path, headers)

    def image(self, network_path: RouterPath, src_path: Path, ext: str = "png"):
        headers = [(b"Content-type", f"image/{ext}".encode())]
        self.file(network_path, src_path, headers)

    def video(self, network_path: RouterPath, src_path: Path, ext: str = "mp4"):
        headers = [(b"Content-type", f"video/{ext}".encode())]
        self.file(network_path, src_path, headers)

    def download(self, network_path: RouterPath, src_path: Path):
        headers = [
            (b"Content-type", b"application/octet-stream"),
            (b"Content-disposition", b"attachment"),
        ]
        self.file(network_path, src_path, headers)

    def mount(self, network_path: RouterPath, src_path: Path, html: bool = False):
        """
        把本地路径添加为web资源
            network_path:网络路径
            src_path:本地资源路径
        """
        network_path = RouterPath(network_path)
        src_path = Path(src_path)
        for src_sp in src_path.iterdir():
            network_sp = network_path + RouterPath(src_sp.relative_to(src_path))
            if src_sp.is_dir():
                self.mount(network_sp, src_sp, html)
                continue
            if html and src_sp.name == "index.html":
                self.html(network_sp, src_sp)
                self.inner_redirect(network_sp[:-1], network_sp)
                continue
            ext = src_sp.suffix
            if ext in {".html"}:
                self.html(network_sp, src_sp)
            elif ext in {".js"}:
                self.javascript(network_sp, src_sp)
            elif ext in {".txt", ".json"}:
                self.plain(network_sp, src_sp)
            elif ext in {".jpg", ".png", ".jpeg", "gif", "webp"}:
                self.image(network_sp, src_sp, ext.lstrip("."))
            elif ext in {".mp4", ".avi", ".mkv", "webm"}:
                self.video(network_sp, src_sp, ext.lstrip("."))
            else:
                self.download(network_sp, src_sp)

    def inner_redirect(self, network_path: RouterPath, redirect_to: RouterPath):
        """
        内部重定向
            如果你想无限递归的话,请内部重定向到自己的父路径
        """
        network_resp = self.set_router(network_path)
        redirect_resp = self.get_router(redirect_to)
        network_resp.update(redirect_resp)

    def redirect(
        self, code: Literal[301, 302], network_path: RouterPath, redirect_to: str
    ):
        """
        重定向
        """
        resp = Response(code, [(b"Location", redirect_to.encode())])

        @self.web(network_path)
        async def _(scope, receive, send):
            resp.send_method = send
            await resp.send()

    def api(self, network_path: RouterPath, **kwargs):
        response = self.set_router(RouterPath(network_path))

        def decorator(function: Coroutine):
            async def warpper(scope, receive, send):
                return await function(scope, receive, send, **kwargs)

            response["/"] = warpper

        return decorator

    # def proxy(self, key: str, url: str):
    #     """
    #     代理
    #     """
    #     parsed_url = urllib.parse.urlparse(url)
    #     host = parsed_url.hostname
    #     port = parsed_url.port
    #     path = parsed_url.path

    #     def wrapper(handler: http.server.SimpleHTTPRequestHandler):
    #         conn = http.client.HTTPConnection(host, port)

    #         def request(network_path: str):
    #             conn.request(handler.command, network_path)
    #             resp = conn.getresponse()
    #             if resp.status == 301:
    #                 return request(resp.getheader("Location"))
    #             return resp

    #         resp = request(path)
    #         handler.send_response(resp.status)
    #         for header in resp.getheaders():
    #             handler.send_header(*header)
    #         handler.end_headers()
    #         handler.wfile.write(resp.read())
    #         conn.close()

    #     self.PROXY_DICT[key] = wrapper
