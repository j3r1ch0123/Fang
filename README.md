# Fang 🐍
A modular black box penetration testing toolkit for identifying and validating common web application vulnerabilities. Built for bug bounty hunting and responsible disclosure.

> **Disclaimer:** This tool is intended for authorized penetration testing and security research only. Only use Fang against systems you own or have explicit written permission to test. Unauthorized use is illegal and unethical.

---

## Features

**Web Application Modules**
- **SQL Injection** — Boolean-based and time-based blind SQLi detection
- **Server-Side Template Injection (SSTI)** — Auto-detects engine (Jinja2, Tornado, Django, ERB, Twig) and drops into an interactive shell
- **Local File Inclusion (LFI)** — File read, PHP filter base64 decode, SSH log poisoning, secrets scanning, Tor support
- **Server-Side Request Forgery (SSRF)** — Callback-based detection with normal, decimal, and hex IP encoding modes
- **XML External Entity (XXE)** — File read via external entities, PHP filter support, auto-detection with common payloads
- **Cross-Site Scripting (XSS)** — Reflection detection, context-aware payload selection (HTML, attribute, unknown)

**API Pentesting Toolkit**
- **Mass Assignment** — Fuzzes registration/update endpoints for privilege field injection
- **BOLA/IDOR** — Path-based and parameter-based object-level authorization testing
- **JWT Weakness Detection** — Tests for alg:none, weak secrets, and algorithm confusion attacks

**Binary Exploitation**
- **Buffer Overflow** — Parameterized stack-based buffer overflow exploit with NOP sled, bad char detection, and dry run mode
- **ret2libc** — ROP-based ret2libc exploit with static and dynamic (ASLR bypass) modes

**Fuzzer**
- **State Fuzzer** — HTTP flow fuzzer that tests step skipping and step reordering to detect broken state logic

---

## Installation

```bash
git clone https://github.com/j3r1ch0123/Fang.git
cd Fang
pip install -r requirements.txt
```

### Dependencies

```
requests
paramiko
pyfiglet
urllib3
pwntools
```

---

## Usage

Run the main menu:

```bash
python3 fang.py
```

You'll be prompted to select a module and enter the target details interactively.

---

## Web Application Modules

### SQL Injection (`SQLI/sqli.py`)

Detects boolean-based and time-based blind SQL injection.

```bash
python3 sqli.py -u <URL> -p <PARAMETER> [-e <ENCODING>] [-v <VALUE>]
```

| Argument | Description |
|---|---|
| `-u` | Target URL |
| `-p` | Vulnerable parameter name |
| `-e` | Encoding: `none`, `url`, `double`, `base64`, `all` |
| `-v` | Base parameter value to prepend to payloads (default: `1`) |

---

### SSTI (`SSTI/ssti.py`)

Detects and exploits server-side template injection. Auto-identifies the template engine and opens an interactive shell for command execution.

```bash
python3 ssti.py <URL> <PARAMETER> [--login] [--username USER] [--password PASS] [--engine ENGINE] [--method GET|POST] [--encode none|url|double]
```

| Argument | Description |
|---|---|
| `url` | Target base URL |
| `parameter` | Injectable parameter |
| `--login` | Authenticate before testing |
| `--engine` | Force engine: `jinja2`, `tornado`, `django` |
| `--method` | HTTP method (default: GET) |
| `--encode` | Encoding method |

---

### LFI (`LFI/lfi.py`)

Tests for local file inclusion vulnerabilities with multiple encoding bypass techniques and log poisoning support.

```bash
python3 lfi.py <URL> <PARAM> <PAYLOAD> [--method GET|POST] [--encode ENCODING] [--php-filter] [--ssh] [--secrets] [--tor]
```

| Argument | Description |
|---|---|
| `url` | Target URL |
| `param` | Vulnerable parameter |
| `lfi_payload` | File path to include (e.g. `/etc/passwd`) |
| `--method` | HTTP method (default: GET) |
| `--encode` | Encoding: `none`, `url`, `double`, `base64`, `traversal`, `double_traversal`, `nullbyte`, `all` |
| `--php-filter` | Use PHP filter wrapper to base64-decode source |
| `--ssh` | Perform SSH log poisoning |
| `--secrets` | Scan included file for secrets/credentials |
| `--outfile` | Output file for found secrets (default: `secrets.txt`) |
| `--tor` | Route traffic through Tor |
| `--cookie` | PHPSESSID cookie for authenticated testing |

