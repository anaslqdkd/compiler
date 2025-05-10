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
;	------------------------


_start:
	push rbp
	mov rbp, rsp
	sub rsp, 24

	mov rax, 5
	push rax
	mov rax, 4
	push rax
	mov rax, 3
	push rax

	; Performing + operation
	pop rbx
	pop rax
	add rax, rbx
	push rax

	; Performing - operation
	sub rax, rbx
	push rax
	pop rax
	mov [rbp-8], rax
	mov rax, 1
	mov [rbp-16], rax
	mov rax, 1
	push rax

	; Performing + operation
	add rax, rbx
	push rax
	pop rax
	mov [rbp-24], rax

	; print(c)
	mov rax, [rbp-24]
	call print_rax

;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	------------------------


; EOF