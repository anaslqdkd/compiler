section .data
	str_1 db "abc", 0
	newline db 0xA

section .bss
	buffer resb 20


section .text
	global _start


;	---Print Protocol---
print_rax:
	mov rcx, buffer + 20
	mov rbx, 10

.convert_loop:
	xor rdx, rdx
	div rbx
	add dl, '0'
	dec rcx
	mov [rcx], dl
	test rax, rax
	jnz .convert_loop

	; write result
	mov rax, 1
	mov rdi, 1
	mov rsi, rcx
	mov rdx, buffer + 20
	sub rdx, rcx
	syscall

	; newline
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall
	ret
;	--------------------


_start:
	; Allocating space for 0 local variables
	push rbp
	mov rbp, rsp
	sub rsp, 0

	mov rax, 1
	mov rdi, 1
	mov rsi, str_1
	mov rdx, 5
	syscall


;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	--------------------


; EOF