import requests
import json
import time

t = 0
IPv6 = None


def get_my_IPv6():
    now = time.time()
    global IPv6
    if IPv6 is None or now - t > 360:
        IPv6 = my_IPv6()
    return IPv6


def my_IPv6() -> str:
    try:
        resp = requests.get(r"https://ipv6.jp2.test-ipv6.com/ip/?callback=?")
    except:
        return "::1"
    resp = "".join(x for x in resp.text if x.isprintable())
    start = resp.find("{")
    end = resp.rfind("}") + 1
    return json.loads(resp[start:end])["ip"]


def resp_302():
    addr = f"http://[{my_IPv6()}]:{8888}/"
    print(f"重定向已更新:{addr}")
    return f"HTTP/1.1 302 Moved Permanently\r\nLocation: {addr}\r\n".encode()
