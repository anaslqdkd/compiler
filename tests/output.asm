section .data
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
	; Allocating space for 3 variable(s) & 0 function(s)
	push rbp
	mov rbp, rsp
	sub rsp, 24

	mov rax, 5
	mov [rbp - 8], rax
	mov rax, 6
	mov [rbp - 16], rax

	;--------if 0------

	; Performing > operation
	mov rax, [rbp - 16]
	mov rbx, [rbp - 8]
	cmp rax, rbx
	mov rax, 0
	setg al
	push rax

	cmp rax, 1
	jne end_if_0_3

	;operations in if

	; print: parameter 1 (b)
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax - 16]
	call print_rax

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall

end_if_0_3:

	; print: parameter 1 (a)
	mov rax, [rbp - 8]
	call print_rax

	; print: end of line
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