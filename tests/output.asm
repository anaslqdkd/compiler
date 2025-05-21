section .data
	list_a dq 5, 7
	list_a_len dq 2
	newline db 0xA
	minus_sign db "-"

section .bss
	buffer resb 20


section .text
	global _start
	global f


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


f:
;	---Protocole d'entree---
	push rbp
	mov rbp, rsp
	sub rsp, 8
;	------------------------

	mov rax, [rbp + 16]
	mov rax, [rax - 8]
	mov rax, [rax + 1*8]
	push rax
	mov rax, 1
	push rax

	; Performing + operation
	pop rbx
	pop rax
	add rax, rbx
	push rax
	mov [rbp - 8], rax

;	---Protocole de sortie---
	mov rsp, rbp
	pop rbp
	ret
;	------------------------


_start:
	; Allocating space for 2 variable(s) & 1 function(s)
	push rbp
	mov rbp, rsp
	sub rsp, 24


	; a = [5, 7]
	mov rax, list_a
	mov [rbp - 8], rax

;	---Stacking parameters---
	push rbp

;	---Calling the function---
	call f
;	---Popping parameters---
;	--------------------
	mov [rbp - 16], rax

	; print: parameter 1 (x)
	mov rax, [rbp - 16]
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