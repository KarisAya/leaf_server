from typing import Coroutine, Tuple, List

Headers = List[Tuple[bytes, bytes]]

Bodys = List[bytes]


class Response:
    def __init__(
        self,
        code: int = 200,
        headers: Headers = [],
        bodys: Bodys = [b""],
        send_method: Coroutine = None,
    ):
        self._send = send_method
        self.bodys = [
            {
                "type": "http.response.body",
                "body": body,
                "more_body": True,
            }
            for body in bodys
        ]
        self.bodys[-1]["more_body"] = False
        headers.append((b"Content-Length", str(sum(map(len, bodys)))))
        self.start = {
            "type": "http.response.start",
            "status": code,
            "headers": headers,
        }

    @property
    def send_method(self):
        return self._send

    @send_method.setter
    def send_method(self, send_method: Coroutine):
        self._send = send_method

    async def send(self):
        await self._send(self.start)
        for body in self.bodys:
            await self._send(body)