---

### SSRF (`SSRF/ssrf.py`)

Detects server-side request forgery using a local callback listener with a unique token.

```bash
python3 ssrf.py <URL> <PARAM> <PUBLIC_IP> <PORT> [-e ENCODING] [-m MODE]
```

| Argument | Description |
|---|---|
| `url` | Target URL |
| `param` | Vulnerable parameter |
| `public_ip` | Your public IP for the callback |
| `port` | Port to listen on |
| `-e` | Encoding: `none`, `url`, `double` |
| `-m` | IP mode: `normal`, `decimal`, `hex` |

---

### XXE (`XXE/xxe.py`)

Tests for XML external entity injection. Supports plain file read and PHP filter base64 extraction.

```bash
python3 xxe.py <URL> [FILE_PATH] [--field FIELD] [--php-filter] [--detect] [--tor] [--outfile FILE]
```

| Argument | Description |
|---|---|
| `url` | Target URL |
| `file_path` | File to read (default: `/etc/passwd`) |
| `--field` | XML field to inject into (default: `email`) |
| `--php-filter` | Use PHP filter base64 wrapper |
| `--detect` | Auto-detect XXE with common file payloads |
| `--tor` | Route traffic through Tor |
| `--outfile` | Save output to file |

---

### XSS (`XSS/xss.py`)

Tests for reflected cross-site scripting. Detects reflection, identifies injection context, and selects payloads accordingly.

```bash
python3 xss.py <URL> <PARAM> [--method GET|POST]
```

| Argument | Description |
|---|---|
| `url` | Target URL |
| `param` | Parameter to test |
| `--method` | HTTP method (default: GET) |

**How it works:**
1. Sends a unique marker to detect reflection
2. Identifies the injection context (HTML body, attribute, or unknown)
3. Tests context-appropriate payloads and reports any that are reflected unescaped

---

## API Pentesting Toolkit

### Mass Assignment (`API/mass_assignment.py`)

Fuzzes API registration and update endpoints for privilege field injection vulnerabilities.

```bash
python3 mass_assignment.py <URL> <ENDPOINT> <USERNAME> <PASSWORD> [--fields FIELDS] [--tor] [--outfile FILE]
```

| Argument | Description |
|---|---|
| `url` | Base URL of the target |
| `endpoint` | Registration or update endpoint |
| `username` | Username to register |
| `password` | Password to register |
| `--fields` | Custom fields to test (space-separated) |
| `--tor` | Route traffic through Tor |
| `--outfile` | Save results to file |

---

### BOLA/IDOR (`API/BOLA/bola.py`)

Tests for broken object level authorization via path-based ID iteration or parameter substitution.

```bash
python3 bola.py <URL> [--token TOKEN] [--range N] [--param PARAM] [--own-id ID] [--test-id ID] [--method GET|POST] [--tor] [--outfile FILE]
```

| Argument | Description |
|---|---|
| `url` | Target API endpoint |
| `--token` | Bearer token for authenticated requests |
| `--range` | Number of IDs to iterate (default: 5) |
| `--param` | Parameter name for parameter-based IDOR |
| `--own-id` | Your own user ID |
| `--test-id` | Target user ID to test |
| `--method` | HTTP method (default: GET) |
| `--tor` | Route traffic through Tor |
| `--outfile` | Save results to file |

---

### JWT Weakness Detection (`API/JWT/jwt.py`)

Tests JWT tokens for common weaknesses including alg:none, weak secrets, and algorithm confusion.

```bash
python3 jwt.py <TOKEN> [--url URL] [--header HEADER] [--alg-none] [--weak-secret] [--alg-confusion] [--public-key KEY] [--wordlist FILE] [--all] [--tor] [--outfile FILE]
```

