#!/usr/bin/env python3
import subprocess
import shlex
import os
import pyfiglet

def sql_injection():
    os.chdir("SQLI")
    os.system("clear")
    pyfiglet.print_figlet("SQLI")
    print("[+] Enter the URL of the vulnerable web application: ")
    url = input(">>> ")
    print("[+] Enter the vulnerable parameter: ")
    param = input(">>> ")
    print("[+] Enter encoding method (none, url, double, base64) [default: none]: ")
    encode = input(">>> ").strip() or "none"
    print("[+] Enter the value to test against [default: 1]: ")
    value = input(">>> ").strip() or "none"

    cmd = f"python3 sqli.py -u {url} -p {param} -e {encode} -v {value}"
    subprocess.run(shlex.split(cmd))
    os.chdir("..")

def ssti():
    os.chdir("SSTI")
    os.system("clear")
    pyfiglet.print_figlet("SSTI")
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
    os.system("clear")
    pyfiglet.print_figlet("LFI")
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
    print("Use php filter? (y/n) [default: n]: ")
    php_filter = input(">>> ").strip().lower() or "n"
    if php_filter == "y":
        php_filter = "--php-filter"
    else:
        php_filter = ""

    cmd = f"python3 lfi.py {url} {param} {lfi_payload} {method} --encode {encode} {php_filter}"
    subprocess.run(shlex.split(cmd))
    os.chdir("..")

def ssrf():
    os.chdir("SSRF")
    os.system("clear")
    pyfiglet.print_figlet("SSRF")
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

def buffer_overflow():
    os.chdir("Buffer-Overflow")
    os.system("clear")
    pyfiglet.print_figlet("Buffer Overflow")  # Fixed typo

    print("[+] Enter the IP address: ")
    ip = input(">>> ").strip()

    print("[+] Enter the port number: ")
    port_number = input(">>> ").strip()

    print("[+] Enter the path to the shellcode (default shellcode.bin): ")
    shellcode_path = input(">>> ").strip() or "shellcode.bin"

    print("[+] Enter the buffer size: ")
    buffer_size = input(">>> ").strip()

    print("[+] Enter the return address (hex, e.g. 0x7fffffffdbe0): ")
    return_address = input(">>> ").strip()

    print("[+] Enter the NOP sled size (default 128): ")
    nop_size = input(">>> ").strip() or "128"

    print("[+] Enter extra offset adjustment (default 0): ")
    extra_offset = input(">>> ").strip() or "0"

    print("[+] Enter bad chars to avoid (comma-separated hex, default 00,0a,0d): ")
    bad_chars = input(">>> ").strip() or "00,0a,0d"

    cmd = (
        f"python3 buffer_overflow.py "
        f"-H {ip} "
        f"-p {port_number} "
        f"-s {shellcode_path} "
        f"-b {buffer_size} "
        f"-r {return_address} "
        f"--nop-size {nop_size} "
        f"--extra-offset {extra_offset} "
        f"--bad-chars {bad_chars} "
        f"--send"
    )

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
    print("[+] Enter the HTTP method (GET or POST) [default: POST]: ")
    method = input(">>> ").strip().upper() or "POST"
    print("[+] Use PHP filter? (y/n): ")
    php_filter = "--php-filter" if input(">>> ").strip().lower() == "y" else ""

    cmd = f"python3 xxe.py {url} {file_path} --field {field} {php_filter}"
    subprocess.run(shlex.split(cmd))
    os.chdir("..")

def xss():
    os.chdir("XSS")
    os.system("clear")
    pyfiglet.print_figlet("XSS")
    print("[+] Enter the URL of the vulnerable web application: ")
    url = input(">>> ")
    print("[+] Enter the vulnerable parameter: ")
    param = input(">>> ")
    print("[+] Enter the HTTP method (GET or POST) [default: GET]: ")
    method = input(">>> ").strip().upper() or "GET"
    if method not in ["GET", "POST"]:
        print("[-] Invalid method, defaulting to GET")
        method = "GET"

    cmd = f"python3 xss.py {url} {param} --method {method}"
    subprocess.run(shlex.split(cmd), cwd="XSS")

