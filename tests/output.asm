section .data
	list_a_str1 db "a", 0
	list_a_str3 db "abc", 0
	list_a dq 1, list_a_str1, 234, list_a_str3
	list_a_len dq 4
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
	; Allocating space for 1 local variables
	push rbp
	mov rbp, rsp
	sub rsp, 8

	; a = [1, "a", 234, "abc"]
	mov rax, list_a
	mov [rbp - 8], rax

	; print: parameter 1 (a)
	mov rax, [rbp - 8]
	mov rax, [rax + 2*8]
	call print_rax
	mov rax, 1
	mov rdi, 1
	mov rsi, space_char
	mov rdx, 1
	syscall

	; print: parameter 2 (a)
	mov rax, [rbp - 8]
	mov rax, [rax + 1*8]
	mov rsi, rax
	call print_str
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