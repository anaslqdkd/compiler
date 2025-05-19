section .data
	list_I dq 0, 0, 0, 0, 0, 0
	list_I_len dq 6
	newline db 0xA
	minus_sign db "-"

section .bss
	buffer resb 20


section .text
	global _start
	global fibo


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


fibo:
;	---Protocole d'entree---
	push rbp
	mov rbp, rsp
	sub rsp, 48
;	------------------------


;	---Protocole de sortie---
	mov rsp, rbp
	pop rbp
	ret
;	------------------------


_start:
	; Allocating space for 2 local variables
	push rbp
	mov rbp, rsp
	sub rsp, 16

	; I = [0, 0, 0, 0, 0, 0]
	mov rax, list_I
	mov [rbp - 8], rax

;	---Stacking parameters---
;	---1-th parameter---
	mov rax, [rbp - 8]
	push rax

;	---Calling the function---
	call fibo
;	---Popping parameters---
	pop rax
;	--------------------

	; print(I)
	mov rax, [rbp - 8]
	call print_rax


;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	--------------------


; EOF