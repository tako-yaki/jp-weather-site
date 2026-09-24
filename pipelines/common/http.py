"""シンプルなJSON取得ヘルパー。"""
import json
import urllib.request

USER_AGENT = "weather-site-dev/0.1 (local pipeline)"


def fetch_json(url: str, timeout: int = 10):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.load(res)
