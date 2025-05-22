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

	call if_0_2

;	---Protocole de sortie---
	mov rsp, rbp
	pop rbp
	ret
;	------------------------


if_0_2:
;	---Protocole d'entree---
	push rbp
	mov rbp, rsp
;	------------------------


	;--------if 0------
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax + 8 + 8]
	push rax
	mov rax, 0
	push rax

	; Performing == operation
	pop rbx
	pop rax
	cmp rax, rbx
	mov rax, 0
	sete al
	push rax

	pop rax
	cmp rax, 1
	jne else_0_2

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

;	---Getting return value---
	mov rax, 1
	push rax
	pop rax
	jmp end_if_1_2
else_0_2:
	; else section

	; print: parameter 1 (1)
	mov rax, 1
	call print_rax

	; print: end of line
	mov rax, 1
	mov rdi, 1
	mov rsi, newline
	mov rdx, 1
	syscall


;	---Stacking parameters---
	push rbp
;	---1-th parameter---
	mov rax, rbp
	mov rax, [rax]
	mov rax, [rax + 8 + 8]
	push rax
	mov rax, 1
	push rax

	; Performing - operation
	pop rbx
	pop rax
	sub rax, rbx
	push rax

;	---Calling the function---
	call fn

;	---Unstacking parameters---
	pop rbx
;	--------------------
	mov [rbp - 8], rax
;	---Getting return value---
	mov rax, [rbp - 8]
	push rax
	pop rax
end_if_1_2:

;	---Protocole de sortie---
	mov rsp, rbp
	pop rbp
	ret
;	------------------------


_start:
	; Allocating space for 0 variable(s) & 1 function(s)
	push rbp
	mov rbp, rsp
	sub rsp, 8


;	---Stacking parameters---
	push rbp
;	---1-th parameter---
	mov rax, 10
	push rax

;	---Calling the function---
	call fn

;	---Unstacking parameters---
	pop rbx
;	--------------------


;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	--------------------


; EOF