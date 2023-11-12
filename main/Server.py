from typing import Callable


class Server:
    WEB_DICT = {}

    def add_page(self, path: str, header: tuple = ("Content-type", "text/html")):
        def decorator(function: Callable):
            def wapper(handler):
                handler.send_response(200)
                handler.send_header(*header)
                handler.end_headers()
                return function(handler)

            self.WEB_DICT[path] = wapper

        return decorator

    def redirect(self, status: int, path: str, url: str):
        def wapper(handler):
            handler.send_response(status)
            handler.send_header("Location", url)
            handler.end_headers()

        self.WEB_DICT[path] = wapper
