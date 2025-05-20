section .data
	space_char db " ", 0
	newline db 0xA
	minus_sign db "-"

section .bss
	buffer resb 20


section .text
	global _start


;	---print_rax protocol---
print_rax:
	test rax, rax
	jns .positive
	push rax
	mov rax, 1
	mov rdi, 1
	mov rsi, minus_sign
	mov rdx, 1
	syscall
	pop rax
	neg rax
.positive:
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
	ret
;	--------------------

; ---print_str protocol---
print_str:
	xor rcx, rcx

.find_len_str:
	mov al, [rsi + rcx]
	test al, al
	jz .len_found_str
	inc rcx
	jmp .find_len_str

.len_found_str:
	mov rdx, rcx
	mov rax, 1
	mov rdi, 1
	syscall
	ret
;	--------------------


_start:
	; Allocating space for 5 local variables
	push rbp
	mov rbp, rsp
	sub rsp, 40

	mov rax, 1
	mov [rbp - 8], rax
	mov rax, 0
	mov [rbp - 16], rax
	mov rax, 0
	mov [rbp - 24], rax
	mov rax, 1
	mov [rbp - 32], rax
	mov rax, 2
	mov [rbp - 40], rax

	; print: parameter 1 (a)
	mov rax, [rbp - 8]
	call print_rax
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall

	; print() - empty print statement
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall

	; print: parameter 1 (b)
	mov rax, [rbp - 16]
	call print_rax
	mov rax, 1
	mov rdi, 1
	mov rsi, space_char
	mov rdx, 1
	syscall

	; print: parameter 2 (c)
	mov rax, [rbp - 24]
	call print_rax
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall
	mov rax, 2
	push rax
	mov rax, 5
	push rax

	; Performing + operation
	pop rbx
	pop rax
	add rax, rbx
	push rax
	pop rax
	call print_rax

	; print: parameter 1 (param_1)
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall
	mov rax, [rbp - 32]
	push rax
	mov rax, [rbp - 40]
	push rax

	; Performing + operation
	mov rax, [rbp - 32]
	mov rbx, [rbp - 40]
	add rax, rbx
	push rax
	pop rax
	call print_rax

	; print: parameter 1 (param_1)
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall


;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	--------------------


; EOF