section .data
	newline db 0xA
	minus_sign db "-"

section .bss
	buffer resb 20


section .text
	global _start
	global fn


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


fn:
;	---Protocole d'entree---
	push rbp
	mov rbp, rsp
;	------------------------

	call if_0_6
	call if_2_10

;	---Protocole de sortie---
	mov rsp, rbp
	pop rbp
	ret
;	------------------------


if_0_6:
;	---Protocole d'entree---
	push rbp
	mov rbp, rsp
;	------------------------


	;--------if 0------
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax]
	mov rax, [rax - 16]
	push rax
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax]
	mov rax, [rax - 8]
	push rax

	; Performing > operation
	pop rbx
	pop rax
	cmp rax, rbx
	mov rax, 0
	setg al
	push rax

	cmp rax, 1
	jne end_if_0_6

	;operations in if
	call if_1_7

	; print: parameter 1 (b)
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax]
	mov rax, [rax - 16]
	call print_rax

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall

end_if_0_6:

;	---Protocole de sortie---
	mov rsp, rbp
	pop rbp
	ret
;	------------------------


if_1_7:
;	---Protocole d'entree---
	push rbp
	mov rbp, rsp
;	------------------------


	;--------if 1------
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax]
	mov rax, [rax]
	mov rax, [rax - 16]
	push rax
	mov rax, 6
	push rax

	; Performing == operation
	pop rbx
	pop rax
	cmp rax, rbx
	mov rax, 0
	sete al
	push rax

	cmp rax, 1
	jne end_if_1_7

	;operations in if

	; print: parameter 1 (3)
	mov rax, 3
	call print_rax

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall

end_if_1_7:

;	---Protocole de sortie---
	mov rsp, rbp
	pop rbp
	ret
;	------------------------


if_2_10:
;	---Protocole d'entree---
	push rbp
	mov rbp, rsp
;	------------------------


	;--------if 2------
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax]
	mov rax, [rax - 8]
	push rax
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax]
	mov rax, [rax - 32]
	push rax

	; Performing < operation
	pop rbx
	pop rax
	cmp rax, rbx
	mov rax, 0
	setl al
	push rax

	cmp rax, 1
	jne else_0_10

	;operations in if

	; print: parameter 1 (10)
	mov rax, 10
	call print_rax

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall

	jmp end_if_3_10
else_0_10:
	; else section
	call if_3_13

	; print: parameter 1 (r)
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax]
	mov rax, [rax - 32]
	call print_rax

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall

end_if_3_10:

;	---Protocole de sortie---
	mov rsp, rbp
	pop rbp
	ret
;	------------------------


if_3_13:
;	---Protocole d'entree---
	push rbp
	mov rbp, rsp
;	------------------------


	;--------if 3------
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax]
	mov rax, [rax]
	mov rax, [rax - 16]
	push rax
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax]
	mov rax, [rax]
	mov rax, [rax - 8]
	push rax

	; Performing > operation
	pop rbx
	pop rax
	cmp rax, rbx
	mov rax, 0
	setg al
	push rax

	cmp rax, 1
	jne end_if_3_13

	;operations in if

	; print: parameter 1 (a)
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax]
	mov rax, [rax]
	mov rax, [rax - 8]
	call print_rax

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall

end_if_3_13:

;	---Protocole de sortie---
	mov rsp, rbp
	pop rbp
	ret
;	------------------------


_start:
	; Allocating space for 4 variable(s) & 1 function(s)
	push rbp
	mov rbp, rsp
	sub rsp, 40

	mov rax, 5
	mov [rbp - 8], rax
	mov rax, 6
	mov [rbp - 16], rax
	mov rax, 2
	mov [rbp - 24], rax
	mov rax, 1
	mov [rbp - 32], rax

;	---Stacking parameters---
	push rbp

;	---Calling the function---
	call fn
;	--------------------


;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	--------------------


; EOF