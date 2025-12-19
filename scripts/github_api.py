import requests

BASE_URL = "https://api.github.com"

def gh(method, url, token, json=None):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    r = requests.request(method, url, headers=headers, json=json)

    if r.status_code >= 400:
        raise RuntimeError(f"{r.status_code}: {r.text}")

    return r.json() if r.text else None
