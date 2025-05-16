section .data
	newline db 0xA

section .bss
	buffer resb 20


section .text
	global _start
	global fn


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


fn:
;	---Protocole d'entree---
	push rbp
	mov rbp, rsp
;	------------------------

	; if 0
	mov rax, [rbp--8]
	mov rbx, 0

	cmp rax, rbx
	jge else_0_2
	mov rax, 5
	mov [rbp-8], rax

	; print(a)
	mov rax, [rbp-8]
	call print_rax
	jmp end_if_1_2
else_0_2:
	; else section
	; if 1
	mov rax, 2
	mov rbx, 1

	cmp rax, rbx
	jle end_if_1_6
	mov rax, 3
	mov [rbp-8], rax

	; print(b)
	mov rax, [rbp-8]
	call print_rax
end_if_1_6:
	; if 2
	mov rax, 1
	mov rbx, 2

	cmp rax, rbx
	jle else_1_9
	mov rax, 0
	mov [rbp-8], rax

	; print(f)
	mov rax, [rbp-8]
	call print_rax
	jmp end_if_3_9
else_1_9:
	; else section
	mov rax, 1
	mov [rbp-8], rax

	; print(r)
	mov rax, [rbp-8]
	call print_rax
end_if_3_9:
	mov rax, 6
	mov [rbp-8], rax

	; print(a)
	mov rax, [rbp-8]
	call print_rax
end_if_1_2:

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

	; if 3
	mov rax, 4
	mov rbx, 5

	cmp rax, rbx
	jge end_if_3_17
	mov rax, 13
	mov [rbp-8], rax

	; print(f)
	mov rax, [rbp-8]
	call print_rax
end_if_3_17:

;	---Stacking parameters---
;	---1-th parameter---
	mov rax, 2
	push rax
	mov rax, 1
	push rax

	; Performing + operation
	pop rbx
	pop rax
	add rax, rbx
	push rax

;	---Calling the function---
	call fn
;	---Popping parameters---
	pop rax
;	--------------------


;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	--------------------


; EOF