section .data
	newline db 0xA

section .bss
	buffer resb 20


section .text
	global _start
	global g


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
	; Allocating space for 3 local variables
	push rbp
	mov rbp, rsp
	sub rsp, 24

	mov rax, 5
	mov [rbp-8], rax

;	---Entering function---
	mov rax, [8]
	push rax
	mov rax, 17
	push rax
	call g
	mov [rbp-16], rax

	; print(A)
	mov rax, [rbp-16]
	call print_rax


;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	--------------------


g:
;	---Protocole d'entree---
	push rbp
	mov rbp, rsp
;	------------------------


	; Performing + operation
	mov rax, [rbp--8]
	mov rbx, [rbp-{'type': 'INTEGER', 'depl': 8}]
	add rax, rbx
	push rax

	; Performing + operation
	pop rbx
	pop rax
	add rax, rbx
	push rax
	pop rax
	mov [rbp--16], rax

;	---Protocole de sortie---
	pop rbp
	ret
;	------------------------


; EOF