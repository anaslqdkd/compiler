section .data
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
	; Allocating space for 1 local variables
	push rbp
	mov rbp, rsp
	sub rsp, 8

	mov rax, 1
	push rax
	mov rax, 3
	push rax

	; Performing * operation
	pop rbx
	pop rax
	imul rax, rbx
	push rax
	mov rax, 2
	push rax

	; Performing - operation
	pop rbx
	pop rax
	sub rax, rbx
	push rax
	pop rax
	mov [rbp-8], rax

	; print(a)
	mov rax, [rbp-8]
	call print_rax


;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	--------------------


; EOF