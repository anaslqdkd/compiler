section .data
	list_a_str2 db "a", 0
	list_a_str3 db "b", 0
	list_a dq 1, 2, list_a_str2, list_a_str3
	newline db 0xA

section .bss
	buffer resb 20


section .text
	global _start
	global g


;	---print_rax protocol---
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
	; Allocating space for 2 local variables
	push rbp
	mov rbp, rsp
	sub rsp, 16

	; a = [1, 2, a, b]
	mov rax, list_a
	mov [rbp-8], rax

	; b = a[3]
	mov rax, [rbp-8]
	mov rax, [rax + 3*8]
	mov [rbp-16], rax

	; print(b)
	mov rax, [rbp-16]
	; Printing a string variable
	mov rsi, rax
	call print_str


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