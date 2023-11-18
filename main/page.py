from lika.response import Response, Headers
from lika.router import RouterPath
from lika.server import ResponseMap, Server


def listing(server: Server, network_path: RouterPath, src_path: RouterPath):
    """
    展示网络资源
        network_path:网络位置
        src_path:网络资源路径
    """
    network_path = RouterPath(network_path)
    src_path = RouterPath(src_path)
    response = ResponseMap()

    def _listing(src_path: RouterPath):
        def _dir_list(src_path: RouterPath):
            body = []
            for src_sp in server.get_router(src_path).keys():
                if src_sp == "/":
                    continue
                src_sp = src_path + [src_sp]
                inner_resp = server.set_router(src_sp)
                if inner_resp and inner_resp.is_dir():
                    src_sp = network_path + src_sp
                body.append(f'<li><a href="{src_sp.url}">{src_sp.name}</a></li>')
            body = "\n".join(body)
            content = f"""
            <!DOCTYPE html>
            <html lang="cn">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{src_path.name}</title>
            </head>
            <body>
                <h1>Directory listing for {src_path.url}</h1>
                <hr>
                <ul>{body}</ul>
            </body>
            </html>
            """
            content = content.encode()
            resp = Response(200, [(b"Content-type", b"text/html")], [content])

            async def func(scope, receive, send):
                resp.send_method = send
                await resp.send()

            return func

        resp_map = server.get_router(src_path)
        if resp_map is None or resp_map.is_file():
            return
        inner_resp = response.set_router(src_path)
        inner_resp["/"] = _dir_list(src_path)
        for src_sp in resp_map:
            if src_sp == "/":
                continue
            _listing(src_path + [src_sp])

    _listing(src_path)
    server.set_router(network_path).set_map(response)
