"""Token-independent JSON HTTP client used only during explicit setup."""
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
API = "https://tonapi.io/v2"

def fetch(path, attempts=3, *, api=API):
    for attempt in range(attempts):
        try:
            request = Request(api + path, headers={"Accept": "application/json", "User-Agent": "TON-Observatory-Factory/1.2"})
            with urlopen(request, timeout=20) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError, ConnectionError) as error:
            if isinstance(error, HTTPError) and error.code not in (408, 429, 500, 502, 503, 504):
                raise
            if attempt + 1 == attempts:
                raise
            time.sleep(2 ** (attempt + 1))
