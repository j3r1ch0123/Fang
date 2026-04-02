# Fang 🐍
A modular web application penetration testing framework for identifying and validating common vulnerabilities.

> **Disclaimer:** This tool is intended for authorized penetration testing and security research only. Only use Fang against systems you own or have explicit written permission to test. Unauthorized use is illegal and unethical.

---

## Features

- **SQL Injection** — Boolean-based and time-based blind SQLi detection
- **Server-Side Template Injection (SSTI)** — Auto-detects engine (Jinja2, Tornado, Django, ERB, Twig) and drops into an interactive shell
- **Local File Inclusion (LFI)** — File read, PHP filter base64 decode, SSH log poisoning, secrets scanning, Tor support
- **Server-Side Request Forgery (SSRF)** — Callback-based detection with normal, decimal, and hex IP encoding modes

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
```

---

## Usage

Run the main menu:

```bash
python3 fang.py
```

You'll be prompted to select a module and enter the target details interactively.

---

## Modules

### SQL Injection (`SQLI/sqli.py`)

Detects boolean-based and time-based blind SQL injection.

```bash
python3 sqli.py -u <URL> -p <PARAMETER> [-e <ENCODING>]
```

| Argument | Description |
|---|---|
| `-u` | Target URL |
| `-p` | Vulnerable parameter name |
| `-e` | Encoding: `none`, `url`, `double`, `base64`, `all` |

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

## Example

```bash
# Test for SSRF
python3 ssrf.py http://target.com/fetch url 1.2.3.4 8080

# Test for SSTI with login
python3 ssti.py http://target.com/ name --login --username admin --password admin

# LFI with PHP filter
python3 lfi.py http://target.com/page.php file /etc/passwd --php-filter

# SQLi with URL encoding
python3 sqli.py -u http://target.com/item -p id -e url
```

---

## License

MIT License — see `LICENSE` for details.
