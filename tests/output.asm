section .data
	cst_1 dd 7
	cst_2 dd 6
	cst_3 dd 4


section .text
	global _start
	global f


_start:
	mov dword [rbp+8], 7

;	---End of program---
	mov rax, 60
	xor rdi, rdi 
	syscall
;	------------------------


f:
;	---Protocole d'entree---
	push lr
	push rbp
	mov rbp, rsp
	sub rsp, 4
;	------------------------

	mov dword [rbp+8], 6

;	---Protocole de sortie---
	pop rbp
	pop lr
	bx lr
;	------------------------


; EOF