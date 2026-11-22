import httpx2
import os

PROXY_URL = os.getenv(
    "PLAY_URL",
    "http://host.containers.internal:3000/api/proxy?url=https%3A%2F%2Fvip.ffzy-play9.com%2F20221112%2F3355_328c86a9%2Findex.m3u8",
)
COOKIES = "auth=%257B%2522role%2522%253A%2522admin%2522%252C%2522username%2522%253A%2522moon%2522%252C%2522signature%2522%253A%2522d702ee2cf9088db1ff137a7785988b08a25e3ab8bfea57f1cfe642956281f574%2522%252C%2522timestamp%2522%253A1793795086368%257D"

headers = {
    "User-Agent": "AptvPlayer/1.4.10",
    "Cookie": COOKIES,
    "Accept": "*/*",
    "Referer": "https://vip.ffzy-play9.com/",
}

try:
    with httpx2.Client(verify=False, timeout=15.0, follow_redirects=True) as client:
        r = client.get(PROXY_URL, headers=headers)
        print("status:", r.status_code)
        print("content-type:", r.headers.get("content-type"))
        print(r.text[:200])
except Exception as e:
    print("error:", repr(e))
