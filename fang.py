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

    cmd = f"python3 lfi.py {url} {param} {lfi_payload} {method} --encode {encode}"
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

def xxe():
    os.chdir("XXE")
    print("[+] Enter the URL of the vulnerable web application: ")
    url = input(">>> ")
    print("[+] Enter the file to read [default: /etc/passwd]: ")
    file_path = input(">>> ").strip() or "/etc/passwd"
    print("[+] Enter the XML field name [default: email]: ")
    field = input(">>> ").strip() or "email"
    print("[+] Use PHP filter? (y/n): ")
    php_filter = "--php-filter" if input(">>> ").strip().lower() == "y" else ""

    cmd = f"python3 xxe.py {url} {file_path} --field {field} {php_filter}"
    subprocess.run(shlex.split(cmd))
    os.chdir("..")

def api_hack():
    os.chdir("API")
    print("1. Mass Assignment")
    print("2. BOLA/IDOR")
    print("3. JWT")
    print("4. Exit")
    choice = input(">>> ").strip()

    if choice == "1":
        print("[+] Enter the base URL of the vulnerable API: ")
        url = input(">>> ")
        print("[+] Enter the registration endpoint (e.g. api/register): ")
        endpoint = input(">>> ")
        print("[+] Enter the username: ")
        username = input(">>> ")
        print("[+] Enter the password: ")
        password = input(">>> ")
        print("[+] Enter fields to test (comma-separated) [leave blank for all]: ")
        fields_input = input(">>> ").strip()
        fields = fields_input.split(",") if fields_input else None
        print("[+] Use Tor? (y/n): ")
        tor = "--tor" if input(">>> ").strip().lower() == "y" else ""
        print("[+] Save results to file? Enter filename or leave blank to skip: ")
        outfile_input = input(">>> ").strip()
        outfile = f"--outfile {outfile_input}" if outfile_input else ""

        fields_arg = f"--fields {' '.join(fields)}" if fields else ""
        cmd = f"python3 mass_assignment.py {url} {endpoint} {username} {password} {fields_arg} {tor} {outfile}"
        subprocess.run(shlex.split(cmd))

    elif choice == "2":
        print("[+] Enter the target API endpoint (e.g. http://target.com/api/users): ")
        url = input(">>> ")
        print("[+] Enter Bearer token (leave blank if none): ")
        token_input = input(">>> ").strip()
        token = f"--token {token_input}" if token_input else ""
        print("[+] How many IDs to test? [default: 5]: ")
        id_range_input = input(">>> ").strip()
        id_range = f"--range {id_range_input}" if id_range_input else ""
        print("[+] Use Tor? (y/n): ")
        tor = "--tor" if input(">>> ").strip().lower() == "y" else ""
        print("[+] Save results to file? Enter filename or leave blank to skip: ")
        outfile_input = input(">>> ").strip()
        outfile = f"--outfile {outfile_input}" if outfile_input else ""

        cmd = f"python3 bola.py {url} {token} {id_range} {tor} {outfile}"
        subprocess.run(shlex.split(cmd))

    elif choice == "3":
        print("[+] Enter the target API endpoint: ")
        url = input(">>> ")
        print("[+] Enter JWT token: ")
        token_input = input(">>> ").strip()
        print("[+] Use a wordlist? (y/n): ")
        wordlist = ""
        if input(">>> ").strip().lower() == "y":
            print("[+] Enter path to wordlist: ")
            wordlist = f"--wordlist {input('>>> ').strip()}"
        print("[+] Save results to file? Enter filename or leave blank to skip: ")
        outfile_input = input(">>> ").strip()
        outfile = f"--outfile {outfile_input}" if outfile_input else ""

        cmd = f"python3 jwt.py {token_input} --url {url} --all {wordlist} {outfile}"
        subprocess.run(shlex.split(cmd))
    
    elif choice == "4":
        print("Back to the main menu")
        os.chdir("..")
        return

    else:
        print("[-] Invalid choice")

    os.chdir("..")

def main():
    ascii_banner = pyfiglet.figlet_format("Fang")
    print(ascii_banner)
    while True:
        print("1. SQL Injection")
        print("2. Server-Side Template Injection")
        print("3. Local File Inclusion")
        print("4. Server-Side Request Forgery")
        print("5. XML External Entity Injection")
        print("6. API Pentesting Toolkit")
        print("7. Exit")
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
            xxe()
        elif choice == "6":
            api_hack()
        elif choice == "7":
            print("Exiting...")
            sys.exit(0)
        else:
            print("[-] Invalid choice")

if __name__ == "__main__":
    main()
