# Fuzzer/utils.py
import requests
import random
import string

def random_string(length=8):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

def send_request(session, base_url, req):
    try:
        return session.request(
            method=req["method"],
            url=base_url + req["endpoint"],
            json=req.get("json"),
            headers=req.get("headers", {})
        )
    except requests.exceptions.RequestException as e:
        print(f"[!] Request error: {e}")
        return None