def api_hack():
    os.chdir("API")
    os.system("clear")
    pyfiglet.print_figlet("API")
    print("1. Mass Assignment")
    print("2. BOLA/IDOR")
    print("3. JWT")
    print("4. Exit")
    choice = input(">>> ").strip()

    if choice == "1":
        os.system("clear")
        pyfiglet.print_figlet("Mass Assignment")
        os.chdir("Mass-Assignment")
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
        os.chdir("..")

    elif choice == "2":
        os.chdir("BOLA")
        os.system("clear")
        pyfiglet.print_figlet("BOLA")
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
        os.chdir("..")

    elif choice == "3":
        os.chdir("JWT")
        os.system("clear")
        pyfiglet.print_figlet("JWT")
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
        os.chdir("..")

    elif choice == "4":
        print("Back to the main menu")
        os.chdir("..")
        return

    else:
        print("[-] Invalid choice")

    os.chdir("..")

def fuzz():
    os.chdir("Fuzzer")
    os.system("clear")
    pyfiglet.print_figlet("Fuzzer")
    print("[+] Enter the URL to fuzz: ")
    url = input(">>> ")
    print("[+] Enter the number of steps (default 10): ")
    steps = input(">>> ")
    print("[+] Enter path to flow file (e.g. flows.json): ")
    flow = input(">>> ").strip()

    cmd = f"python3 fuzzer.py {url} --flow {flow}"
    subprocess.run(shlex.split(cmd))

def return_to_libc():
    os.system("clear")
    pyfiglet.print_figlet("ret2libc")

    print("[+] Enter the IP address: ")
    ip = input(">>> ").strip()

    print("[+] Enter the port number: ")
    port = input(">>> ").strip()

    print("[+] Enter the path to the target binary: ")
    elf = input(">>> ").strip()

    print("[+] Enter the buffer size: ")
    buffer_size = input(">>> ").strip()

    print("[+] Enter pop rdi ; ret gadget address (hex): ")
    pop_rdi = input(">>> ").strip()

    print("[+] Enter ret gadget address for alignment (hex): ")
    ret = input(">>> ").strip()

    print("[+] Enable dynamic mode for ASLR bypass? (y/n): ")
    dynamic = input(">>> ").strip().lower() == "y"

    if dynamic:
        print("[+] Enter path to libc.so.6: ")
        libc = input(">>> ").strip()
        print("[+] Enter puts@plt address (hex): ")
        puts_plt = input(">>> ").strip()
        print("[+] Enter puts@got address (hex): ")
        puts_got = input(">>> ").strip()
        print("[+] Enter main() address (hex): ")
        main_addr = input(">>> ").strip()
        print("[+] Enter string to recvuntil before payload: ")
        recv_until = input(">>> ").strip()
        print("[+] Enter string to send first (e.g. menu option): ")
        send_first = input(">>> ").strip()
        print("[+] Enter string to recvuntil before stage 2: ")
        stage2_until = input(">>> ").strip()

        cmd = (
            f"python3 ret2libc.py "
            f"-H {ip} "
            f"-p {port} "
            f"-e {elf} "
            f"-b {buffer_size} "
            f"--pop-rdi {pop_rdi} "
            f"--ret {ret} "
            f"--libc {libc} "
            f"--puts-plt {puts_plt} "
            f"--puts-got {puts_got} "
            f"--main {main_addr} "
            f"--recv-until '{recv_until}' "
            f"--send-first '{send_first}' "
            f"--stage2-until '{stage2_until}' "
            f"--dynamic "
            f"--send"
        )
    else:
        print("[+] Enter path to libc.so.6 (leave blank to provide addresses manually): ")
        libc = input(">>> ").strip()
        print("[+] Enter known libc base address (hex): ")
        libc_base = input(">>> ").strip()
        print("[+] Enter system() address (hex): ")
        system = input(">>> ").strip()
        print("[+] Enter /bin/sh address (hex): ")
        bin_sh = input(">>> ").strip()
        print("[+] Enter string to recvuntil before payload: ")
        recv_until = input(">>> ").strip()
        print("[+] Enter string to send first (e.g. menu option): ")
        send_first = input(">>> ").strip()

        libc_arg = f"--libc {libc}" if libc else ""

        cmd = (
            f"python3 ret2libc.py "
            f"-H {ip} "
            f"-p {port} "
            f"-e {elf} "
            f"-b {buffer_size} "
            f"--pop-rdi {pop_rdi} "
            f"--ret {ret} "
            f"{libc_arg} "
            f"--libc-base {libc_base} "
            f"--system {system} "
            f"--bin-sh {bin_sh} "
            f"--recv-until '{recv_until}' "
            f"--send-first '{send_first}' "
            f"--send"
        )

    subprocess.run(shlex.split(cmd))