| Argument | Description |
|---|---|
| `token` | JWT token to test |
| `--url` | Target URL to send forged tokens to |
| `--header` | Header name (default: `Authorization`) |
| `--alg-none` | Test alg:none attack |
| `--weak-secret` | Brute force weak HMAC secret |
| `--alg-confusion` | Test RS256 → HS256 algorithm confusion |
| `--public-key` | Public key for algorithm confusion attack |
| `--wordlist` | Custom wordlist for secret brute force |
| `--all` | Run all applicable tests |
| `--tor` | Route traffic through Tor |
| `--outfile` | Save results to file |

---

## Binary Exploitation

### Buffer Overflow (`Binary-Exploitation/buffer_overflow.py`)

Parameterized stack-based buffer overflow exploit module. Builds and delivers a payload with configurable NOP sled, bad char detection, and dry run mode. Supports raw shellcode binaries generated with NASM or msfvenom.

```bash
python3 buffer_overflow.py -H <HOST> -p <PORT> -s <SHELLCODE> -b <BUFFER_SIZE> -r <RET_ADDR> [OPTIONS]
```

| Argument | Description |
|---|---|
| `-H`, `--host` | Target IP or hostname |
| `-p`, `--port` | Target port |
| `-s`, `--shellcode` | Path to raw shellcode binary (default: `shellcode.bin`) |
| `-b`, `--buffer-size` | Vulnerable buffer size in bytes |
| `-r`, `--ret-addr` | Return address in hex (e.g. `0x7fffffffdb90`) |
| `--nop-size` | NOP sled size in bytes (default: 128) |
| `--rbp-size` | Saved RBP size (default: 8) |
| `--extra-offset` | Extra padding adjustment for fine-tuning (default: 0) |
| `--bad-chars` | Comma-separated bad chars to check (default: `00,0a,0d`) |
| `--send` | Actually send the payload — omit for dry run |
| `--timeout` | Socket timeout in seconds (default: 5) |

**Payload layout:**
```
[ padding ] [ saved RBP ] [ RIP ] [ NOP sled ] [ shellcode ]
```

**Workflow:**
1. Find the buffer size and return address using GDB/GEF
2. Generate shellcode with NASM or msfvenom
3. Dry run first to verify layout and check for bad chars
4. Send the payload with `--send`

```bash
# Dry run
python3 buffer_overflow.py -H 127.0.0.1 -p 4444 \
  -s revshell.bin -b 64 -r 0x7fffffffdb90

# Fire
python3 buffer_overflow.py -H 127.0.0.1 -p 4444 \
  -s revshell.bin -b 64 -r 0x7fffffffdb90 --send

# Custom NOP sled and bad chars
python3 buffer_overflow.py -H 127.0.0.1 -p 4444 \
  -s revshell.bin -b 64 -r 0x7fffffffdb90 \
  --nop-size 256 --bad-chars "00,0a,0d,20" --send
```

---

### ret2libc (`Binary-Exploitation/ret2libc.py`)

ROP-based ret2libc exploit module. Supports both static mode (ASLR off) with known addresses and dynamic mode (ASLR on) with libc leak via puts@plt. Requires pwntools.

```bash
python3 ret2libc.py -H <HOST> -p <PORT> -b <BUFFER_SIZE> -e <ELF> --pop-rdi <ADDR> --ret <ADDR> [OPTIONS]
```

**Required arguments:**

| Argument | Description |
|---|---|
| `-H`, `--host` | Target IP or hostname |
| `-p`, `--port` | Target port |
| `-b`, `--buffer-size` | Buffer size in bytes |
| `-e`, `--elf` | Path to target binary |
| `--pop-rdi` | `pop rdi ; ret` gadget address (hex) |
| `--ret` | `ret` gadget address for stack alignment (hex) |

**Static mode (ASLR off):**

| Argument | Description |
|---|---|
| `--libc-base` | Known libc base address (hex) |
| `--system` | Known `system()` address (hex) |
| `--bin-sh` | Known `/bin/sh` address (hex) |

**Dynamic mode (ASLR on):**

| Argument | Description |
|---|---|
| `--dynamic` | Enable ASLR bypass via libc leak |
| `--libc` | Path to `libc.so.6` |
| `--puts-plt` | `puts@plt` address (hex) |
| `--puts-got` | `puts@got` address (hex) |
| `--main` | `main()` address to return to after leak (hex) |

**Protocol options:**

