import shlex
import json
from urllib.parse import urlparse

def parse_curl_file(path="curl.txt"):
    with open(path, "r", encoding="utf-8") as f:
        curl_command = f.read()

    parts = shlex.split(curl_command)

    url = None
    headers = {}
    cookies = {}
    data = None
    method = "GET"

    i = 0
    while i < len(parts):
        part = parts[i]

        if part.startswith("http"):
            url = part

        elif part in ("-X", "--request"):
            method = parts[i + 1]
            i += 1

        elif part in ("-H", "--header"):
            header = parts[i + 1]
            key, value = header.split(":", 1)
            headers[key.strip()] = value.strip()
            i += 1

        elif part in ("--data", "--data-raw", "--data-binary"):
            data = parts[i + 1]
            i += 1

        i += 1

    # извлекаем cookies из headers
    if "Cookie" in headers:
        raw_cookies = headers.pop("Cookie")
        for item in raw_cookies.split(";"):
            if "=" in item:
                k, v = item.strip().split("=", 1)
                cookies[k] = v

    # JSON body
    json_body = None
    # Было:
    if data:
        try:
            json_body = json.loads(data)
        except json.JSONDecodeError:
            json_body = data

    return {
        "method": method,
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "json": json_body
    }

    