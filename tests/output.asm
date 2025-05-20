section .data
	mult_list_b dq 1, 2, 3, 1, 2, 3
	mult_list_b_len dq 6
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
	; Allocating space for 1 variable(s) & 0 function(s)
	push rbp
	mov rbp, rsp
	sub rsp, 8

	; List multiplication: b = [1, 2, 3] * 2
	mov rax, mult_list_b
	mov [rbp - 8], rax
	pop rax
	mov [rbp - 8], rax

	; print: parameter 1 (b)
	mov rax, [rbp - 8]
	mov rax, [rax + 4*8]
	call print_rax
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