| Argument | Description |
|---|---|
| `--recv-until` | String to `recvuntil` before sending payload |
| `--send-first` | String to send before payload (e.g. menu option) |
| `--stage2-until` | String to `recvuntil` before stage 2 payload |
| `--rbp-size` | Saved RBP size (default: 8) |
| `--send` | Send payload — omit for dry run |
| `--timeout` | Socket timeout in seconds (default: 5) |

**Workflow:**
1. Find buffer size and gadgets using `ROPgadget` or `ropper`
2. For dynamic mode, locate `puts@plt`, `puts@got`, and `main()` in the binary
3. Provide `libc.so.6` for offset calculations
4. Dry run first, then `--send`

```bash
# Static mode
python3 ret2libc.py -H 127.0.0.1 -p 4444 \
  -b 64 -e ./vuln \
  --pop-rdi 0x401234 --ret 0x401235 \
  --libc-base 0x7ffff7dc0000 \
  --system 0x7ffff7e13290 \
  --bin-sh 0x7ffff7f7a152 \
  --send

# Dynamic mode (ASLR bypass)
python3 ret2libc.py -H 127.0.0.1 -p 4444 \
  -b 64 -e ./vuln --libc /lib/x86_64-linux-gnu/libc.so.6 \
  --pop-rdi 0x401234 --ret 0x401235 \
  --puts-plt 0x401090 --puts-got 0x404018 \
  --main 0x401156 \
  --dynamic --send
```

---

## Fuzzer

### State Fuzzer (`Fuzzer/state_fuzzer.py`)

Tests multi-step HTTP flows for broken state logic by detecting behavior changes when steps are skipped or reordered. Useful for finding authentication bypass and business logic vulnerabilities.

```bash
python3 state_fuzzer.py <URL> [--steps N] [--flow FILE]
```

| Argument | Description |
|---|---|
| `url` | Base URL to fuzz |
| `--steps` | Number of random steps to generate (default: 10) |
| `--flow` | Path to a JSON file defining the steps to fuzz |

**Flow file format (`flows.json`):**
```json
[
    {"name": "register", "request": {"method": "POST", "endpoint": "/register"}},
    {"name": "login",    "request": {"method": "POST", "endpoint": "/login"}},
    {"name": "profile",  "request": {"method": "GET",  "endpoint": "/profile"}}
]
```

```bash
# Random steps
python3 state_fuzzer.py http://target.com --steps 5

# Custom flow
python3 state_fuzzer.py http://target.com --flow flows.json
```

---

## Examples

```bash
# SQLi with URL encoding and base value
python3 sqli.py -u http://target.com/item -p id -e url -v 1

# SSTI with login
python3 ssti.py http://target.com/ name --login --username admin --password admin

# LFI with PHP filter
python3 lfi.py http://target.com/page.php file /etc/passwd --php-filter

# SSRF
python3 ssrf.py http://target.com/fetch url 1.2.3.4 8080

# XXE auto-detect
python3 xxe.py http://target.com/api/upload --detect

# XSS
python3 xss.py http://target.com/search q --method GET

# Mass assignment
python3 mass_assignment.py http://target.com/ api/register user pass

# BOLA/IDOR
python3 bola.py http://target.com/api/users --token eyJ... --range 10

# JWT all tests
python3 jwt.py eyJ... --url http://target.com/api/profile --all

# Buffer overflow dry run
python3 buffer_overflow.py -H 192.168.1.10 -p 4444 -s revshell.bin -b 64 -r 0x7fffffffdb90

# Buffer overflow fire
python3 buffer_overflow.py -H 192.168.1.10 -p 4444 -s revshell.bin -b 64 -r 0x7fffffffdb90 --send

# ret2libc dynamic mode
python3 ret2libc.py -H 192.168.1.10 -p 4444 -b 64 -e ./vuln \
  --libc /lib/x86_64-linux-gnu/libc.so.6 \
  --pop-rdi 0x401234 --ret 0x401235 \
  --puts-plt 0x401090 --puts-got 0x404018 \
  --main 0x401156 --dynamic --send

# State fuzzer with flow file
python3 state_fuzzer.py http://target.com --flow flows.json
```

---

## License

MIT License — see `LICENSE` for details.