def binary_exploitation():
    os.chdir("Binary-Exploitation")
    os.system("clear")
    pyfiglet.print_figlet("Binary Exploitation")

    print("1. Buffer Overflow")
    print("2. Return to libc")
    print("3. Back")
    choice = input(">>> ").strip()

    if choice == "1":
        buffer_overflow()
    elif choice == "2":
        return_to_libc()
    elif choice == "3":
        os.chdir("..")
        return
    else:
        print("[-] Invalid choice")
        os.chdir("..")
        return

    os.chdir("..")

def buffer_overflow():
    os.system("clear")
    pyfiglet.print_figlet("Buffer Overflow")
    print("[+] Enter the IP address: ")
    ip = input(">>> ").strip()

    print("[+] Enter the port number: ")
    port_number = input(">>> ").strip()

    print("[+] Enter the path to the shellcode (default shellcode.bin): ")
    shellcode_path = input(">>> ").strip() or "shellcode.bin"

    print("[+] Enter the buffer size: ")
    buffer_size = input(">>> ").strip()

    print("[+] Enter the return address (hex, e.g. 0x7fffffffdbe0): ")
    return_address = input(">>> ").strip()

    print("[+] Enter the NOP sled size (default 128): ")
    nop_size = input(">>> ").strip() or "128"

    print("[+] Enter extra offset adjustment (default 0): ")
    extra_offset = input(">>> ").strip() or "0"

    print("[+] Enter bad chars to avoid (comma-separated hex, default 00,0a,0d): ")
    bad_chars = input(">>> ").strip() or "00,0a,0d"

    cmd = (
        f"python3 buffer_overflow.py "
        f"-H {ip} "
        f"-p {port_number} "
        f"-s {shellcode_path} "
        f"-b {buffer_size} "
        f"-r {return_address} "
        f"--nop-size {nop_size} "
        f"--extra-offset {extra_offset} "
        f"--bad-chars {bad_chars} "
        f"--send"
    )

    subprocess.run(shlex.split(cmd))

def main():
    ascii_banner = pyfiglet.figlet_format("Fang")
    print(ascii_banner)
    while True:
        print("1. SQL Injection")
        print("2. Server-Side Template Injection")
        print("3. Local File Inclusion")
        print("4. Server-Side Request Forgery")
        print("5. XML External Entity Injection")
        print("6. XSS")
        print("7. API Pentesting Toolkit")
        print("8. Fuzzer")
        print("9. Binary Exploitation")
        print("10. Exit")
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
            xss()
        elif choice == "7":
            api_hack()
        elif choice == "8":
            fuzz()
        elif choice == "9":
            binary_exploitation()
        elif choice == "10":
            print("Goodbye!")
            break
        else:
            print("[-] Invalid choice")

if __name__ == "__main__":
    main()