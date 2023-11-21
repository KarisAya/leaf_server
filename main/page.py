from lika.response import Response, Headers
from lika.router import RouterPath
from lika.server import RouterMap


def listing(server: RouterMap, network_path: RouterPath, src_path: RouterPath):
    """
    展示网络资源
        network_path:网络位置
        src_path:网络资源路径
    """
    network_path = RouterPath(network_path)
    src_path = RouterPath(src_path)
    return_map = RouterMap()

    def _func(src_path: RouterPath):
        sub_map = server.get_map(src_path)
        if sub_map is None or sub_map.is_file:
            return
        body = []
        for src_sp in sub_map:
            src_sp = src_path + [src_sp]
            if server.get_map(src_sp).is_file:
                network_sp = src_sp
            else:
                _func(src_sp)
                network_sp = network_path + src_sp
            body.append(f'<li><a href="{network_sp.url}">{src_sp.name}</a></li>')
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
            <h1>Directory listing for {src_path.path}</h1>
            <hr>
            <ul>{body}</ul>
        </body>
        </html>
        """
        content = content.encode()
        return_map.set_map(
            src_path,
            RouterMap(True, Response(200, Headers.from_ext("html"), [content])),
        )

    _func(src_path)
    server.set_map(network_path, return_map.get_map(src_path))
