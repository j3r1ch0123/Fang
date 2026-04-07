# Fuzzer/state_fuzzer.py
import argparse
import requests
import json
from utils import random_string, send_request

class StateFuzzer:
    def __init__(self, session, base_url):
        self.s = session
        self.base_url = base_url

    def run_flow(self, steps):
        results = {}
        for step in steps:
            r = send_request(self.s, self.base_url, step["request"])
            results[step["name"]] = r.status_code
        return results

    def fuzz(self, steps):
        print("[*] Running normal flow...")
        baseline = self.run_flow(steps)

        print("[*] Testing step skipping...")
        for i in range(len(steps)):
            test_steps = steps[:i] + steps[i+1:]
            result = self.run_flow(test_steps)
            if result != baseline:
                print(f"[!] Behavior changed when skipping {steps[i]['name']}")

        print("[*] Testing step reordering...")
        for i in range(len(steps)-1):
            swapped = steps[:]
            swapped[i], swapped[i+1] = swapped[i+1], swapped[i]
            result = self.run_flow(swapped)
            if result != baseline:
                print(f"[!] Order manipulation detected between {steps[i]['name']} and {steps[i+1]['name']}")

def load_flow(path):
    try:
        with open(path, "r") as f:
            steps = json.load(f)
        print(f"[*] Loaded {len(steps)} steps from {path}")
        return steps
    except FileNotFoundError:
        print(f"[!] Flow file not found: {path}")
        return None
    except json.JSONDecodeError as e:
        print(f"[!] Invalid JSON in flow file: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL to fuzz")
    parser.add_argument("--steps", type=int, default=10, help="Number of random steps to generate")
    parser.add_argument("--flow", help="Path to a JSON file defining the steps to fuzz")
    args = parser.parse_args()

    session = requests.Session()

    if args.flow:
        steps = load_flow(args.flow)
        if not steps:
            return
    else:
        steps = [
            {"name": random_string(), "request": {"method": "GET", "endpoint": "/"}}
            for _ in range(args.steps)
        ]

    fuzzer = StateFuzzer(session, args.url)
    fuzzer.fuzz(steps)

if __name__ == "__main__":
    main()
