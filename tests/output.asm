section .data
	newline db 0xA
	cst_1 dd 7
	cst_2 dd 2


section .bss
	buffer resb 20


section .text
	global _start
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



_start:
	mov dword [rbp+8], 7

	mov dword [rbp+8], 2

;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	------------------------
; EOF