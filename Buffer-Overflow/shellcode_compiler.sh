#!/bin/bash

echo "Enter the path to the assembly code: "
read assembly

echo "Enter the name of the shellcode: "
read shellcode

# Validate inputs
if [ ! -f "$assembly" ]; then
    echo "[!] File not found: $assembly"
    exit 1
fi

if [ -z "$shellcode" ]; then
    echo "[!] No shellcode name provided"
    exit 1
fi

echo "[+] Assembling $assembly..."
nasm -f elf64 "$assembly" -o "$shellcode.o"
if [ $? -ne 0 ]; then
    echo "[!] NASM failed"
    exit 1
fi

echo "[+] Linking..."
ld -o "$shellcode" "$shellcode.o"
if [ $? -ne 0 ]; then
    echo "[!] Linking failed"
    exit 1
fi

echo "[+] Extracting binary..."
objcopy -O binary --only-section=.text "$shellcode" "$shellcode.bin"
if [ $? -ne 0 ]; then
    echo "[!] objcopy failed"
    exit 1
fi

# Cleanup intermediate files
rm -f "$shellcode.o" "$shellcode"

echo "[+] Done — $shellcode.bin"
echo "[+] Size: $(wc -c < "$shellcode.bin") bytes"

echo "[+] Bad char check (\\x00 \\x0a \\x0d):"
python3 -c "
data = open('$shellcode.bin', 'rb').read()
bad = [0x00, 0x0a, 0x0d]
found = [(i, b) for i, b in enumerate(data) if b in bad]
for i, b in found:
    print(f'  [!] 0x{b:02x} at offset {i}')
if not found:
    print('  [+] Clean!')
else:
    print(f'  [!] {len(found)} bad chars found')
"

echo "[+] Hex dump:"
xxd "$shellcode.bin"
