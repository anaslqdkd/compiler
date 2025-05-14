section .data
	newline db 0xA

section .bss
	buffer resb 20


section .text
	global _start
	global f


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
	; Allocating space for 6 local variables
	push rbp
	mov rbp, rsp
	sub rsp, 48

	mov rax, 5
	mov [rbp-8], rax
	mov rax, 7
	mov [rbp-16], rax
	mov rax, 1
	push rax
	mov rax, 2
	push rax
	pop rax
	mov [rbp-24], rax


;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	--------------------


f:
;	---Protocole d'entree---
	push rbp
	mov rbp, rsp
	sub rsp, 1
;	------------------------

	mov rax, 10
	mov [rbp-8], rax

;	---Protocole de sortie---
	pop rbp
	ret
;	------------------------


; EOF