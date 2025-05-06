section .data
	cst_1 dd 7
	cst_2 dd 6
	cst_3 dd 4
	cst_4 dd 8
	newline db 0xA


section .bss
	buffer resb 20


section .text
	global _start
	global f


;	---Print Protocol---
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
;	------------------------


_start:
	mov 32, cst_1
	call f
	mov 64, rax
	call f

;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	------------------------


f:
;	---Protocole d'entree---
	push rbp
	mov rbp, rsp
	sub rsp, 4
;	------------------------

	mov 32, cst_2

;	---Protocole de sortie---
	pop rbp
	ret
;	------------------------


; EOF